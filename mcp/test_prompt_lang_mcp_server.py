import sys
import os
import unittest
from pathlib import Path
import yaml

# Add mcp dir to path so we can import the module
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "mcp"))

# We also need to add forge/prompt-lang for the module to work
sys.path.insert(0, str(repo_root / "forge" / "prompt-lang"))

# Import the module
# Note: This will execute the module level code, which is fine for now
import prompt_lang_mcp_server as server

class TestPromptLangMCPServer(unittest.TestCase):

    def test_detect_domain(self):
        self.assertEqual(server.detect_domain("I need a python script to sort files"), "technical")
        self.assertEqual(server.detect_domain("Please summarize this document"), "summarization")
        self.assertEqual(server.detect_domain("Search for papers about AI"), "rag")
        self.assertEqual(server.detect_domain("Write a poem"), "general")

    def test_merge_templates(self):
        base = {"a": 1, "b": {"c": 2}}
        overlay = {"b": {"d": 3}, "e": 4}
        merged = server.merge_templates(base, overlay)
        self.assertEqual(merged, {"a": 1, "b": {"c": 2, "d": 3}, "e": 4})

    def test_template_to_prompt(self):
        # Mock template data
        data = {
            "required": {
                "role": "Expert {{requirements}}",
                "goal": "Do {{requirements}}",
                "constraints": ["Must be {{requirements}}"],
                "format": "JSON"
            }
        }

        reqs = "fast"
        prompt = server.template_to_prompt(data, reqs, "test_skill")

        self.assertEqual(prompt.name, "test_skill")
        self.assertEqual(prompt.role, "Expert fast")
        self.assertIn("Do fast", prompt.goal)
        self.assertEqual(prompt.constraints, ["Must be fast"])

    def test_generate_source_code(self):
        from prompt_lang import Prompt
        p = Prompt(
            name="test",
            role="Role",
            goal="Goal",
            constraints=["C1"],
            format="Text"
        )

        code = server.generate_source_code(p)
        self.assertIn("#prompt test", code)
        self.assertIn("@role:\n  Role", code)
        self.assertIn("@goal:\n  Goal", code)
        self.assertIn("@constraints:\n  - C1", code)
        # Format might be wrapped in backticks if not present
        self.assertIn("@format:", code)
        self.assertIn("Text", code)

    def test_template_to_prompt_with_activation(self):
        data = {
            "optional": {
                "activation": {
                    "mode": "glob",
                    "pattern": "*.py",
                    "priority": 5
                }
            }
        }
        prompt = server.template_to_prompt(data, "reqs", "test_act")
        self.assertIsNotNone(prompt.activation)
        self.assertEqual(prompt.activation.mode, "glob")
        self.assertEqual(prompt.activation.priority, 5)

if __name__ == "__main__":
    unittest.main()
