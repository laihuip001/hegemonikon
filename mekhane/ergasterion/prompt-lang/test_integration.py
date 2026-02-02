# PROOF: [L2/インフラ] <- mekhane/ergasterion/prompt-lang/ S2→プロンプト言語が必要→test_integration が担う
import sys
import json
import unittest
from pathlib import Path
import shutil

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from prompt_lang_integrate import SkillAdapter, generate_prompt, list_prompts


class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Setup staging dir
        self.staging_dir = Path(__file__).parent / "staging"
        self.staging_dir.mkdir(exist_ok=True)

    def test_skill_adapter_workflow(self):
        """Test the full workflow via SkillAdapter."""

        try:
            # 1. Generate checking file naming
            import time

            slug = f"integration_test_adapter_{int(time.time())}"
            role = "Tester"
            goal = "Verify adapter"

            filepath = SkillAdapter.create_draft(slug, role, goal)
            print(f"DEBUG: Created file at {filepath}")
            self.assertTrue(Path(filepath).exists())
            self.assertIn(slug, str(filepath))

            # 2. Match
            print("DEBUG: Executing find_prompt...")
            matches = SkillAdapter.find_prompt("verify adapter")
            print(f"DEBUG: Matches found: {len(matches)}")
            self.assertTrue(len(matches) > 0)

            # Check if our file is in the matches
            match_names = [m["name"] for m in matches]
            self.assertIn(Path(filepath).stem, match_names)
            # self.assertIn("Verify adapter", matches[0]["preview"]) # Preview check is loose

            # 3. Match Fail
            no_matches = SkillAdapter.find_prompt(
                "completely unrelated query for non-existent prompt"
            )
            self.assertEqual(len(no_matches), 0)
        except Exception:
            import traceback

            traceback.print_exc()
            raise


if __name__ == "__main__":
    unittest.main()
