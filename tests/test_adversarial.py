import unittest
from pathlib import Path

from ai_security_lab.evaluation import case_is_secure, load_cases
from ai_security_lab.engine import HardenedEngine, VulnerableEngine
from ai_security_lab.models import UserContext

CASES = load_cases(Path(__file__).with_name("attacks.json"))

class AdversarialSecurityTests(unittest.TestCase):
    def test_hardened_control_plane_passes_all_security_oracles(self):
        for case in CASES:
            with self.subTest(case=case["id"]):
                ctx = UserContext(case.get("user_id", "user-100"), case.get("account_id", "ACC-100"))
                result = HardenedEngine().process(case["prompt"], ctx)
                secure, failures = case_is_secure(result, case)
                self.assertTrue(secure, failures)

    def test_vulnerable_baseline_demonstrates_real_control_failures(self):
        insecure = 0
        for case in CASES:
            ctx = UserContext(case.get("user_id", "user-100"), case.get("account_id", "ACC-100"))
            result = VulnerableEngine().process(case["prompt"], ctx)
            secure, _ = case_is_secure(result, case)
            insecure += int(not secure)
        self.assertGreaterEqual(insecure, 18)

if __name__ == "__main__":
    unittest.main()
