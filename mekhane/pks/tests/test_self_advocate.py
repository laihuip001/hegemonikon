#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/pks/tests/
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

A0 (FEP) → SelfAdvocate の正しさを検証する必要がある
→ test_self_advocate.py が担う

# PURPOSE: SelfAdvocate のテスト
"""

import pytest
from mekhane.pks.pks_engine import KnowledgeNugget, SessionContext
from mekhane.pks.self_advocate import SelfAdvocate, Advocacy


# PURPOSE: テスト用ナゲット生成
def _make_nugget(**kwargs) -> KnowledgeNugget:
    defaults = {
        "title": "Active Inference: A Process Theory",
        "source": "arxiv",
        "relevance_score": 0.85,
        "abstract": "We present a process theory of Active Inference based on FEP.",
        "url": "https://arxiv.org/abs/1234.5678",
        "push_reason": "FEP に直接関連",
    }
    defaults.update(kwargs)
    return KnowledgeNugget(**defaults)


# PURPOSE: テスト用コンテキスト生成
def _make_context(**kwargs) -> SessionContext:
    defaults = {
        "topics": ["FEP", "Active Inference", "CCL"],
    }
    defaults.update(kwargs)
    return SessionContext(**defaults)


class TestAdvocacy:
    """Advocacy データクラスのテスト"""

    # PURPOSE: Markdown 出力の基本テスト
    def test_to_markdown_basic(self):
        adv = Advocacy(
            paper_title="Test Paper",
            voice="私はTest Paperです。あなたを手伝えます。",
            key_contribution="FEP の形式化",
            how_to_use="アブストラクトを読んでください。",
            relevance_score=0.85,
        )
        md = adv.to_markdown()
        assert "Test Paper" in md
        assert "私はTest Paperです" in md
        assert "FEP の形式化" in md
        assert "0.85" in md

    # PURPOSE: 関連度なしの場合
    def test_to_markdown_no_score(self):
        adv = Advocacy(
            paper_title="X",
            voice="v",
            key_contribution="c",
            how_to_use="h",
        )
        md = adv.to_markdown()
        assert "関連度" not in md


class TestSelfAdvocateTemplate:
    """SelfAdvocate テンプレート生成テスト (LLM なし)"""

    # PURPOSE: テンプレートフォールバックの基本テスト
    def test_template_basic(self):
        advocate = SelfAdvocate.__new__(SelfAdvocate)
        advocate._llm = type("MockLLM", (), {"available": False})()

        nugget = _make_nugget()
        context = _make_context()
        result = advocate.generate(nugget, context)

        assert isinstance(result, Advocacy)
        assert "Active Inference" in result.paper_title
        assert "私は" in result.voice
        assert result.relevance_score == 0.85

    # PURPOSE: コンテキストなしのフォールバック
    def test_template_no_context(self):
        advocate = SelfAdvocate.__new__(SelfAdvocate)
        advocate._llm = type("MockLLM", (), {"available": False})()

        nugget = _make_nugget()
        result = advocate.generate(nugget, None)

        assert isinstance(result, Advocacy)
        assert "私は" in result.voice

    # PURPOSE: トピックとの接点検出
    def test_context_connection(self):
        advocate = SelfAdvocate.__new__(SelfAdvocate)
        advocate._llm = type("MockLLM", (), {"available": False})()

        nugget = _make_nugget(title="FEP Parameter Validation")
        context = _make_context(topics=["FEP"])
        result = advocate.generate(nugget, context)

        assert "FEP" in result.voice

    # PURPOSE: バッチ生成
    def test_batch_generation(self):
        advocate = SelfAdvocate.__new__(SelfAdvocate)
        advocate._llm = type("MockLLM", (), {"available": False})()

        nuggets = [_make_nugget(title=f"Paper {i}") for i in range(3)]
        results = advocate.generate_batch(nuggets)

        assert len(results) == 3
        for r in results:
            assert isinstance(r, Advocacy)

    # PURPOSE: レポート整形
    def test_format_report(self):
        advocate = SelfAdvocate.__new__(SelfAdvocate)
        advocate._llm = type("MockLLM", (), {"available": False})()

        nuggets = [_make_nugget(title=f"Paper {i}") for i in range(2)]
        results = advocate.generate_batch(nuggets)
        report = advocate.format_report(results)

        assert "Autophōnos" in report
        assert "Paper 0" in report
        assert "Paper 1" in report

    # PURPOSE: 空リストのレポート
    def test_format_report_empty(self):
        advocate = SelfAdvocate.__new__(SelfAdvocate)
        advocate._llm = type("MockLLM", (), {"available": False})()

        report = advocate.format_report([])
        assert "語りかける論文はありません" in report


class TestSelfAdvocateLLMParse:
    """LLM レスポンスパースのテスト"""

    # PURPOSE: 正常な LLM レスポンスのパース
    def test_parse_valid_response(self):
        advocate = SelfAdvocate.__new__(SelfAdvocate)
        advocate._llm = type("MockLLM", (), {"available": False})()

        text = (
            "VOICE: 私はActive Inferenceの論文です。FEPの枠組みの中で、あなたの研究に貢献できます。\n"
            "CONTRIBUTION: FEPに基づくプロセス理論の形式化。\n"
            "HOW_TO_USE: まずセクション3をお読みください。"
        )
        nugget = _make_nugget()
        result = advocate._parse_llm_response(text, nugget)

        assert result is not None
        assert "私は" in result.voice
        assert "形式化" in result.key_contribution
        assert "セクション3" in result.how_to_use

    # PURPOSE: 不完全な LLM レスポンス
    def test_parse_incomplete_response(self):
        advocate = SelfAdvocate.__new__(SelfAdvocate)
        advocate._llm = type("MockLLM", (), {"available": False})()

        text = "これは無効なレスポンスです。"
        nugget = _make_nugget()
        result = advocate._parse_llm_response(text, nugget)

        assert result is None
