import importlib.util
import json
from pathlib import Path
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
