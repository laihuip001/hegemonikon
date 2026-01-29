"""
Tests for O-Series & S-Series Derivative Selector

Tests the derivative selection logic for O1-O4 and S1-S4 theorems.
"""


import pytest
from mekhane.fep.derivative_selector import (
    select_derivative,
    encode_for_derivative_selection,
    DerivativeRecommendation,
    DerivativeStateSpace,
    get_derivative_description,
    list_derivatives,
)


class TestDerivativeStateSpace:
    """Test state space definitions."""
    
    def test_o1_states_defined(self):
        assert len(DerivativeStateSpace.O1_STATES) == 3
        assert "abstract_problem" in DerivativeStateSpace.O1_STATES
    
    def test_o2_states_defined(self):
        assert len(DerivativeStateSpace.O2_STATES) == 3
        assert "will_action_gap" in DerivativeStateSpace.O2_STATES
    
    def test_o3_states_defined(self):
        assert len(DerivativeStateSpace.O3_STATES) == 3
        assert "hypothesis_needed" in DerivativeStateSpace.O3_STATES
    
    def test_o4_states_defined(self):
        assert len(DerivativeStateSpace.O4_STATES) == 3
        assert "production_goal" in DerivativeStateSpace.O4_STATES


class TestEncodeForDerivativeSelection:
    """Test observation encoding."""
    
    def test_abstract_problem_encoding(self):
        obs = encode_for_derivative_selection("この概念の本質は何か？原理を理解したい", "O1")
        assert obs[0] >= 1  # Abstraction level should be high
    
    def test_practical_situation_encoding(self):
        obs = encode_for_derivative_selection("この具体的なケースで、今回どうすべきか？", "O1")
        assert obs[1] >= 1  # Context dependency should be high
    
    def test_reflection_need_encoding(self):
        obs = encode_for_derivative_selection("この判断は本当に正しいのか？再考した方がいい？", "O1")
        assert obs[2] >= 1  # Reflection need should be high
    
    def test_returns_tuple_of_three(self):
        obs = encode_for_derivative_selection("テスト入力", "O1")
        assert isinstance(obs, tuple)
        assert len(obs) == 3
        assert all(0 <= v <= 2 for v in obs)


class TestSelectDerivativeO1:
    """Test O1 Noēsis derivative selection."""
    
    def test_nous_selection_for_abstract(self):
        result = select_derivative("O1", "この原理の本質を把握したい、普遍的な概念を理解")
        assert result.theorem == "O1"
        assert result.derivative == "nous"
        assert result.confidence > 0.5
    
    def test_phro_selection_for_practical(self):
        result = select_derivative("O1", "この具体的な状況で、今回の場合どう判断すべき？")
        assert result.derivative == "phro"
    
    def test_meta_selection_for_reflection(self):
        result = select_derivative("O1", "この判断は本当に正しいか？再考が必要、どう思う？")
        assert result.derivative == "meta"
    
    def test_has_alternatives(self):
        result = select_derivative("O1", "テスト")
        assert len(result.alternatives) == 2


class TestSelectDerivativeO2:
    """Test O2 Boulēsis derivative selection."""
    
    def test_desir_selection(self):
        result = select_derivative("O2", "〜がしたい、欲しい、この目標を達成したい")
        assert result.derivative == "desir"
    
    def test_voli_selection_for_conflict(self):
        result = select_derivative("O2", "〜したいけど、迷っている、どちらを優先すべきか葛藤")
        assert result.derivative == "voli"
    
    def test_akra_selection_for_gap(self):
        result = select_derivative("O2", "わかっているのにできない、意志が弱い、実行に移せない")
        assert result.derivative == "akra"


class TestSelectDerivativeO3:
    """Test O3 Zētēsis derivative selection."""
    
    def test_anom_selection(self):
        result = select_derivative("O3", "なぜこの現象が起きるのか不思議、違和感がある")
        assert result.derivative == "anom"
    
    def test_hypo_selection(self):
        result = select_derivative("O3", "もしかして〜かもしれない、仮説を立てたい、可能性")
        assert result.derivative == "hypo"
    
    def test_eval_selection(self):
        result = select_derivative("O3", "どれがベストか比較したい、優先順位をつけて評価")
        assert result.derivative == "eval"


