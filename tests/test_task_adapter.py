import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "plugins" / "awesome-kit" / "scripts" / "task.py"
SPEC = importlib.util.spec_from_file_location("codex_task_adapter", MODULE_PATH)
adapter = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(adapter)


class TaskAdapterTests(unittest.TestCase):
    def test_runtime_environment_does_not_fabricate_redirect(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(
            adapter, "upstream_task", return_value=Path("canonical.py")
        ), mock.patch.object(adapter.subprocess, "run") as run:
            run.return_value.returncode = 0
            self.assertEqual(adapter.run(["validate"]), 0)
        env = run.call_args.kwargs["env"]
        self.assertNotIn("CLAUDE_BOOTSTRAP_DATA_ROOT", env)
        self.assertEqual(env["_BOOTSTRAP_GUARD_VENV_REEXEC"], "1")

    def test_runtime_environment_preserves_real_redirect(self) -> None:
        with mock.patch.dict(os.environ, {"CLAUDE_BOOTSTRAP_DATA_ROOT": "real-dev"}, clear=True), mock.patch.object(
            adapter, "upstream_task", return_value=Path("canonical.py")
        ), mock.patch.object(adapter.subprocess, "run") as run:
            run.return_value.returncode = 0
            adapter.run(["validate"])
        self.assertEqual(run.call_args.kwargs["env"]["CLAUDE_BOOTSTRAP_DATA_ROOT"], "real-dev")
        self.assertNotIn("_BOOTSTRAP_GUARD_VENV_REEXEC", run.call_args.kwargs["env"])

    def test_valid_redirect_selects_its_interpreter(self) -> None:
        upstream = ROOT.parent / "plugins-kit" / "plugins" / "bootstrap" / "bootstrap_lib"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            interpreter = root / "data-dev" / "plugins-kit" / "awesome-kit" / ".venv" / "bin" / "python"
            interpreter.parent.mkdir(parents=True)
            interpreter.write_text("", encoding="utf-8")
            script = root / "consumer.py"
            script.write_text(
                "import sys\n"
                f"sys.path.insert(0, {str(upstream)!r})\n"
                "import bootstrap_guard as guard\n"
                "guard._is_windows = lambda: False\n"
                "def selected(path, args):\n"
                f"    assert path == {str(interpreter)!r}\n"
                "    print(path)\n"
                "    raise SystemExit(0)\n"
                "guard.os.execv = selected\n"
                "guard.reexec_under_plugin_venv('awesome-kit')\n"
                "raise SystemExit(9)\n", encoding="utf-8"
            )
            with mock.patch.dict(os.environ, {"CLAUDE_BOOTSTRAP_DATA_ROOT": str(root / "data-dev")}, clear=True), mock.patch.object(
                adapter, "upstream_task", return_value=script
            ):
                self.assertEqual(adapter.run(["work"]), 0)

    def test_real_redirect_preserves_inherited_guard(self) -> None:
        original = {"CLAUDE_BOOTSTRAP_DATA_ROOT": "real-dev", "_BOOTSTRAP_GUARD_VENV_REEXEC": "inherited"}
        with mock.patch.dict(os.environ, original, clear=True), mock.patch.object(
            adapter, "upstream_task", return_value=Path("canonical.py")
        ), mock.patch.object(adapter.subprocess, "run") as run:
            run.return_value.returncode = 0
            adapter.run(["validate"])
        self.assertEqual(run.call_args.kwargs["env"], original)

    def test_real_missing_redirect_refuses_before_production_import(self) -> None:
        upstream = ROOT.parent / "plugins-kit" / "plugins" / "bootstrap" / "bootstrap_lib"
        self.assertTrue((upstream / "bootstrap_guard.py").is_file())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            marker = root / "production-imported"
            package = root / "bootstrap_lib"
            package.mkdir()
            (package / "__init__.py").write_text(
                f"from pathlib import Path\nPath({str(marker)!r}).touch()\n", encoding="utf-8"
            )
            script = root / "consumer.py"
            script.write_text(
                "import sys\n"
                f"sys.path.insert(0, {str(upstream)!r})\n"
                "from bootstrap_guard import reexec_under_plugin_venv\n"
                "reexec_under_plugin_venv('awesome-kit')\n"
                f"sys.path.insert(0, {str(root)!r})\n"
                "import bootstrap_lib\n", encoding="utf-8"
            )
            redirected = root / "real-dev"
            with mock.patch.dict(os.environ, {"CLAUDE_BOOTSTRAP_DATA_ROOT": str(redirected)}), mock.patch.object(
                adapter, "upstream_task", return_value=script
            ), mock.patch.object(adapter.subprocess, "run", wraps=subprocess.run) as run:
                self.assertEqual(adapter.run(["work"]), 2)
            self.assertEqual(run.call_args.kwargs["env"]["CLAUDE_BOOTSTRAP_DATA_ROOT"], str(redirected))
            self.assertFalse(marker.exists())

    def test_resolves_canonical_cli_from_runtime_record(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / adapter.UPSTREAM_TASK
            script.parent.mkdir(parents=True)
            script.write_text("# canonical\n", encoding="utf-8")
            record = root / "runtime.json"
            record.write_text(json.dumps({"pluginsKit": str(root)}), encoding="utf-8")
            with mock.patch.object(adapter, "RUNTIME_RECORD", record):
                self.assertEqual(adapter.upstream_task(), script)

    def test_missing_runtime_has_actionable_error(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "runtime.json"
            with mock.patch.object(adapter, "RUNTIME_RECORD", missing):
                with self.assertRaisesRegex(adapter.AdapterError, "run codex-plugins-kit's setup"):
                    adapter.upstream_task()

    def test_work_output_uses_codex_notation_and_preserves_identity(self):
        original = (
            "== task init -- invoke each of these now, one Skill call each ==\n"
            'Skill(skill: "awesome-kit:orchestrate")\n'
            'Skill(skill: "home-domain")\n'
            "agent_hint: general-purpose\n"
            "== then: dispatch the work per orchestrate -- do not implement inline in the main context ==\n"
        )
        rendered = adapter.codex_work_output(original)
        self.assertIn("$awesome-kit:orchestrate", rendered)
        self.assertIn("$home-domain", rendered)
        self.assertNotIn("Skill(skill:", rendered)
        self.assertIn("Codex background agents", rendered)
        self.assertIn("agent_hint: general-purpose", rendered)

    def test_skill_is_thin_and_names_all_verbs(self):
        text = (ROOT / "plugins" / "awesome-kit" / "skills" / "task" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        for verb in (
            "init", "list", "show", "status", "validate", "work", "update",
            "items", "close", "reopen", "archive", "delete", "move",
        ):
            self.assertIn(f"`{verb}`", text)
        self.assertIn("CLAUDE.md", text)
        self.assertIn("runtime.json", text)
        self.assertNotIn("task_system", text)


if __name__ == "__main__":
    unittest.main()
