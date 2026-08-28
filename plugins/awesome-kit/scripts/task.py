#!/usr/bin/env python3
"""Codex launcher for the canonical plugins-kit task system."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys


RUNTIME_ROOT = Path.home() / ".codex" / ".local-data" / "codex-plugins-kit"
RUNTIME_RECORD = RUNTIME_ROOT / "runtime.json"
UPSTREAM_TASK = Path("plugins/awesome-kit/skills/task/scripts/task.py")


class AdapterError(RuntimeError):
    pass


def upstream_task() -> Path:
    try:
        state = json.loads(RUNTIME_RECORD.read_text(encoding="utf-8"))
        source = Path(state["pluginsKit"]).expanduser()
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        raise AdapterError(
            f"shared runtime record is missing or invalid ({RUNTIME_RECORD}); "
            "run codex-plugins-kit's setup script"
        ) from exc
    script = source / UPSTREAM_TASK
    if not script.is_file():
        raise AdapterError(
            f"canonical task CLI is missing at {script}; update the editable "
            "plugins-kit checkout or rerun setup"
        )
    return script


def codex_work_output(text: str) -> str:
    """Translate Claude tool-call notation without changing skill identities."""
    rendered: list[str] = []
    prefix = 'Skill(skill: "'
    for line in text.splitlines():
        if line == "== task init -- invoke each of these now, one Skill call each ==":
            rendered.append("== task init -- use each of these Codex skills now ==")
        elif line.startswith(prefix) and line.endswith('")'):
            rendered.append(f"${line[len(prefix):-2]}")
        elif line.startswith("== then: dispatch the work per orchestrate"):
            rendered.append(
                "== then: delegate the work per orchestrate using Codex "
                "background agents; do not implement inline in the main context =="
            )
        else:
            rendered.append(line)
    return "\n".join(rendered) + ("\n" if text.endswith("\n") else "")


def run(argv: list[str]) -> int:
    script = upstream_task()
    env = os.environ.copy()
    # The upstream script's Claude bootstrap guard should not redirect this
    # process into a Claude plugin venv. Dependencies already live in the
    # shared Codex runtime that invoked this adapter.
    env["CLAUDE_BOOTSTRAP_DATA_ROOT"] = str(RUNTIME_ROOT / "bootstrap-disabled")
    command = [sys.executable, str(script), *argv]
    if argv and argv[0] == "work":
        result = subprocess.run(command, env=env, text=True, capture_output=True)
        sys.stdout.write(codex_work_output(result.stdout))
        sys.stderr.write(result.stderr)
        return result.returncode
    return subprocess.run(command, env=env).returncode


def main() -> int:
    try:
        return run(sys.argv[1:])
    except AdapterError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