class TestSelectDerivativeO4:
    """Test O4 Energeia derivative selection."""
    
    def test_flow_selection(self):
        result = select_derivative("O4", "没入して集中したい、最適なパフォーマンスで楽しく")
        assert result.derivative == "flow"
    
    def test_prax_selection(self):
        result = select_derivative("O4", "それ自体に意味がある、目的ではなく過程、内発的")
        assert result.derivative == "prax"
    
    def test_pois_selection(self):
        result = select_derivative("O4", "この機能を作って完成させたい、成果物を納品")
        assert result.derivative == "pois"
    
    def test_default_to_pois(self):
        """In development context, production is common default."""
        result = select_derivative("O4", "test input without specific keywords")
        assert result.derivative == "pois"


class TestRecommendationStructure:
    """Test DerivativeRecommendation structure."""
    
    def test_recommendation_fields(self):
        result = select_derivative("O1", "テスト入力")
        assert isinstance(result, DerivativeRecommendation)
        assert hasattr(result, "theorem")
        assert hasattr(result, "derivative")
        assert hasattr(result, "confidence")
        assert hasattr(result, "rationale")
        assert hasattr(result, "alternatives")
    
    def test_confidence_range(self):
        result = select_derivative("O1", "テスト")
        assert 0 <= result.confidence <= 1.0
    
    def test_alternatives_are_valid(self):
        result = select_derivative("O1", "テスト")
        valid_derivatives = ["nous", "phro", "meta"]
        assert all(alt in valid_derivatives for alt in result.alternatives)


class TestHelperFunctions:
    """Test utility functions."""
    
    def test_get_derivative_description(self):
        desc = get_derivative_description("O1", "nous")
        assert "本質" in desc or "直観" in desc
    
    def test_list_derivatives(self):
        derivs = list_derivatives("O1")
        assert len(derivs) == 3
        assert "nous" in derivs
        assert "phro" in derivs
        assert "meta" in derivs
    
    def test_unknown_theorem_raises(self):
        with pytest.raises(ValueError):
            select_derivative("O5", "test")


class TestEdgeCases:
    """Test edge cases and robustness."""
    
    def test_empty_input(self):
        result = select_derivative("O1", "")
        assert result.derivative in ["nous", "phro", "meta"]
    
    def test_very_long_input(self):
        long_text = "テスト " * 1000
        result = select_derivative("O1", long_text)
        assert result is not None
    
    def test_mixed_japanese_english(self):
        result = select_derivative("O1", "What is the 本質 of this concept?")
        assert result.derivative == "nous"
    
    def test_unicode_input(self):
        result = select_derivative("O1", "🤔 この問題の本質は？")
        assert result is not None


# =============================================================================
# S-Series Tests
# =============================================================================

class TestDerivativeStateSpaceS:
    """Test S-series state space definitions."""
    
    def test_s1_states_defined(self):
        assert len(DerivativeStateSpace.S1_STATES) == 3
        assert "continuous_measure" in DerivativeStateSpace.S1_STATES
    
    def test_s2_states_defined(self):
        assert len(DerivativeStateSpace.S2_STATES) == 3
        assert "assemble_existing" in DerivativeStateSpace.S2_STATES
    
    def test_s3_states_defined(self):
        assert len(DerivativeStateSpace.S3_STATES) == 3
        assert "ideal_based" in DerivativeStateSpace.S3_STATES
    
    def test_s4_states_defined(self):
        assert len(DerivativeStateSpace.S4_STATES) == 3
        assert "temporal_execution" in DerivativeStateSpace.S4_STATES


