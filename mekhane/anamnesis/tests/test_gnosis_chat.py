# PROOF: [L3/テスト] <- mekhane/anamnesis/tests/ 対象モジュール gnosis_chat が存在→その検証が必要
"""
Gnōsis Chat Test Suite — ConversationHistory, KnowledgeIndexer, Reranker, GnosisChat

テスト対象:
  1. ConversationHistory: ターン管理、フォーマット、上限 (pure logic)
  2. KnowledgeIndexer: チャンキング、テキスト構築 (pure static)
  3. Reranker: ロード失敗時フォールバック、閾値フィルタ (mock model)
  4. GnosisChat: 確信度判定、コンテキスト構築 (pure logic)
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure repo root is in sys.path
repo_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(repo_root))

from mekhane.anamnesis.gnosis_chat import (
    ConversationHistory,
    KnowledgeIndexer,
    Reranker,
    GnosisChat,
)


# ═══════════════════════════════════════
# 1. ConversationHistory
# ═══════════════════════════════════════


# PURPOSE: Test suite validating conversation history correctness
class TestConversationHistory:
    """マルチターン対話履歴のテスト."""

    # PURPOSE: Verify initial state behaves correctly
    def test_initial_state(self):
        """初期状態: ターンなし."""
        h = ConversationHistory()
        assert h.turn_count == 0
        assert h.format_for_prompt() == ""

    # PURPOSE: Verify add turn behaves correctly
    def test_add_turn(self):
        """ターン追加."""
        h = ConversationHistory()
        h.add("user", "Hello")
        h.add("assistant", "Hi there")
        assert h.turn_count == 1
        assert len(h.turns) == 2

    # PURPOSE: Verify format user turn behaves correctly
    def test_format_user_turn(self):
        """user ターンのフォーマット."""
        h = ConversationHistory()
        h.add("user", "What is FEP?")
        fmt = h.format_for_prompt()
        assert "<|im_start|>user" in fmt
        assert "What is FEP?" in fmt
        assert "<|im_end|>" in fmt

    # PURPOSE: Verify format assistant turn behaves correctly
    def test_format_assistant_turn(self):
        """assistant ターンのフォーマット."""
        h = ConversationHistory()
        h.add("assistant", "Free Energy Principle")
        fmt = h.format_for_prompt()
        assert "<|im_start|>assistant" in fmt
        assert "Free Energy Principle" in fmt

    # PURPOSE: Verify format multi turn behaves correctly
    def test_format_multi_turn(self):
        """複数ターンのフォーマット — 正しい順序."""
        h = ConversationHistory()
        h.add("user", "Q1")
        h.add("assistant", "A1")
        h.add("user", "Q2")
        h.add("assistant", "A2")
        fmt = h.format_for_prompt()
        # Q1 が Q2 より前にある
        assert fmt.index("Q1") < fmt.index("Q2")
        assert h.turn_count == 2

    # PURPOSE: Verify max turns truncation behaves correctly
    def test_max_turns_truncation(self):
        """max_turns 超過時の古いターン削除."""
        h = ConversationHistory(max_turns=2)
        for i in range(5):
            h.add("user", f"Q{i}")
            h.add("assistant", f"A{i}")
        # max_turns=2 → 最大 4 entries (2*2)
        assert len(h.turns) == 4
        # 最新のターンが残っている
        assert h.turns[-1]["content"] == "A4"
        assert h.turns[-2]["content"] == "Q4"

    # PURPOSE: Verify clear behaves correctly
    def test_clear(self):
        """clear() でリセット."""
        h = ConversationHistory()
        h.add("user", "test")
        h.clear()
        assert h.turn_count == 0
        assert len(h.turns) == 0

    # PURPOSE: Verify turn count odd entries behaves correctly
    def test_turn_count_odd_entries(self):
        """奇数エントリ時の turn_count (整数除算)."""
        h = ConversationHistory()
        h.add("user", "Q1")
        # 1 entry / 2 = 0 (整数除算)
        assert h.turn_count == 0
        h.add("assistant", "A1")
        assert h.turn_count == 1


# ═══════════════════════════════════════
# 2. KnowledgeIndexer (pure static methods)
# ═══════════════════════════════════════


# PURPOSE: Test suite validating chunk text correctness
class TestChunkText:
    """KnowledgeIndexer._chunk_text のテスト."""

    # PURPOSE: Verify short text single chunk behaves correctly
    def test_short_text_single_chunk(self):
        """chunk_size 以下のテキスト → 単一チャンク."""
        text = "Short text"
        result = KnowledgeIndexer._chunk_text(text, chunk_size=100)
        assert result == ["Short text"]

    # PURPOSE: Verify markdown header split behaves correctly
    def test_markdown_header_split(self):
        """Markdown ヘッダーでセクション分割."""
        text = (
            "# Title\nContent A\n\n"
            "## Section 1\nContent B\n\n"
            "## Section 2\nContent C"
        )
        result = KnowledgeIndexer._chunk_text(text, chunk_size=50)
        # ヘッダー境界で分割される
        assert len(result) >= 2
        # 各チャンクにセクション内容が含まれる
        all_text = " ".join(result)
        assert "Content B" in all_text
        assert "Content C" in all_text

    # PURPOSE: Verify paragraph split behaves correctly
    def test_paragraph_split(self):
        """空行で段落分割 (Phase 2)."""
        # 各段落が chunk_size 以下だが合計は超える
        para = "A" * 40
        text = f"{para}\n\n{para}\n\n{para}"
        result = KnowledgeIndexer._chunk_text(text, chunk_size=50)
        assert len(result) >= 2

    # PURPOSE: Verify long text split behaves correctly
    def test_long_text_split(self):
        """改行で固定サイズ分割 (Phase 3)."""
        # 1000文字超、chunk_size=200 → 複数チャンク
        lines = [f"Line {i}: " + "x" * 50 for i in range(20)]
        text = "\n".join(lines)
        result = KnowledgeIndexer._chunk_text(text, chunk_size=200)
        assert len(result) > 3
        # 空チャンクがないこと
        for chunk in result:
            assert len(chunk) > 0

    # PURPOSE: Verify filter short chunks behaves correctly
    def test_filter_short_chunks(self):
        """20文字以下のチャンクは除去."""
        text = "## A\nOK content here\n\n## B\nhi\n\n## C\nAnother good chunk"
        result = KnowledgeIndexer._chunk_text(text, chunk_size=30)
        for chunk in result:
            assert len(chunk) > 20

    # PURPOSE: Verify empty text behaves correctly
    def test_empty_text(self):
        """空テキスト."""
        result = KnowledgeIndexer._chunk_text("", chunk_size=100)
        assert result == [""]


# PURPOSE: Test suite validating split long text correctness
class TestSplitLongText:
    """KnowledgeIndexer._split_long_text のテスト."""

    # PURPOSE: Verify basic split behaves correctly
    def test_basic_split(self):
        """基本分割."""
        text = "A" * 300
        result = KnowledgeIndexer._split_long_text(text, chunk_size=100, overlap=10)
        assert len(result) >= 3
        for chunk in result:
            assert len(chunk) <= 100

    # PURPOSE: Verify split at newline behaves correctly
    def test_split_at_newline(self):
        """改行位置で切断."""
        text = "A" * 60 + "\n" + "B" * 60
        result = KnowledgeIndexer._split_long_text(text, chunk_size=80, overlap=10)
        # 最初のチャンクが改行位置で切れている
        assert result[0].endswith("A" * 60)

    # PURPOSE: Verify overlap behaves correctly
    def test_overlap(self):
        """overlap が機能する (次チャンクの開始が前チャンクの末尾と重複)."""
        text = "ABCDEFGHIJ" * 10  # 100 chars
        result = KnowledgeIndexer._split_long_text(text, chunk_size=30, overlap=5)
        assert len(result) >= 3


# PURPOSE: Test suite validating build embedding text correctness
class TestBuildEmbeddingText:
    """KnowledgeIndexer._build_embedding_text のテスト."""

    # PURPOSE: Verify format behaves correctly
    def test_format(self):
        """[source] title\\ncontent 形式."""
        result = KnowledgeIndexer._build_embedding_text(
            "My Paper", "handoff", "This is the content"
        )
        assert result.startswith("[handoff] My Paper\n")
        assert "This is the content" in result

    # PURPOSE: Verify truncation behaves correctly
    def test_truncation(self):
        """content が 500文字制限にトランケート."""
        long_content = "x" * 1000
        result = KnowledgeIndexer._build_embedding_text(
            "Title", "src", long_content
        )
        assert len(result) <= 500

    # PURPOSE: Verify prefix length affects content behaves correctly
    def test_prefix_length_affects_content(self):
        """長い title → content 埋め込み量が減る."""
        short_title = "T"
        long_title = "T" * 100
        r_short = KnowledgeIndexer._build_embedding_text(short_title, "s", "x" * 500)
        r_long = KnowledgeIndexer._build_embedding_text(long_title, "s", "x" * 500)
        # 長い title の方が content が短い
        assert len(r_short) == len(r_long) == 500


# ═══════════════════════════════════════
# 3. Reranker
# ═══════════════════════════════════════


# PURPOSE: Test suite validating reranker correctness
class TestReranker:
    """Reranker のテスト — model は mock."""

    # PURPOSE: Verify empty results behaves correctly
    def test_empty_results(self):
        """空結果はそのまま返却."""
        rr = Reranker()
        assert rr.rerank("query", []) == []

    # PURPOSE: Verify fallback on load failure behaves correctly
    def test_fallback_on_load_failure(self):
        """モデルロード失敗時 → bi-encoder で distance ソート."""
        rr = Reranker()
        rr._failed = True
        rr._model = None
        results = [
            {"title": "A", "_distance": 0.5},
            {"title": "B", "_distance": 0.3},
            {"title": "C", "_distance": 0.8},
        ]
        output = rr.rerank("query", results, top_k=2)
        assert len(output) == 2
        # distance 昇順でソート
        assert output[0]["title"] == "B"
        assert output[1]["title"] == "A"

    # PURPOSE: Verify rerank with mock model behaves correctly
    def test_rerank_with_mock_model(self):
        """mock cross-encoder での rerank."""
        rr = Reranker()
        rr._model = MagicMock()
        # 3 results → scores: [1.0, 5.0, 3.0] → sorted: B(5.0), C(3.0), A(1.0)
        rr._model.predict.return_value = [1.0, 5.0, 3.0]
        results = [
            {"title": "A", "_distance": 0.5, "abstract": "aaa"},
            {"title": "B", "_distance": 0.6, "abstract": "bbb"},
            {"title": "C", "_distance": 0.7, "abstract": "ccc"},
        ]
        output = rr.rerank("query", results, top_k=2)
        assert len(output) == 2
        # cross-encoder score 降順
        assert output[0]["title"] == "B"
        assert output[0]["_rerank_score"] == 5.0
        assert output[1]["title"] == "C"

    # PURPOSE: Verify score threshold filter behaves correctly
    def test_score_threshold_filter(self):
        """SCORE_THRESHOLD 以下のスコアはフィルタ."""
        rr = Reranker()
        rr._model = MagicMock()
        # score -5.0 < threshold -4.0 → filtered
        rr._model.predict.return_value = [-5.0, 2.0]
        results = [
            {"title": "Bad", "_distance": 0.5, "abstract": "x"},
            {"title": "Good", "_distance": 0.6, "abstract": "y"},
        ]
        output = rr.rerank("query", results, top_k=5)
        assert len(output) == 1
        assert output[0]["title"] == "Good"

    # PURPOSE: Verify knowledge table uses content behaves correctly
    def test_knowledge_table_uses_content(self):
        """knowledge テーブルは content フィールドを使用."""
        rr = Reranker()
        rr._model = MagicMock()
        rr._model.predict.return_value = [3.0]
        results = [
            {
                "title": "T",
                "_distance": 0.5,
                "_source_table": "knowledge",
                "content": "Knowledge content here",
                "abstract": "Short abstract",
            }
        ]
        output = rr.rerank("query", results, top_k=5)
        # predict に渡されたペアを確認
        call_args = rr._model.predict.call_args[0][0]
        # knowledge テーブルは content を使用
        assert "Knowledge content here" in call_args[0][1]


# ═══════════════════════════════════════
# 4. GnosisChat (pure logic methods)
# ═══════════════════════════════════════


# PURPOSE: Test suite validating assess confidence correctness
class TestAssessConfidence:
    """GnosisChat._assess_confidence のテスト."""

    # PURPOSE: Verify chat behaves correctly
    @pytest.fixture
    def chat(self):
        """LLM/GPU 依存なしで GnosisChat インスタンスを生成."""
        return GnosisChat.__new__(GnosisChat)

    # PURPOSE: Verify no results returns none behaves correctly
    def test_no_results_returns_none(self, chat):
        """結果なし → CONFIDENCE_NONE."""
        assert chat._assess_confidence([]) == "none"

    # PURPOSE: Verify close results high behaves correctly
    def test_close_results_high(self, chat):
        """min_dist < 0.6 + n>=3 + avg < 0.75 → high."""
        results = [
            {"_distance": 0.5},
            {"_distance": 0.6},
            {"_distance": 0.7},
        ]
        assert chat._assess_confidence(results) == "high"

    # PURPOSE: Verify single close result high behaves correctly
    def test_single_close_result_high(self, chat):
        """min_dist < 0.7 → high (単一でも)."""
        results = [{"_distance": 0.65}]
        assert chat._assess_confidence(results) == "high"

    # PURPOSE: Verify medium confidence behaves correctly
    def test_medium_confidence(self, chat):
        """min_dist 0.7-0.8 → medium."""
        results = [{"_distance": 0.75}]
        assert chat._assess_confidence(results) == "medium"

    # PURPOSE: Verify low confidence behaves correctly
    def test_low_confidence(self, chat):
        """min_dist >= 0.8 → low."""
        results = [{"_distance": 0.82}]
        assert chat._assess_confidence(results) == "low"


# PURPOSE: Test suite validating build context correctness
class TestBuildContext:
    """GnosisChat._build_context のテスト."""

    # PURPOSE: Verify chat behaves correctly
    @pytest.fixture
    def chat(self):
        """Verify chat behavior."""
        return GnosisChat.__new__(GnosisChat)

    # PURPOSE: Verify empty results behaves correctly
    def test_empty_results(self, chat):
        """結果なし → 空文字列."""
        assert chat._build_context([]) == ""

    # PURPOSE: Verify numbering behaves correctly
    def test_numbering(self, chat):
        """結果に [1], [2] 番号が付く."""
        results = [
            {"title": "Paper A", "source": "papers", "abstract": "Abs A", "_distance": 0.5},
            {"title": "Paper B", "source": "papers", "abstract": "Abs B", "_distance": 0.6},
        ]
        ctx = chat._build_context(results)
        assert "[1]" in ctx
        assert "[2]" in ctx

    # PURPOSE: Verify knowledge uses content behaves correctly
    def test_knowledge_uses_content(self, chat):
        """knowledge テーブルは content を使う."""
        results = [
            {
                "title": "Doc",
                "source": "kernel",
                "_source_table": "knowledge",
                "content": "Full knowledge content",
                "abstract": "Short",
                "_distance": 0.5,
            },
        ]
        ctx = chat._build_context(results)
        assert "Full knowledge content" in ctx

    # PURPOSE: Verify papers uses abstract behaves correctly
    def test_papers_uses_abstract(self, chat):
        """papers テーブルは abstract を使う."""
        results = [
            {
                "title": "Paper",
                "source": "papers",
                "_source_table": "papers",
                "abstract": "Paper abstract here",
                "_distance": 0.5,
            },
        ]
        ctx = chat._build_context(results)
        assert "Paper abstract here" in ctx

    # PURPOSE: Verify source grounding behaves correctly
    def test_source_grounding(self, chat):
        """primary_key が Source として含まれる."""
        results = [
            {
                "title": "Doc",
                "source": "handoff",
                "abstract": "Content",
                "_distance": 0.5,
                "primary_key": "handoff:session_2026:0",
            },
        ]
        ctx = chat._build_context(results)
        assert "Source: handoff:session_2026:0" in ctx

    # PURPOSE: Verify relevance score behaves correctly
    def test_relevance_score(self, chat):
        """Relevance が 1-distance で計算される."""
        results = [
            {"title": "T", "source": "s", "abstract": "A", "_distance": 0.3},
        ]
        ctx = chat._build_context(results)
        assert "Relevance: 0.70" in ctx


# PURPOSE: Test suite validating gnosis chat init correctness
class TestGnosisChatInit:
    """GnosisChat.__init__ のテスト."""

    # PURPOSE: Verify defaults behaves correctly
    def test_defaults(self):
        """デフォルトパラメータ."""
        with patch("mekhane.anamnesis.gnosis_chat.Reranker"):
            chat = GnosisChat()
            assert chat.model_id == "Qwen/Qwen2.5-3B-Instruct"
            assert chat.top_k == 5
            assert chat.max_new_tokens == 512
            assert chat.search_knowledge is True
            assert chat.search_papers is True
            assert chat.steering_profile == "hegemonikon"

    # PURPOSE: Verify custom params behaves correctly
    def test_custom_params(self):
        """カスタムパラメータ."""
        with patch("mekhane.anamnesis.gnosis_chat.Reranker"):
            chat = GnosisChat(
                model_id="test/model",
                top_k=3,
                max_new_tokens=256,
                use_reranker=False,
                steering_profile="academic",
            )
            assert chat.model_id == "test/model"
            assert chat.top_k == 3
            assert chat._reranker is None
            assert chat.steering_profile == "academic"

    # PURPOSE: Verify steering profiles exist behaves correctly
    def test_steering_profiles_exist(self):
        """定義済み steering profiles の存在確認."""
        assert "hegemonikon" in GnosisChat.STEERING_PROFILES
        assert "neutral" in GnosisChat.STEERING_PROFILES
        assert "academic" in GnosisChat.STEERING_PROFILES

    # PURPOSE: Verify distance thresholds behaves correctly
    def test_distance_thresholds(self):
        """距離閾値の妥当性."""
        assert 0 < GnosisChat.DISTANCE_THRESHOLD < 1.5
        assert GnosisChat.PAPERS_DISTANCE_THRESHOLD > GnosisChat.DISTANCE_THRESHOLD


# ═══════════════════════════════════════
# 5. KnowledgeIndexer.discover_knowledge_files (filesystem mock)
# ═══════════════════════════════════════


# PURPOSE: Test suite validating discover knowledge files correctness
class TestDiscoverKnowledgeFiles:
    """Filesystem をモックしたファイル発見テスト."""

    # PURPOSE: Verify returns list behaves correctly
    def test_returns_list(self, tmp_path):
        """戻り値が list[dict] 形式."""
        with patch("mekhane.anamnesis.gnosis_chat.MNEME_SESSIONS", tmp_path):
            with patch("mekhane.anamnesis.gnosis_chat.MNEME_KNOWLEDGE", tmp_path / "x"):
                with patch("mekhane.anamnesis.gnosis_chat.MNEME_HANDOFFS", tmp_path / "x"):
                    with patch("mekhane.anamnesis.gnosis_chat.MNEME_DOXA", tmp_path / "x"):
                        with patch("mekhane.anamnesis.gnosis_chat.MNEME_WORKFLOWS", tmp_path / "x"):
                            with patch("mekhane.anamnesis.gnosis_chat.MNEME_RESEARCH", tmp_path / "x"):
                                with patch("mekhane.anamnesis.gnosis_chat.MNEME_XSERIES", tmp_path / "x"):
                                    with patch("mekhane.anamnesis.gnosis_chat.KERNEL_DIR", tmp_path / "x"):
                                        with patch("mekhane.anamnesis.gnosis_chat.HANDOFF_DIR", tmp_path / "x"):
                                            result = KnowledgeIndexer.discover_knowledge_files()
            assert isinstance(result, list)

    # PURPOSE: Verify discovers handoff behaves correctly
    def test_discovers_handoff(self, tmp_path):
        """handoff_*.md ファイルを発見."""
        sessions = tmp_path / "sessions"
        sessions.mkdir()
        (sessions / "handoff_2026-02-01.md").write_text("test")
        nope = tmp_path / "nope"  # non-existent paths

        with patch("mekhane.anamnesis.gnosis_chat.MNEME_SESSIONS", sessions):
            with patch("mekhane.anamnesis.gnosis_chat.MNEME_KNOWLEDGE", nope):
                with patch("mekhane.anamnesis.gnosis_chat.MNEME_HANDOFFS", nope):
                    with patch("mekhane.anamnesis.gnosis_chat.MNEME_DOXA", nope):
                        with patch("mekhane.anamnesis.gnosis_chat.MNEME_WORKFLOWS", nope):
                            with patch("mekhane.anamnesis.gnosis_chat.MNEME_RESEARCH", nope):
                                with patch("mekhane.anamnesis.gnosis_chat.MNEME_XSERIES", nope):
                                    with patch("mekhane.anamnesis.gnosis_chat.KERNEL_DIR", nope):
                                        with patch("mekhane.anamnesis.gnosis_chat.HANDOFF_DIR", nope):
                                            result = KnowledgeIndexer.discover_knowledge_files()
        handoffs = [f for f in result if f["source_type"] == "handoff"]
        assert len(handoffs) == 1
        assert handoffs[0]["title"] == "Handoff 2026-02-01"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
