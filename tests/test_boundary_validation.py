"""Regression coverage for malformed proposals at the model trust boundary."""
import unittest

from ai_security_lab.engine import HardenedEngine
from ai_security_lab.models import ModelDecision, UserContext
from ai_security_lab.providers import DecisionJSONMixin
from ai_security_lab.tools import ToolPolicy


class SuppliedDecision:
    def __init__(self, decision):
        self.decision = decision

    def decide(self, prompt, context):
        return self.decision


class BoundaryValidationTests(unittest.TestCase):
    def test_malformed_proposals_are_blocked_without_tools_or_crashes(self):
        malformed = [
            None,
            ModelDecision({"not": "text"}),
            ModelDecision("ok", ["get_balance"], {}),
            ModelDecision("ok", "get_balance", "not-an-object"),
        ]
        for decision in malformed:
            with self.subTest(decision=decision):
                engine = HardenedEngine(SuppliedDecision(decision))
                before = repr(engine.runtime.customers)
                result = engine.process("my balance", UserContext("user-100", "ACC-100"))
                self.assertEqual(result.executed_tools, [])
                self.assertEqual(result.state_changes, [])
                self.assertEqual(repr(engine.runtime.customers), before)
                self.assertIn("model_decision_invalid", result.security_events)

    def test_unexpected_read_tool_arguments_are_denied(self):
        for args in [None, [], "bad", {}, {"account_id": 100},
                     {"account_id": "ACC-100", "admin": True}]:
            with self.subTest(args=args):
                allowed, _ = ToolPolicy.authorize("get_balance", args, UserContext("user-100", "ACC-100"))
                self.assertFalse(allowed)

    def test_policy_rejects_cross_account_reads(self):
        for name in ["get_balance", "get_transactions"]:
            decision = ModelDecision("ok", name, {"account_id": "ACC-200"})
            result = HardenedEngine(SuppliedDecision(decision)).process(
                "show another account", UserContext("user-100", "ACC-100"))
            self.assertEqual(result.executed_tools, [])
            self.assertNotIn("Hotel", result.output)
            self.assertNotIn("9460", result.output)
            self.assertTrue(any("cross-account" in event for event in result.security_events))

    def test_provider_rejects_malformed_schema_instead_of_coercing_it(self):
        cases = [
            {},
            {"answer": 42, "tool_name": None, "tool_args": {}},
            {"answer": "ok", "tool_name": [], "tool_args": {}},
            {"answer": "ok", "tool_name": None, "tool_args": []},
            {"answer": "ok", "tool_name": None, "tool_args": {}, "admin": True},
        ]
        for payload in cases:
            with self.subTest(payload=payload):
                with self.assertRaises(ValueError):
                    DecisionJSONMixin._decision(payload)

    def test_valid_schema_and_own_account_reads_remain_usable(self):
        for name, expected in [("get_balance", "1280.50"), ("get_transactions", "Grocer")]:
            decision = DecisionJSONMixin._decision({
                "answer": "ok", "tool_name": name, "tool_args": {"account_id": "ACC-100"}})
            result = HardenedEngine(SuppliedDecision(decision)).process(
                "my account", UserContext("user-100", "ACC-100"))
            self.assertEqual(result.executed_tools, [name])
            self.assertIn(expected, result.output)


if __name__ == "__main__":
    unittest.main()