class TestSelectDerivativeS1:
    """Test S1 Metron derivative selection."""
    
    def test_cont_selection(self):
        result = select_derivative("S1", "この期間の時間的な流れ、連続的な変化")
        assert result.theorem == "S1"
        assert result.derivative == "cont"
    
    def test_disc_selection(self):
        result = select_derivative("S1", "何個あるか数える、回数、カウント")
        assert result.derivative == "disc"
    
    def test_abst_selection(self):
        result = select_derivative("S1", "どのレベルで見るか、粒度、詳細vs全体")
        assert result.derivative == "abst"
    
    def test_default_to_abst(self):
        result = select_derivative("S1", "test input")
        assert result.derivative == "abst"


class TestSelectDerivativeS2:
    """Test S2 Mekhanē derivative selection."""
    
    def test_comp_selection(self):
        result = select_derivative("S2", "既存のライブラリを組み合わせて統合")
        assert result.derivative == "comp"
    
    def test_inve_selection(self):
        result = select_derivative("S2", "新しい方法をゼロから創出、前例がない")
        assert result.derivative == "inve"
    
    def test_adap_selection(self):
        result = select_derivative("S2", "既存のものを修正してカスタマイズ")
        assert result.derivative == "adap"


class TestSelectDerivativeS3:
    """Test S3 Stathmos derivative selection."""
    
    def test_norm_selection(self):
        result = select_derivative("S3", "理想的にはどうあるべきか、ベストプラクティス")
        assert result.derivative == "norm"
    
    def test_empi_selection(self):
        result = select_derivative("S3", "過去のデータと実績、KPIベンチマーク")
        assert result.derivative == "empi"
    
    def test_rela_selection(self):
        result = select_derivative("S3", "競合と比較、ランキング、他社との相対評価")
        assert result.derivative == "rela"


class TestSelectDerivativeS4:
    """Test S4 Praxis derivative selection."""
    
    def test_prax_selection(self):
        result = select_derivative("S4", "過程が大事、内発的な意味、それ自体が目的")
        assert result.derivative == "prax"
    
    def test_pois_selection(self):
        result = select_derivative("S4", "成果物を納品、製品を完成させる")
        assert result.derivative == "pois"
    
    def test_temp_selection(self):
        result = select_derivative("S4", "アジャイルかウォーターフォールか、繰り返し反復")
        assert result.derivative == "temp"


class TestSSeriesHelperFunctions:
    """Test S-series utility functions."""
    
    def test_get_s1_description(self):
        desc = get_derivative_description("S1", "cont")
        assert "連続" in desc
    
    def test_get_s2_description(self):
        desc = get_derivative_description("S2", "comp")
        assert "統合" in desc or "組立" in desc
    
    def test_list_s_derivatives(self):
        derivs = list_derivatives("S3")
        assert len(derivs) == 3
        assert "norm" in derivs
        assert "empi" in derivs
        assert "rela" in derivs
    
    def test_unknown_s_theorem_raises(self):
        with pytest.raises(ValueError):
            select_derivative("S5", "test")


# =============================================================================
# H-Series Tests
# =============================================================================

class TestDerivativeStateSpaceH:
    """Test H-series state space definitions."""
    
    def test_h1_states_defined(self):
        assert len(DerivativeStateSpace.H1_STATES) == 3
        assert "approach_response" in DerivativeStateSpace.H1_STATES
    
    def test_h2_states_defined(self):
        assert len(DerivativeStateSpace.H2_STATES) == 3
        assert "objective_evidence" in DerivativeStateSpace.H2_STATES
    
    def test_h3_states_defined(self):
        assert len(DerivativeStateSpace.H3_STATES) == 3
        assert "activity_oriented" in DerivativeStateSpace.H3_STATES
    
    def test_h4_states_defined(self):
        assert len(DerivativeStateSpace.H4_STATES) == 3
        assert "formal_belief" in DerivativeStateSpace.H4_STATES


