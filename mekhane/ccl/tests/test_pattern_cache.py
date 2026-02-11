"""Tests for mekhane.ccl.pattern_cache.PatternCache."""

import unittest
from mekhane.ccl.pattern_cache import PatternCache


# PURPOSE: Test suite validating pattern cache generate correctness
class TestPatternCacheGenerate(unittest.TestCase):
    """Test PatternCache.generate() workflow matching."""

    # PURPOSE: Verify set up behaves correctly
    def setUp(self):
        """Verify set up behavior."""
        self.cache = PatternCache()

    # --- O-Series keywords ---

    # PURPOSE: Verify noesis keyword behaves correctly
    def test_noesis_keyword(self):
        """Verify noesis keyword behavior."""
        result = self.cache.generate("本質を理解したい")
        self.assertIsNotNone(result)
        self.assertIn("/noe", result)

    # PURPOSE: Verify boulesis keyword behaves correctly
    def test_boulesis_keyword(self):
        """Verify boulesis keyword behavior."""
        result = self.cache.generate("目標を決めたい")
        self.assertIsNotNone(result)
        self.assertIn("/bou", result)

    # PURPOSE: Verify zetesis keyword behaves correctly
    def test_zetesis_keyword(self):
        """Verify zetesis keyword behavior."""
        result = self.cache.generate("問いを探求する")
        self.assertIsNotNone(result)
        self.assertIn("/zet", result)

    # PURPOSE: Verify energeia keyword behaves correctly
    def test_energeia_keyword(self):
        """Verify energeia keyword behavior."""
        result = self.cache.generate("実装する")
        self.assertIsNotNone(result)
        self.assertIn("/ene", result)

    # --- S-Series keywords ---

    # PURPOSE: Verify strategy keyword behaves correctly
    def test_strategy_keyword(self):
        """Verify strategy keyword behavior."""
        result = self.cache.generate("設計を計画する")
        self.assertIsNotNone(result)
        self.assertIn("/s", result)

    # PURPOSE: Verify mekhane keyword behaves correctly
    def test_mekhane_keyword(self):
        """Verify mekhane keyword behavior."""
        result = self.cache.generate("ツールを生成する")
        self.assertIsNotNone(result)

    # PURPOSE: Verify stathmos keyword behaves correctly
    def test_stathmos_keyword(self):
        """Verify stathmos keyword behavior."""
        result = self.cache.generate("基準を評価する")
        self.assertIsNotNone(result)
        self.assertIn("/sta", result)

    # --- A-Series keywords ---

    # PURPOSE: Verify krisis keyword behaves correctly
    def test_krisis_keyword(self):
        """Verify krisis keyword behavior."""
        result = self.cache.generate("判定してレビューする")
        self.assertIsNotNone(result)
        self.assertIn("/dia", result)

    # --- Modifiers ---

    # PURPOSE: Verify detailed modifier behaves correctly
    def test_detailed_modifier(self):
        """Verify detailed modifier behavior."""
        result = self.cache.generate("詳細に分析する")
        self.assertIsNotNone(result)
        self.assertIn("+", result)

    # PURPOSE: Verify summary modifier behaves correctly
    def test_summary_modifier(self):
        """Verify summary modifier behavior."""
        result = self.cache.generate("要約して判断する")
        self.assertIsNotNone(result)
        self.assertIn("-", result)

    # PURPOSE: Verify meta modifier behaves correctly
    def test_meta_modifier(self):
        """Verify meta modifier behavior."""
        result = self.cache.generate("メタな分析をする")
        self.assertIsNotNone(result)
        self.assertIn("^", result)

    # --- Structure ---

    # PURPOSE: Verify sequence structure behaves correctly
    def test_sequence_structure(self):
        """Multiple workflows joined with _ (default)."""
        result = self.cache.generate("分析して判定する")
        self.assertIsNotNone(result)
        self.assertIn("_", result)

    # PURPOSE: Verify parallel structure behaves correctly
    def test_parallel_structure(self):
        """同時 keyword triggers * structure."""
        result = self.cache.generate("認識 目標 同時")
        self.assertIsNotNone(result)
        self.assertIn("*", result)

    # PURPOSE: Verify oscillation structure behaves correctly
    def test_oscillation_structure(self):
        """往復 keyword triggers ~ structure."""
        result = self.cache.generate("認識 目標 往復")
        self.assertIsNotNone(result)
        self.assertIn("~", result)

    # --- Loop pattern ---

    # PURPOSE: Verify loop pattern behaves correctly
    def test_loop_pattern(self):
        """Verify loop pattern behavior."""
        result = self.cache.generate("分析を3回繰り返す")
        self.assertIsNotNone(result)
        self.assertIn("F:×3", result)

    # PURPOSE: Verify loop with inner workflow behaves correctly
    def test_loop_with_inner_workflow(self):
        """Verify loop with inner workflow behavior."""
        result = self.cache.generate("判定を5回する")
        self.assertIsNotNone(result)
        self.assertIn("F:×5", result)
        self.assertIn("/dia", result)

    # --- Edge cases ---

    # PURPOSE: Verify no match returns none behaves correctly
    def test_no_match_returns_none(self):
        """Verify no match returns none behavior."""
        result = self.cache.generate("hello world nothing matches")
        self.assertIsNone(result)

    # PURPOSE: Verify empty string behaves correctly
    def test_empty_string(self):
        """Verify empty string behavior."""
        result = self.cache.generate("")
        self.assertIsNone(result)

    # PURPOSE: Verify case insensitive behaves correctly
    def test_case_insensitive(self):
        """Japanese keywords don't have case, but test the lowering."""
        result = self.cache.generate("実装")
        self.assertIsNotNone(result)


# PURPOSE: Test suite validating pattern cache generate inner correctness
class TestPatternCacheGenerateInner(unittest.TestCase):
    """Test _generate_inner() directly."""

    # PURPOSE: Verify set up behaves correctly
    def setUp(self):
        """Verify set up behavior."""
        self.cache = PatternCache()

    # PURPOSE: Verify single workflow no modifier behaves correctly
    def test_single_workflow_no_modifier(self):
        """Single unambiguous keyword → single workflow."""
        result = self.cache._generate_inner("レビュー")
        self.assertIsNotNone(result)
        self.assertIn("/dia", result)

    # PURPOSE: Verify single workflow with modifier behaves correctly
    def test_single_workflow_with_modifier(self):
        """Verify single workflow with modifier behavior."""
        result = self.cache._generate_inner("詳細に分析する")
        self.assertIn("+", result)

    # PURPOSE: Verify multiple workflows sequence behaves correctly
    def test_multiple_workflows_sequence(self):
        """Verify multiple workflows sequence behavior."""
        result = self.cache._generate_inner("分析して判定する")
        self.assertIsNotNone(result)
        parts = result.split("_")
        self.assertGreaterEqual(len(parts), 2)


if __name__ == "__main__":
    unittest.main()
