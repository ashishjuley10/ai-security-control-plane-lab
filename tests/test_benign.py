import json
import unittest
from pathlib import Path

from ai_security_lab.engine import HardenedEngine
from ai_security_lab.models import UserContext

CASES = json.loads(Path(__file__).with_name("benign.json").read_text(encoding="utf-8"))


class BenignTaskTests(unittest.TestCase):
    def test_hardened_engine_retains_legitimate_functionality(self):
        for case in CASES:
            with self.subTest(case=case["id"]):
                result = HardenedEngine().process(
                    case["prompt"],
                    UserContext("user-100", "ACC-100"),
                )

                required_tool = case.get("required_tool")
                if required_tool:
                    self.assertIn(required_tool, result.executed_tools)

                must_contain = case.get("must_contain")
                if must_contain:
                    self.assertIn(must_contain.lower(), result.output.lower())


if __name__ == "__main__":
    unittest.main()