class TestSelectDerivativeH1:
    """Test H1 Propatheia derivative selection."""
    
    def test_appr_selection(self):
        result = select_derivative("H1", "これには惹かれる、興味がある、ポジティブな感じ")
        assert result.theorem == "H1"
        assert result.derivative == "appr"
    
    def test_avoi_selection(self):
        result = select_derivative("H1", "これは嫌だ、避けたい、危険を感じる")
        assert result.derivative == "avoi"
    
    def test_arre_selection(self):
        result = select_derivative("H1", "待って、保留で、判断停止したい")
        assert result.derivative == "arre"
    
    def test_default_to_arre(self):
        result = select_derivative("H1", "neutral test input")
        assert result.derivative == "arre"


class TestSelectDerivativeH2:
    """Test H2 Pistis derivative selection."""
    
    def test_subj_selection(self):
        result = select_derivative("H2", "私はこう思う、直感的にこう感じる、個人的に")
        assert result.derivative == "subj"
    
    def test_inte_selection(self):
        result = select_derivative("H2", "みんなの合意、チームで議論、一般的に")
        assert result.derivative == "inte"
    
    def test_obje_selection(self):
        result = select_derivative("H2", "データによると、証拠がある、実験で検証")
        assert result.derivative == "obje"


class TestSelectDerivativeH3:
    """Test H3 Orexis derivative selection."""
    
    def test_targ_selection(self):
        result = select_derivative("H3", "これが欲しい、この対象を獲得したい")
        assert result.derivative == "targ"
    
    def test_acti_selection(self):
        result = select_derivative("H3", "すること自体を楽しむ、プロセス、やりがい")
        assert result.derivative == "acti"
    
    def test_stat_selection(self):
        result = select_derivative("H3", "平和な状態を維持したい、健康でいたい")
        assert result.derivative == "stat"


class TestSelectDerivativeH4:
    """Test H4 Doxa derivative selection."""
    
    def test_sens_selection(self):
        result = select_derivative("H4", "見た、聞いた、パターンでわかった")
        assert result.derivative == "sens"
    
    def test_conc_selection(self):
        result = select_derivative("H4", "この概念、カテゴリ、分類としては")
        assert result.derivative == "conc"
    
    def test_form_selection(self):
        result = select_derivative("H4", "論理的に、ならば、法則として、証明")
        assert result.derivative == "form"


class TestHSeriesHelperFunctions:
    """Test H-series utility functions."""
    
    def test_get_h1_description(self):
        desc = get_derivative_description("H1", "appr")
        assert "接近" in desc or "Approach" in desc
    
    def test_get_h2_description(self):
        desc = get_derivative_description("H2", "obje")
        assert "客観" in desc or "Objective" in desc
    
    def test_list_h_derivatives(self):
        derivs = list_derivatives("H3")
        assert len(derivs) == 3
        assert "targ" in derivs
        assert "acti" in derivs
        assert "stat" in derivs
    
    def test_unknown_h_theorem_raises(self):
        with pytest.raises(ValueError):
            select_derivative("H5", "test")


# =============================================================================
# P-Series Tests
# =============================================================================

class TestDerivativeStateSpaceP:
    """Test P-series state space definitions."""
    
    def test_p1_states_defined(self):
        assert len(DerivativeStateSpace.P1_STATES) == 3
        assert "physical_space" in DerivativeStateSpace.P1_STATES
    
    def test_p2_states_defined(self):
        assert len(DerivativeStateSpace.P2_STATES) == 3
        assert "cyclical_path" in DerivativeStateSpace.P2_STATES
    
    def test_p3_states_defined(self):
        assert len(DerivativeStateSpace.P3_STATES) == 3
        assert "emergent_attractor" in DerivativeStateSpace.P3_STATES
    
    def test_p4_states_defined(self):
        assert len(DerivativeStateSpace.P4_STATES) == 3
        assert "automated_operation" in DerivativeStateSpace.P4_STATES


