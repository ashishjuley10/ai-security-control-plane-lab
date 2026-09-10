import os
import unittest
from unittest.mock import patch

from ai_security_lab.providers import DecisionJSONMixin, OpenAIResponsesProvider


class ProviderParsingTests(unittest.TestCase):
    def test_parse_plain_json(self):
        parsed = DecisionJSONMixin._parse_json(
            '{"answer":"ok","tool_name":null,"tool_args":{}}'
        )
        self.assertEqual(parsed["answer"], "ok")
        self.assertIsNone(parsed["tool_name"])
        self.assertEqual(parsed["tool_args"], {})

    def test_parse_fenced_json(self):
        parsed = DecisionJSONMixin._parse_json(
            '```json\n{"answer":"ok","tool_name":"get_balance","tool_args":{"account_id":"ACC-100"}}\n```'
        )
        self.assertEqual(parsed["tool_name"], "get_balance")
        self.assertEqual(parsed["tool_args"]["account_id"], "ACC-100")

    def test_extract_responses_output_text(self):
        payload = {
            "output": [
                {
                    "type": "message",
                    "content": [
                        {
                            "type": "output_text",
                            "text": '{"answer":"ok","tool_name":null,"tool_args":{}}',
                        }
                    ],
                }
            ]
        }
        text = OpenAIResponsesProvider._extract_output_text(payload)
        self.assertIn('"answer":"ok"', text)

    def test_missing_openai_key_fails_closed(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError):
                OpenAIResponsesProvider()


if __name__ == "__main__":
    unittest.main()
