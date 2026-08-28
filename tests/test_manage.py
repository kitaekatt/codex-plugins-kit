import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("codex_plugins_manage", ROOT / "scripts" / "manage.py")
manage = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(manage)


class ManageTests(unittest.TestCase):
    def test_default_package_set_is_deduplicated(self):
        self.assertEqual(
            manage.selected_packages([]),
            ["bootstrap", "llm-scripting-kit", "skills-kit"],
        )

    def test_llm_plugin_gets_only_its_dependencies(self):
        self.assertEqual(
            manage.selected_packages(["llm-scripting-kit"]),
            ["bootstrap", "llm-scripting-kit"],
        )

    def test_explicit_source_must_be_a_complete_plugins_kit_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(manage.SetupError):
                manage.find_local_source(directory)

    def test_doctor_checks_only_recorded_packages(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = Path(directory)
            (runtime / "runtime.json").write_text(
                json.dumps({"packages": ["llm-scripting-kit"]}), encoding="utf-8"
            )
            with (
                mock.patch.object(manage, "RUNTIME_ROOT", runtime),
                mock.patch.object(manage, "inspect_import", return_value=(True, "source")) as inspect,
                mock.patch.object(manage, "python_in_venv", return_value=runtime / "python"),
            ):
                manage.doctor(mock.Mock())
            inspect.assert_called_once_with("llm_scripting_kit")

    def test_setup_parser_accepts_python_only_mode(self):
        args = manage.parser().parse_args(
            ["setup", "--plugin", "llm-scripting-kit", "--skip-codex-install"]
        )
        self.assertTrue(args.skip_codex_install)


if __name__ == "__main__":
    unittest.main()