class TestSelectDerivativeP1:
    """Test P1 Khōra derivative selection."""
    
    def test_phys_selection(self):
        result = select_derivative("P1", "物理的な場所、建物の位置、どこで実行する？")
        assert result.theorem == "P1"
        assert result.derivative == "phys"
    
    def test_conc_selection(self):
        result = select_derivative("P1", "概念モデル、設計図、スキーマ、マップ")
        assert result.derivative == "conc"
    
    def test_rela_selection(self):
        result = select_derivative("P1", "ネットワーク、関係性、コミュニティ、チーム")
        assert result.derivative == "rela"
    
    def test_default_to_conc(self):
        result = select_derivative("P1", "neutral test input")
        assert result.derivative == "conc"


class TestSelectDerivativeP2:
    """Test P2 Hodos derivative selection."""
    
    def test_line_selection(self):
        result = select_derivative("P2", "順番に、ステップバイステップ、直線的に進める")
        assert result.derivative == "line"
    
    def test_bran_selection(self):
        result = select_derivative("P2", "分岐、条件分岐、AかBか選択肢がある")
        assert result.derivative == "bran"
    
    def test_cycl_selection(self):
        result = select_derivative("P2", "繰り返し、ループ、フィードバック、アジャイル")
        assert result.derivative == "cycl"


class TestSelectDerivativeP3:
    """Test P3 Trokhia derivative selection."""
    
    def test_fixe_selection(self):
        result = select_derivative("P3", "固定、安定、いつも同じ、ルーティン")
        assert result.derivative == "fixe"
    
    def test_adap_selection(self):
        result = select_derivative("P3", "適応、調整、状況に応じて、柔軟に")
        assert result.derivative == "adap"
    
    def test_emer_selection(self):
        result = select_derivative("P3", "創発、自己組織、予測不能、新しいパターン")
        assert result.derivative == "emer"


class TestSelectDerivativeP4:
    """Test P4 Tekhnē derivative selection."""
    
    def test_manu_selection(self):
        result = select_derivative("P4", "手動で、職人の技、ハンズオン、自分で直接")
        assert result.derivative == "manu"
    
    def test_mech_selection(self):
        result = select_derivative("P4", "ツールを使って、機械で支援、効率化、半自動")
        assert result.derivative == "mech"
    
    def test_auto_selection(self):
        result = select_derivative("P4", "自動化、AI、ロボット、完全自動")
        assert result.derivative == "auto"


class TestPSeriesHelperFunctions:
    """Test P-series utility functions."""
    
    def test_get_p1_description(self):
        desc = get_derivative_description("P1", "phys")
        assert "物理" in desc or "Physical" in desc
    
    def test_get_p2_description(self):
        desc = get_derivative_description("P2", "cycl")
        assert "循環" in desc or "Cyclical" in desc
    
    def test_list_p_derivatives(self):
        derivs = list_derivatives("P3")
        assert len(derivs) == 3
        assert "fixe" in derivs
        assert "adap" in derivs
        assert "emer" in derivs
    
    def test_unknown_p_theorem_raises(self):
        with pytest.raises(ValueError):
            select_derivative("P5", "test")


# =============================================================================
# K-Series Tests
# =============================================================================

class TestDerivativeStateSpaceK:
    """Test K-series state space definitions."""
    
    def test_k1_states_defined(self):
        assert len(DerivativeStateSpace.K1_STATES) == 3
        assert "urgent_opportunity" in DerivativeStateSpace.K1_STATES
    
    def test_k2_states_defined(self):
        assert len(DerivativeStateSpace.K2_STATES) == 3
        assert "long_term" in DerivativeStateSpace.K2_STATES
    
    def test_k3_states_defined(self):
        assert len(DerivativeStateSpace.K3_STATES) == 3
        assert "intrinsic_goal" in DerivativeStateSpace.K3_STATES
    
    def test_k4_states_defined(self):
        assert len(DerivativeStateSpace.K4_STATES) == 3
        assert "tacit_knowledge" in DerivativeStateSpace.K4_STATES


