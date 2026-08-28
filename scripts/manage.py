#!/usr/bin/env python3
"""Provision and inspect the shared codex-plugins-kit Python runtime."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = Path.home() / ".codex" / ".local-data" / "codex-plugins-kit"
VENV = RUNTIME_ROOT / ".venv"
MANAGED_SOURCE = RUNTIME_ROOT / "source" / "plugins-kit"
LOCK_FILE = REPO_ROOT / "upstream.lock.json"

PACKAGE_PATHS = {
    "bootstrap": "plugins/bootstrap",
    "llm-scripting-kit": "plugins/llm-scripting-kit",
    "skills-kit": "plugins/skills-kit",
}
PLUGIN_PACKAGES = {
    "llm-scripting-kit": ("bootstrap", "llm-scripting-kit"),
    "awesome-kit": ("bootstrap", "llm-scripting-kit", "skills-kit"),
}
IMPORTS = {
    "bootstrap": "bootstrap_lib",
    "llm-scripting-kit": "llm_scripting_kit",
    "skills-kit": "skills_kit_lib",
}


class SetupError(RuntimeError):
    pass


def run(command: list[str], *, cwd: Path | None = None) -> None:
    print("+", " ".join(command))
    try:
        subprocess.run(command, cwd=cwd, check=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SetupError(str(exc)) from exc


def executable_command(name: str) -> list[str]:
    """Resolve a command, including Windows batch launchers."""
    resolved = shutil.which(name)
    if not resolved:
        raise SetupError(f"Required command is not on PATH: {name}")
    if os.name == "nt" and resolved.lower().endswith((".cmd", ".bat")):
        return ["cmd.exe", "/d", "/s", "/c", resolved]
    return [resolved]


def python_in_venv() -> Path:
    if os.name == "nt":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


def load_lock() -> dict[str, str]:
    try:
        data = json.loads(LOCK_FILE.read_text(encoding="utf-8"))
        return {"repository": data["repository"], "revision": data["revision"]}
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        raise SetupError(f"Invalid upstream lock file: {LOCK_FILE}: {exc}") from exc


def validate_source(source: Path) -> Path:
    source = source.expanduser().resolve()
    missing = [path for path in PACKAGE_PATHS.values() if not (source / path / "pyproject.toml").is_file()]
    if missing:
        raise SetupError(f"Not a plugins-kit checkout ({source}); missing: {', '.join(missing)}")
    return source


def find_local_source(explicit: str | None) -> Path | None:
    if explicit:
        return validate_source(Path(explicit))
    sibling = REPO_ROOT.parent / "plugins-kit"
    if sibling.is_dir():
        return validate_source(sibling)
    return None


def provision_managed_source() -> Path:
    lock = load_lock()
    if not MANAGED_SOURCE.exists():
        MANAGED_SOURCE.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", lock["repository"], str(MANAGED_SOURCE)])
    elif not (MANAGED_SOURCE / ".git").is_dir():
        raise SetupError(f"Managed source exists but is not a Git checkout: {MANAGED_SOURCE}")
    run(["git", "fetch", "origin", lock["revision"]], cwd=MANAGED_SOURCE)
    run(["git", "checkout", "--detach", lock["revision"]], cwd=MANAGED_SOURCE)
    return validate_source(MANAGED_SOURCE)


def selected_packages(plugins: list[str]) -> list[str]:
    selected = plugins or list(PLUGIN_PACKAGES)
    packages: list[str] = []
    for plugin in selected:
        for package in PLUGIN_PACKAGES[plugin]:
            if package not in packages:
                packages.append(package)
    return packages


def setup(args: argparse.Namespace) -> None:
    source = find_local_source(args.plugins_kit) or provision_managed_source()
    uv = shutil.which("uv")
    if not uv:
        raise SetupError("uv is required. Install it from https://docs.astral.sh/uv/ and rerun setup.")

    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    if not python_in_venv().is_file():
        run([uv, "venv", "--python", "3.12", str(VENV)])

    packages = selected_packages(args.plugin)
    editable_paths = [
        str(source / PACKAGE_PATHS[package]) + ("[sdk]" if package == "llm-scripting-kit" else "")
        for package in packages
    ]
    command = [uv, "pip", "install", "--python", str(python_in_venv())]
    for path in editable_paths:
        command.extend(["--editable", path])
    run(command)

    state = {
        "plugins": args.plugin or list(PLUGIN_PACKAGES),
        "packages": packages,
        "pluginsKit": str(source),
        "editable": True,
    }
    (RUNTIME_ROOT / "runtime.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    if not args.skip_codex_install:
        codex = executable_command("codex")
        run(codex + ["plugin", "marketplace", "add", str(REPO_ROOT), "--json"])
        for plugin in args.plugin or list(PLUGIN_PACKAGES):
            skill_files = tuple((REPO_ROOT / "plugins" / plugin / "skills").glob("*/SKILL.md"))
            if not skill_files:
                print(f"Skipping Codex install for {plugin}: no completed skills are packaged yet.")
                continue
            run(codex + ["plugin", "add", f"{plugin}@codex-plugins-kit", "--json"])

    print(f"Runtime ready: {VENV}")
    print(f"Editable plugins-kit source: {source}")


def inspect_import(module: str) -> tuple[bool, str]:
    python = python_in_venv()
    if not python.is_file():
        return False, "shared virtual environment is missing"
    result = subprocess.run(
        [str(python), "-c", f"import importlib.util; print(importlib.util.find_spec({module!r}).origin)"],
        text=True,
        capture_output=True,
    )
    if result.returncode:
        return False, result.stderr.strip() or "not importable"
    return True, result.stdout.strip()


def doctor(_: argparse.Namespace) -> None:
    failures = 0
    print(f"runtime: {RUNTIME_ROOT}")
    print(f"python:  {python_in_venv()}")
    state_file = RUNTIME_ROOT / "runtime.json"
    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
        packages = state["packages"]
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        raise SetupError(f"Runtime record is missing or invalid ({state_file}): {exc}") from exc
    for package in packages:
        module = IMPORTS[package]
        healthy, detail = inspect_import(module)
        print(f"{'ok' if healthy else 'FAIL'}: {package}: {detail}")
        failures += not healthy
    if failures:
        raise SetupError(f"Doctor found {failures} problem(s); run setup to repair the runtime.")


def uninstall(_: argparse.Namespace) -> None:
    removed = False
    for path in (VENV, MANAGED_SOURCE, RUNTIME_ROOT / "runtime.json"):
        if path.is_dir():
            shutil.rmtree(path)
            removed = True
            print(f"Removed {path}")
        elif path.exists():
            path.unlink()
            removed = True
            print(f"Removed {path}")
    if not removed:
        print("No managed runtime files were installed.")
    print(f"Preserved user configuration and credentials under {RUNTIME_ROOT}.")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    setup_parser = commands.add_parser("setup", help="create or update the shared editable runtime")
    setup_parser.add_argument("--plugins-kit", help="path to a plugins-kit checkout")
    setup_parser.add_argument(
        "--plugin",
        action="append",
        choices=sorted(PLUGIN_PACKAGES),
        default=[],
        help="install dependencies for one plugin (repeatable; default: all)",
    )
    setup_parser.add_argument(
        "--skip-codex-install",
        action="store_true",
        help="provision Python only; do not register the marketplace or install plugins",
    )
    setup_parser.set_defaults(handler=setup)
    doctor_parser = commands.add_parser("doctor", help="check the shared runtime")
    doctor_parser.set_defaults(handler=doctor)
    uninstall_parser = commands.add_parser("uninstall", help="remove runtime files but preserve user data")
    uninstall_parser.set_defaults(handler=uninstall)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        args.handler(args)
    except SetupError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
