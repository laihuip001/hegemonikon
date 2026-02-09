"""Tests for mekhane.ccl.pattern_cache.PatternCache."""

import unittest
from mekhane.ccl.pattern_cache import PatternCache


class TestPatternCacheGenerate(unittest.TestCase):
    """Test PatternCache.generate() workflow matching."""

    def setUp(self):
        self.cache = PatternCache()

    # --- O-Series keywords ---

    def test_noesis_keyword(self):
        result = self.cache.generate("本質を理解したい")
        self.assertIsNotNone(result)
        self.assertIn("/noe", result)

    def test_boulesis_keyword(self):
        result = self.cache.generate("目標を決めたい")
        self.assertIsNotNone(result)
        self.assertIn("/bou", result)

    def test_zetesis_keyword(self):
        result = self.cache.generate("問いを探求する")
        self.assertIsNotNone(result)
        self.assertIn("/zet", result)

    def test_energeia_keyword(self):
        result = self.cache.generate("実装する")
        self.assertIsNotNone(result)
        self.assertIn("/ene", result)

    # --- S-Series keywords ---

    def test_strategy_keyword(self):
        result = self.cache.generate("設計を計画する")
        self.assertIsNotNone(result)
        self.assertIn("/s", result)

    def test_mekhane_keyword(self):
        result = self.cache.generate("ツールを生成する")
        self.assertIsNotNone(result)

    def test_stathmos_keyword(self):
        result = self.cache.generate("基準を評価する")
        self.assertIsNotNone(result)
        self.assertIn("/sta", result)

    # --- A-Series keywords ---

    def test_krisis_keyword(self):
        result = self.cache.generate("判定してレビューする")
        self.assertIsNotNone(result)
        self.assertIn("/dia", result)

    # --- Modifiers ---

    def test_detailed_modifier(self):
        result = self.cache.generate("詳細に分析する")
        self.assertIsNotNone(result)
        self.assertIn("+", result)

    def test_summary_modifier(self):
        result = self.cache.generate("要約して判断する")
        self.assertIsNotNone(result)
        self.assertIn("-", result)

    def test_meta_modifier(self):
        result = self.cache.generate("メタな分析をする")
        self.assertIsNotNone(result)
        self.assertIn("^", result)

    # --- Structure ---

    def test_sequence_structure(self):
        """Multiple workflows joined with _ (default)."""
        result = self.cache.generate("分析して判定する")
        self.assertIsNotNone(result)
        self.assertIn("_", result)

    def test_parallel_structure(self):
        """同時 keyword triggers * structure."""
        result = self.cache.generate("認識 目標 同時")
        self.assertIsNotNone(result)
        self.assertIn("*", result)

    def test_oscillation_structure(self):
        """往復 keyword triggers ~ structure."""
        result = self.cache.generate("認識 目標 往復")
        self.assertIsNotNone(result)
        self.assertIn("~", result)

    # --- Loop pattern ---

    def test_loop_pattern(self):
        result = self.cache.generate("分析を3回繰り返す")
        self.assertIsNotNone(result)
        self.assertIn("F:×3", result)

    def test_loop_with_inner_workflow(self):
        result = self.cache.generate("判定を5回する")
        self.assertIsNotNone(result)
        self.assertIn("F:×5", result)
        self.assertIn("/dia", result)

    # --- Edge cases ---

    def test_no_match_returns_none(self):
        result = self.cache.generate("hello world nothing matches")
        self.assertIsNone(result)

    def test_empty_string(self):
        result = self.cache.generate("")
        self.assertIsNone(result)

    def test_case_insensitive(self):
        """Japanese keywords don't have case, but test the lowering."""
        result = self.cache.generate("実装")
        self.assertIsNotNone(result)


class TestPatternCacheGenerateInner(unittest.TestCase):
    """Test _generate_inner() directly."""

    def setUp(self):
        self.cache = PatternCache()

    def test_single_workflow_no_modifier(self):
        """Single unambiguous keyword → single workflow."""
        result = self.cache._generate_inner("レビュー")
        self.assertIsNotNone(result)
        self.assertIn("/dia", result)

    def test_single_workflow_with_modifier(self):
        result = self.cache._generate_inner("詳細に分析する")
        self.assertIn("+", result)

    def test_multiple_workflows_sequence(self):
        result = self.cache._generate_inner("分析して判定する")
        self.assertIsNotNone(result)
        parts = result.split("_")
        self.assertGreaterEqual(len(parts), 2)


if __name__ == "__main__":
    unittest.main()