class TestSelectDerivativeK1:
    """Test K1 Eukairia derivative selection."""
    
    def test_urge_selection(self):
        result = select_derivative("K1", "緊急！今すぐ対応、deadline")
        assert result.theorem == "K1"
        assert result.derivative == "urge"
    
    def test_opti_selection(self):
        result = select_derivative("K1", "準備完了、最適なタイミング、好機")
        assert result.derivative == "opti"
    
    def test_miss_selection(self):
        result = select_derivative("K1", "もう遅い、逃した、後悔")
        assert result.derivative == "miss"
    
    def test_default_to_miss(self):
        result = select_derivative("K1", "neutral test input")
        assert result.derivative == "miss"


class TestSelectDerivativeK2:
    """Test K2 Chronos derivative selection."""
    
    def test_shor_selection(self):
        result = select_derivative("K2", "今日中に、すぐ、短期")
        assert result.theorem == "K2"
        assert result.derivative == "shor"
    
    def test_medi_selection(self):
        result = select_derivative("K2", "来月、四半期、中期プロジェクト")
        assert result.derivative == "medi"
    
    def test_long_selection(self):
        result = select_derivative("K2", "長期的、来年、戦略、ビジョン")
        assert result.derivative == "long"
    
    def test_default_to_medi(self):
        result = select_derivative("K2", "neutral test input")
        assert result.derivative == "medi"


class TestSelectDerivativeK3:
    """Test K3 Telos derivative selection."""
    
    def test_intr_selection(self):
        result = select_derivative("K3", "楽しい、成長、やりがい")
        assert result.theorem == "K3"
        assert result.derivative == "intr"
    
    def test_inst_selection(self):
        result = select_derivative("K3", "お金のため、昇進、手段")
        assert result.derivative == "inst"
    
    def test_ulti_selection(self):
        result = select_derivative("K3", "人生の意義、使命、Eudaimonia")
        assert result.derivative == "ulti"
    
    def test_default_returns_valid_derivative(self):
        """Neutral input should return any valid K3 derivative."""
        result = select_derivative("K3", "neutral test input")
        assert result.derivative in ["intr", "inst", "ulti"]


class TestSelectDerivativeK4:
    """Test K4 Sophia derivative selection."""
    
    def test_taci_selection(self):
        result = select_derivative("K4", "直感、経験、体で覚える")
        assert result.theorem == "K4"
        assert result.derivative == "taci"
    
    def test_expl_selection(self):
        result = select_derivative("K4", "マニュアル、文書、データ")
        assert result.derivative == "expl"
    
    def test_meta_selection(self):
        result = select_derivative("K4", "メタ認識、何が分からないか、限界")
        assert result.derivative == "meta"
    
    def test_default_to_taci(self):
        result = select_derivative("K4", "neutral test input")
        assert result.derivative == "taci"


class TestKSeriesHelperFunctions:
    """Test K-series utility functions."""
    
    def test_get_k1_description(self):
        desc = get_derivative_description("K1", "urge")
        assert "緊急" in desc or "Urgent" in desc
    
    def test_get_k2_description(self):
        desc = get_derivative_description("K2", "long")
        assert "長期" in desc or "Long" in desc
    
    def test_list_k_derivatives(self):
        derivs = list_derivatives("K3")
        assert len(derivs) == 3
        assert "intr" in derivs
        assert "inst" in derivs
        assert "ulti" in derivs
    
    def test_unknown_k_theorem_raises(self):
        with pytest.raises(ValueError):
            select_derivative("K5", "test")


# =============================================================================
# A-Series Tests
# =============================================================================

class TestDerivativeStateSpaceA:
    """Test A-series state space definitions."""
    
    def test_a1_states_defined(self):
        assert len(DerivativeStateSpace.A1_STATES) == 3
        assert "primary_emotion" in DerivativeStateSpace.A1_STATES
    
    def test_a2_states_defined(self):
        assert len(DerivativeStateSpace.A2_STATES) == 3
        assert "suspend_judgment" in DerivativeStateSpace.A2_STATES
    
    def test_a3_states_defined(self):
        assert len(DerivativeStateSpace.A3_STATES) == 3
        assert "universal_wisdom" in DerivativeStateSpace.A3_STATES
    
    def test_a4_states_defined(self):
        assert len(DerivativeStateSpace.A4_STATES) == 3
        assert "certain_knowledge" in DerivativeStateSpace.A4_STATES


