import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins" / "awesome-kit" / "skills" / "orchestrate" / "SKILL.md"
REFERENCE = SKILL.parent / "references" / "delegation.md"


class OrchestrateSkillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SKILL.read_text(encoding="utf-8")

    def test_skill_is_packaged(self):
        self.assertTrue(SKILL.is_file())
        self.assertTrue(REFERENCE.is_file())
        self.assertIn("name: orchestrate", self.text)

    def test_native_codex_agents_are_preferred_but_not_forced_through_cli(self):
        self.assertIn("Prefer native Codex background agents", self.text)
        self.assertIn("Do not route ordinary Codex fan-out through the", self.text)

    def test_all_canonical_backend_types_remain_available(self):
        for term in ("HTTP endpoints", "Claude", "Codex", "OpenCode"):
            self.assertIn(term, self.text)
        self.assertIn("llm-scripting-kit endpoints", self.text)

    def test_existing_configuration_and_cross_platform_runtime_are_documented(self):
        self.assertIn("existing Claude configuration and credentials", self.text)
        self.assertIn("macOS/Linux", self.text)
        self.assertIn("Windows", self.text)

    def test_adapter_does_not_require_mcp_or_bootstrap_lifecycle(self):
        lowered = self.text.lower()
        self.assertNotIn("mcp server", lowered)
        self.assertNotIn("run bootstrap", lowered)

    def test_reference_link_resolves(self):
        self.assertIn("references/delegation.md", self.text)


if __name__ == "__main__":
    unittest.main()
