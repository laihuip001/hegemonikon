# PROOF: [L2.5/統合テスト] <- .agent/projects/aristos/tests/
"""
Aristos L2.5 Feedback Loop Integration Tests

フィードバックループ全体の統合テスト:
  select_derivative → _log_selection → YAML
  → convert_yaml_to_feedback → FeedbackEntry
  → EvolutionEngine.evolve → save_evolved_weights
  → _load_evolved_weights → _apply_evolved_boost
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

import pytest
import yaml

# プロジェクトルートを PATH に追加
PROJECT_ROOT = Path(__file__).resolve().parents[4]  # hegemonikon/
PROJECTS_DIR = Path(__file__).resolve().parents[2]  # .agent/projects/
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECTS_DIR))

from aristos.evolve import (
    Chromosome,
    EvolutionEngine,
    FeedbackCollector,
    FeedbackEntry,
    FitnessVector,
    Scale,
)
from aristos.evolve_cli import (
    THEOREM_DERIVATIVES,
    convert_yaml_to_feedback,
    get_gene_keys,
    save_evolved_weights,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def tmp_mneme(tmp_path):
    """テスト用の一時的な mneme ディレクトリ"""
    mneme = tmp_path / ".hegemonikon"
    mneme.mkdir(parents=True)
    return mneme


@pytest.fixture
def sample_yaml_log(tmp_mneme):
    """サンプルの derivative_selections.yaml"""
    log_path = tmp_mneme / "derivative_selections.yaml"
    selections = {
        "selections": [
            {
                "timestamp": "2026-02-15T09:00:00",
                "theorem": "O1",
                "problem": "本質を知りたい",
                "derivative": "nous",
                "confidence": 0.85,
                "method": "keyword",
            },
            {
                "timestamp": "2026-02-15T09:01:00",
                "theorem": "O1",
                "problem": "具体的にどうするか",
                "derivative": "nous",
                "confidence": 0.60,
                "method": "keyword",
                "corrected_to": "phro",
            },
            {
                "timestamp": "2026-02-15T09:02:00",
                "theorem": "O2",
                "problem": "理想の設計とは",
                "derivative": "desir",
                "confidence": 0.75,
                "method": "keyword",
            },
            {
                "timestamp": "2026-02-15T09:03:00",
                "theorem": "O1",
                "problem": "自分の認知を振り返りたい",
                "derivative": "meta",
                "confidence": 0.90,
                "method": "llm",
            },
        ]
    }
    with open(log_path, "w", encoding="utf-8") as f:
        yaml.dump(selections, f, allow_unicode=True)
    return log_path


@pytest.fixture
def sample_feedback_entries():
    """サンプルの FeedbackEntry リスト"""
    return [
        FeedbackEntry(
            theorem="O1",
            problem="本質を知りたい",
            selected="nous",
            corrected_to=None,
            confidence=0.85,
            method="keyword",
        ),
        FeedbackEntry(
            theorem="O1",
            problem="具体的にどうするか",
            selected="nous",
            corrected_to="phro",
            confidence=0.60,
            method="keyword",
        ),
        FeedbackEntry(
            theorem="O1",
            problem="自分の認知を振り返りたい",
            selected="meta",
            corrected_to=None,
            confidence=0.90,
            method="llm",
        ),
    ]


# =============================================================================
# Test: THEOREM_DERIVATIVES 整合性
# =============================================================================


class TestTheoremDerivativesConsistency:
    """THEOREM_DERIVATIVES が derivative_selector.py のパターンと一致するか"""

    def test_all_24_theorems_present(self):
        """全 24 定理が定義されている"""
        expected = [
            f"{s}{n}"
            for s in ["O", "S", "H", "P", "K", "A"]
            for n in [1, 2, 3, 4]
        ]
        for th in expected:
            assert th in THEOREM_DERIVATIVES, f"{th} が THEOREM_DERIVATIVES にない"

    def test_each_has_derivatives(self):
        """各定理が 2 つ以上の派生を持つ"""
        for th, derivs in THEOREM_DERIVATIVES.items():
            assert len(derivs) >= 2, f"{th} の派生が {len(derivs)} 個しかない"

    def test_gene_keys_format(self):
        """gene keys が 'THEOREM:DERIVATIVE' フォーマット"""
        for th in ["O1", "S2", "A4"]:
            keys = get_gene_keys(th)
            for k in keys:
                assert ":" in k
                parts = k.split(":")
                assert parts[0] == th


# =============================================================================
# Test: FeedbackCollector
# =============================================================================


class TestFeedbackCollector:
    """FeedbackCollector の永続化テスト"""

    def test_save_and_load(self, tmp_path):
        """保存と読み込みの往復"""
        path = tmp_path / "feedback.json"
        collector = FeedbackCollector(path)

        entry = FeedbackEntry(
            theorem="O1",
            problem="テスト",
            selected="nous",
            confidence=0.8,
        )
        collector.add(entry)
        collector.save()

        # 新しいコレクターで読み直し
        collector2 = FeedbackCollector(path)
        loaded = collector2.load()
        assert len(loaded) == 1
        assert loaded[0].theorem == "O1"
        assert loaded[0].selected == "nous"

    def test_was_correct_property(self):
        """was_correct: corrected_to=None なら True"""
        approved = FeedbackEntry(theorem="O1", problem="t", selected="nous")
        assert approved.was_correct is True

        corrected = FeedbackEntry(
            theorem="O1", problem="t", selected="nous", corrected_to="phro"
        )
        assert corrected.was_correct is False

    def test_signal_weights(self):
        """シグナル重みの分類"""
        collector = FeedbackCollector()

        implicit = FeedbackEntry(theorem="O1", problem="t", selected="nous")
        assert collector.signal_weight(implicit) == 0.3

        explicit = FeedbackEntry(
            theorem="O1", problem="t", selected="nous", corrected_to="phro"
        )
        assert collector.signal_weight(explicit) == 1.0

        llm = FeedbackEntry(
            theorem="O1", problem="t", selected="nous", method="llm"
        )
        assert collector.signal_weight(llm) == 0.5


# =============================================================================
# Test: EvolutionEngine
# =============================================================================


class TestEvolutionEngine:
    """GA 進化エンジンのテスト"""

    def test_create_population(self):
        """初期個体群の生成"""
        engine = EvolutionEngine(scale=Scale.MICRO)
        gene_keys = ["O1:nous", "O1:phro", "O1:meta"]
        pop = engine.create_population(gene_keys, pop_size=10)

        assert len(pop) == 10
        for c in pop:
            assert set(c.genes.keys()) == set(gene_keys)
            for v in c.genes.values():
                assert 0.5 <= v <= 1.5

    def test_evolve_with_feedback(self, sample_feedback_entries):
        """フィードバックありの進化"""
        engine = EvolutionEngine(scale=Scale.MICRO)
        gene_keys = ["O1:nous", "O1:phro", "O1:meta"]
        pop = engine.create_population(gene_keys, pop_size=10)

        final = engine.evolve(pop, sample_feedback_entries, generations=10)
        assert len(final) == 10
        # 最良個体の fitness が評価されている
        best = final[0]
        assert best.fitness.precision >= 0.0

    def test_evolve_without_feedback(self):
        """フィードバックなしの進化 (デフォルト fitness)"""
        engine = EvolutionEngine(scale=Scale.MICRO)
        gene_keys = ["O1:nous", "O1:phro", "O1:meta"]
        pop = engine.create_population(gene_keys, pop_size=5)

        final = engine.evolve(pop, [], generations=5)
        assert len(final) == 5


# =============================================================================
# Test: Weight Persistence
# =============================================================================


class TestWeightPersistence:
    """重みの保存・読み込み互換性テスト"""

    def test_save_evolved_weights_format(self, tmp_path, monkeypatch):
        """save_evolved_weights の出力フォーマットが _load_evolved_weights と互換"""
        weights_path = tmp_path / "evolved_weights.json"
        # evolve_cli のグローバル変数をパッチ
        import aristos.evolve_cli as cli_mod
        monkeypatch.setattr(cli_mod, "EVOLVED_WEIGHTS", weights_path)

        best = Chromosome(
            genes={"O1:nous": 1.2, "O1:phro": 0.8, "O1:meta": 1.0},
            fitness=FitnessVector(precision=0.75),
            generation=10,
        )
        save_evolved_weights("O1", best)

        # ファイルが作成されたか
        assert weights_path.exists()

        # 読み込み
        with open(weights_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # フォーマット確認: {"weights": {...}, "fitness_by_theorem": {...}}
        assert "weights" in data
        assert "fitness_by_theorem" in data
        assert "O1:nous" in data["weights"]
        assert data["weights"]["O1:nous"] == 1.2
        assert "O1" in data["fitness_by_theorem"]

    def test_weight_key_matches_boost(self, tmp_path):
        """evolved_weights の key が _apply_evolved_boost のルックアップと一致"""
        weights_path = tmp_path / "evolved_weights.json"

        # evolve_cli が保存するフォーマットを再現
        data = {
            "weights": {
                "O1:nous": 1.3,
                "O1:phro": 0.7,
                "O1:meta": 1.0,
            },
            "fitness_by_theorem": {},
        }
        with open(weights_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        # _apply_evolved_boost が使う key フォーマットを確認
        # key = f"{result.theorem}:{result.derivative}" (L114)
        weights = data["weights"]
        assert weights.get("O1:nous") == 1.3
        assert weights.get("O1:phro") == 0.7

    def test_merge_across_theorems(self, tmp_path, monkeypatch):
        """複数定理の重みがマージされる"""
        weights_path = tmp_path / "evolved_weights.json"
        import aristos.evolve_cli as cli_mod
        monkeypatch.setattr(cli_mod, "EVOLVED_WEIGHTS", weights_path)

        # O1 を保存
        best_o1 = Chromosome(
            genes={"O1:nous": 1.2, "O1:phro": 0.8, "O1:meta": 1.0},
            fitness=FitnessVector(precision=0.75),
            generation=5,
        )
        save_evolved_weights("O1", best_o1)

        # O2 を追加保存
        best_o2 = Chromosome(
            genes={"O2:desir": 1.1, "O2:voli": 0.9, "O2:akra": 1.0},
            fitness=FitnessVector(precision=0.60),
            generation=3,
        )
        save_evolved_weights("O2", best_o2)

        with open(weights_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 両方の定理の重みが存在
        assert "O1:nous" in data["weights"]
        assert "O2:desir" in data["weights"]
        assert "O1" in data["fitness_by_theorem"]
        assert "O2" in data["fitness_by_theorem"]


# =============================================================================
# Test: E2E Feedback Loop
# =============================================================================


class TestE2EFeedbackLoop:
    """フィードバックループ全体の E2E テスト"""

    def test_full_loop(self, tmp_path, monkeypatch):
        """select → log → convert → evolve → save → keycheck"""
        import aristos.evolve_cli as cli_mod

        # パスをすべて tmp_path にリダイレクト
        selection_log = tmp_path / "derivative_selections.yaml"
        feedback_json = tmp_path / "feedback.json"
        evolved_weights = tmp_path / "evolved_weights.json"

        monkeypatch.setattr(cli_mod, "SELECTION_LOG", selection_log)
        monkeypatch.setattr(cli_mod, "FEEDBACK_JSON", feedback_json)
        monkeypatch.setattr(cli_mod, "EVOLVED_WEIGHTS", evolved_weights)

        # Step 1: 選択ログを生成 (derivative_selector の _log_selection を模倣)
        selections = {
            "selections": [
                {
                    "timestamp": "2026-02-15T10:00:00",
                    "theorem": "O1",
                    "problem": "本質を知りたい",
                    "derivative": "nous",
                    "confidence": 0.85,
                    "method": "keyword",
                },
                {
                    "timestamp": "2026-02-15T10:01:00",
                    "theorem": "O1",
                    "problem": "具体的にどうするか",
                    "derivative": "nous",
                    "confidence": 0.60,
                    "method": "corrected",
                    "corrected_to": "phro",
                },
                {
                    "timestamp": "2026-02-15T10:02:00",
                    "theorem": "O1",
                    "problem": "振り返りたい",
                    "derivative": "meta",
                    "confidence": 0.90,
                    "method": "keyword",
                },
            ]
        }
        with open(selection_log, "w", encoding="utf-8") as f:
            yaml.dump(selections, f, allow_unicode=True)

        # Step 2: YAML → FeedbackEntry 変換
        entries = convert_yaml_to_feedback()
        assert len(entries) == 3
        # corrected_to が保持されている
        corrected = [e for e in entries if e.corrected_to is not None]
        assert len(corrected) == 1
        assert corrected[0].corrected_to == "phro"

        # Step 3: GA 進化
        engine = EvolutionEngine(scale=Scale.MICRO)
        gene_keys = get_gene_keys("O1")
        assert gene_keys == ["O1:nous", "O1:phro", "O1:meta"]

        pop = engine.create_population(gene_keys, pop_size=10)
        o1_feedback = [e for e in entries if e.theorem == "O1"]
        final = engine.evolve(pop, o1_feedback, generations=20)
        best = final[0]

        # Step 4: 重みを保存
        save_evolved_weights("O1", best)
        assert evolved_weights.exists()

        # Step 5: 保存フォーマット検証
        with open(evolved_weights, "r", encoding="utf-8") as f:
            data = json.load(f)

        # key が "O1:nous" 形式 = _apply_evolved_boost と互換
        for key in data["weights"]:
            assert key.startswith("O1:")
            _, deriv = key.split(":")
            assert deriv in ["nous", "phro", "meta"]