class TestSelectDerivativeA1:
    """Test A1 Pathos derivative selection."""
    
    def test_prim_selection(self):
        result = select_derivative("A1", "怒りが湧いてきた、自動的、直感的")
        assert result.theorem == "A1"
        assert result.derivative == "prim"
    
    def test_seco_selection(self):
        result = select_derivative("A1", "罪悪感を感じる、後悔、メタ感情")
        assert result.derivative == "seco"
    
    def test_regu_selection(self):
        result = select_derivative("A1", "落ち着いて再評価、感情を制御")
        assert result.derivative == "regu"
    
    def test_default_returns_valid_derivative(self):
        """Neutral input should return any valid A1 derivative."""
        result = select_derivative("A1", "neutral test input")
        assert result.derivative in ["prim", "seco", "regu"]


class TestSelectDerivativeA2:
    """Test A2 Krisis derivative selection."""
    
    def test_affi_selection(self):
        result = select_derivative("A2", "肯定する、はい、賛成、認める")
        assert result.theorem == "A2"
        assert result.derivative == "affi"
    
    def test_nega_selection(self):
        result = select_derivative("A2", "否定、いいえ、拒否、ダメ")
        assert result.derivative == "nega"
    
    def test_susp_selection(self):
        result = select_derivative("A2", "保留、分からない、要検討")
        assert result.derivative == "susp"
    
    def test_default_to_nega(self):
        result = select_derivative("A2", "neutral test input")
        assert result.derivative == "nega"


class TestSelectDerivativeA3:
    """Test A3 Gnōmē derivative selection."""
    
    def test_conc_selection(self):
        result = select_derivative("A3", "このケースでは、具体的に")
        assert result.theorem == "A3"
        assert result.derivative == "conc"
    
    def test_abst_selection(self):
        result = select_derivative("A3", "抽象的な原則、一般的なパターン")
        assert result.derivative == "abst"
    
    def test_univ_selection(self):
        result = select_derivative("A3", "普遍的、永遠の真理、絶対")
        assert result.derivative == "univ"
    
    def test_default_to_conc(self):
        result = select_derivative("A3", "neutral test input")
        assert result.derivative == "conc"


class TestSelectDerivativeA4:
    """Test A4 Epistēmē derivative selection."""
    
    def test_tent_selection(self):
        result = select_derivative("A4", "仮説、たぶん、検証が必要")
        assert result.theorem == "A4"
        assert result.derivative == "tent"
    
    def test_just_selection(self):
        result = select_derivative("A4", "根拠あり、エビデンス、論理的")
        assert result.derivative == "just"
    
    def test_cert_selection(self):
        result = select_derivative("A4", "確実、事実、間違いない")
        assert result.derivative == "cert"
    
    def test_default_returns_valid_derivative(self):
        """Neutral input should return any valid A4 derivative."""
        result = select_derivative("A4", "neutral test input")
        assert result.derivative in ["tent", "just", "cert"]


class TestASeriesHelperFunctions:
    """Test A-series utility functions."""
    
    def test_get_a1_description(self):
        desc = get_derivative_description("A1", "prim")
        assert "一次" in desc or "Primary" in desc
    
    def test_get_a2_description(self):
        desc = get_derivative_description("A2", "susp")
        assert "保留" in desc or "Suspend" in desc
    
    def test_list_a_derivatives(self):
        derivs = list_derivatives("A3")
        assert len(derivs) == 3
        assert "conc" in derivs
        assert "abst" in derivs
        assert "univ" in derivs
    
    def test_unknown_a_theorem_raises(self):
        with pytest.raises(ValueError):
            select_derivative("A5", "test")
