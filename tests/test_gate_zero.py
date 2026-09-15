import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("gate", ROOT / "scripts/validate_gate_zero.py")
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)

class GateZeroTests(unittest.TestCase):
    def test_gate_zero_contract(self):
        self.assertEqual(gate.validate(), [])

    def test_no_real_env_file(self):
        self.assertFalse((ROOT / ".env").exists())

    def test_human_authority_is_explicit(self):
        governance = (ROOT / "GOVERNANCE.md").read_text(encoding="utf-8")
        self.assertIn("autorité humaine finale", governance)

    def test_command_center_tracks_priority_projects(self):
        registry = (ROOT / "governance/project-registry.yaml").read_text(encoding="utf-8")
        for project in ("eCDF", "AGRICHAIN DAO", "Open Technologies Portfolio"):
            self.assertIn(project, registry)

if __name__ == "__main__":
    unittest.main()
