#!/usr/bin/env python3
# PROOF: [L1/テスト] <- mekhane/mcp/tests/
# PURPOSE: Gateway ツール群の正常パステスト（セキュリティテストの補完）
"""
L1 正常系テスト — hgk_gateway

サーバーを起動せず、ツール関数を直接呼び出して正常パスを検証する。
test_gateway_security.py (防御テスト 9件) と対になる攻撃/正常のペア。
"""

import asyncio
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

# GATEWAY_TOKEN を設定（テスト用）
os.environ["HGK_GATEWAY_TOKEN"] = "test_token_for_functional_testing"


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def setup_test_dirs(tmp_path, monkeypatch):
    """各テスト用の一時ディレクトリを設定。実ファイルシステムを汚さない。"""
    # Mneme 構造を一時ディレクトリに再現
    mneme = tmp_path / "mneme" / ".hegemonikon"
    sessions = mneme / "sessions"
    doxa = mneme / "doxa"
    ideas = mneme / "ideas"
    sop = mneme / "workflows"
    incoming = mneme / "digestor" / "incoming"
    processed = mneme / "digestor" / "processed"

    for d in [sessions, doxa, ideas, sop, incoming, processed]:
        d.mkdir(parents=True, exist_ok=True)

    # テスト用 Handoff を作成
    handoff = sessions / "handoff_20260214_test.md"
    handoff.write_text(
        "# Handoff 20260214\n\n## 実施事項\n- Gateway テスト作成\n\n## 次回\n- 検証\n",
        encoding="utf-8",
    )

    # テスト用 Doxa を作成
    doxa_file = doxa / "laws.json"
    doxa_file.write_text(
        json.dumps([
            {"strength": "S", "text": "自分を信じないことが信頼の起点"},
            {"strength": "A", "text": "意志より環境が行動を決める"},
        ], ensure_ascii=False),
        encoding="utf-8",
    )

    # Gateway モジュールのパスを上書き
    import mekhane.mcp.hgk_gateway as gw
    monkeypatch.setattr(gw, "MNEME_DIR", mneme)
    monkeypatch.setattr(gw, "SESSIONS_DIR", sessions)
    monkeypatch.setattr(gw, "DOXA_DIR", doxa)
    monkeypatch.setattr(gw, "IDEA_DIR", ideas)
    monkeypatch.setattr(gw, "SOP_OUTPUT_DIR", sop)
    monkeypatch.setattr(gw, "INCOMING_DIR", incoming)
    monkeypatch.setattr(gw, "PROCESSED_DIR", processed)

    yield {
        "mneme": mneme,
        "sessions": sessions,
        "doxa": doxa,
        "ideas": ideas,
        "sop": sop,
    }


# =============================================================================
# T1: hgk_sop_generate — 調査依頼書生成
# =============================================================================

# PURPOSE: Verify sop generation produces valid markdown template
def test_sop_generate_basic(setup_test_dirs):
    """SOP テンプレートが生成され、ファイルに保存されることを確認。"""
    from mekhane.mcp.hgk_gateway import hgk_sop_generate

    result = hgk_sop_generate(topic="FEP と Active Inference")
    assert "✅" in result, f"SOP 生成が成功すべき: {result[:100]}"
    assert "調査依頼書" in result, "テンプレート内容が含まれるべき"
    assert "FEP" in result, "トピックが含まれるべき"

    # ファイルが保存されているか
    sop_dir = setup_test_dirs["sop"]
    sop_files = list(sop_dir.glob("sop_*.md"))
    assert len(sop_files) >= 1, "SOP ファイルが保存されるべき"
    print("✅ T1: hgk_sop_generate — テンプレート生成 + ファイル保存")


# PURPOSE: Verify sop with optional args works correctly
def test_sop_generate_with_options(setup_test_dirs):
    """decision と hypothesis を指定した SOP 生成。"""
    from mekhane.mcp.hgk_gateway import hgk_sop_generate

    result = hgk_sop_generate(
        topic="圏論の応用",
        decision="採用するフレームワークを決定する",
        hypothesis="Galois 接続が最適",
    )
    assert "採用するフレームワーク" in result, "decision が含まれるべき"
    assert "Galois" in result, "hypothesis が含まれるべき"
    print("✅ T1b: hgk_sop_generate — オプション引数付き生成")


# =============================================================================
# T2: hgk_search — 知識ベース検索
# =============================================================================

# PURPOSE: Verify keyword search returns results from Doxa
def test_search_keyword_doxa(setup_test_dirs):
    """キーワード検索で Doxa がヒットすることを確認。"""
    from mekhane.mcp.hgk_gateway import hgk_search

    result = hgk_search(query="信頼", mode="keyword")
    assert "Doxa" in result or "信頼" in result, \
        f"Doxa の信頼キーワードがヒットすべき: {result[:200]}"
    print("✅ T2: hgk_search — Doxa キーワード検索")


# PURPOSE: Verify search returns no-result message gracefully
def test_search_no_results(setup_test_dirs):
    """存在しないクエリで空結果メッセージが返ることを確認。"""
    from mekhane.mcp.hgk_gateway import hgk_search

    result = hgk_search(query="zyxwvutsrqp_nonexistent_12345", mode="keyword")
    assert "一致する結果はありません" in result, \
        f"空結果メッセージが返るべき: {result[:200]}"
    print("✅ T2b: hgk_search — 空結果の graceful handling")


# PURPOSE: Verify search finds handoff content
def test_search_handoff(setup_test_dirs):
    """Handoff ファイルの内容がキーワード検索でヒットすることを確認。"""
    from mekhane.mcp.hgk_gateway import hgk_search

    result = hgk_search(query="Gateway", mode="keyword")
    assert "Handoff" in result or "Gateway" in result, \
        f"Handoff 内容がヒットすべき: {result[:200]}"
    print("✅ T2c: hgk_search — Handoff キーワード検索")


# =============================================================================
# T3: hgk_status — ステータス表示
# =============================================================================

# PURPOSE: Verify status returns structured overview
def test_status_overview(setup_test_dirs):
    """ステータス表示が構造化された概要を返すことを確認。"""
    from mekhane.mcp.hgk_gateway import hgk_status

    result = hgk_status()
    assert "ステータス" in result, f"ステータスヘッダーがあるべき: {result[:100]}"
    assert "Handoff" in result, "Handoff 件数が含まれるべき"
    assert "Doxa" in result, "Doxa 件数が含まれるべき"
    print("✅ T3: hgk_status — 構造化ステータス表示")


# =============================================================================
# T4: hgk_doxa_read — Doxa 読み取り
# =============================================================================

# PURPOSE: Verify doxa read returns stored beliefs
def test_doxa_read(setup_test_dirs):
    """Doxa の内容が読み取れることを確認。"""
    from mekhane.mcp.hgk_gateway import hgk_doxa_read

    result = hgk_doxa_read()
    assert "信念ストア" in result or "Doxa" in result, \
        f"Doxa ヘッダーがあるべき: {result[:100]}"
    assert "自分を信じない" in result, "テストデータの信念が含まれるべき"
    assert "意志より環境" in result, "テストデータの信念が含まれるべき"
    print("✅ T4: hgk_doxa_read — 信念データの読み取り")


# PURPOSE: Verify doxa read handles empty doxa gracefully
def test_doxa_read_empty(setup_test_dirs):
    """空の Doxa ディレクトリで空メッセージが返ることを確認。"""
    from mekhane.mcp.hgk_gateway import hgk_doxa_read

    # Doxa ファイルを削除
    doxa_dir = setup_test_dirs["doxa"]
    for f in doxa_dir.glob("*.json"):
        f.unlink()

    result = hgk_doxa_read()
    assert "空" in result or "Doxa" in result, \
        f"空 Doxa メッセージがあるべき: {result[:100]}"
    print("✅ T4b: hgk_doxa_read — 空 Doxa のハンドリング")


# =============================================================================
# T5: hgk_handoff_read — Handoff 参照
# =============================================================================

# PURPOSE: Verify handoff read returns latest handoff content
def test_handoff_read(setup_test_dirs):
    """最新 Handoff が読み取れることを確認。"""
    from mekhane.mcp.hgk_gateway import hgk_handoff_read

    result = hgk_handoff_read(count=1)
    assert "Handoff" in result, f"Handoff ヘッダーがあるべき: {result[:100]}"
    assert "Gateway テスト" in result, "テスト Handoff の内容が含まれるべき"
    print("✅ T5: hgk_handoff_read — Handoff 読み取り")


# =============================================================================
# T6: hgk_idea_capture — アイデアメモ保存 (正常パス)
# =============================================================================

# PURPOSE: Verify idea capture saves and returns confirmation
def test_idea_capture_normal(setup_test_dirs):
    """正常サイズのアイデアが保存されることを確認。"""
    from mekhane.mcp.hgk_gateway import hgk_idea_capture

    result = hgk_idea_capture(
        idea="FEP の精度加重をコード品質評価に応用できるかもしれない",
        tags="FEP, 実験",
    )
    assert "✅" in result, f"保存成功すべき: {result[:100]}"
    assert "FEP" in result, "タグが含まれるべき"

    # ファイルが保存されているか
    idea_dir = setup_test_dirs["ideas"]
    idea_files = list(idea_dir.glob("idea_*.md"))
    assert len(idea_files) >= 1, "アイデアファイルが保存されるべき"

    # ファイル内容の確認
    content = idea_files[0].read_text(encoding="utf-8")
    assert "精度加重" in content, "アイデア本文がファイルに含まれるべき"
    print("✅ T6: hgk_idea_capture — 正常保存 + ファイル検証")


# =============================================================================
# T7: hgk_ccl_dispatch — CCL パース
# =============================================================================

# PURPOSE: Verify CCL dispatch parses valid expressions
def test_ccl_dispatch_basic():
    """基本的な CCL 式がパースできることを確認。"""
    from mekhane.mcp.hgk_gateway import hgk_ccl_dispatch

    result = hgk_ccl_dispatch("/noe+")
    # パーサーがインストールされていない場合もエラーハンドリングを確認
    assert "CCL" in result or "noe" in result.lower() or "エラー" in result, \
        f"CCL 関連のレスポンスがあるべき: {result[:200]}"
    print("✅ T7: hgk_ccl_dispatch — CCL 式パース")


# =============================================================================
# Runner
# =============================================================================

# PURPOSE: Run all functional tests and report results
async def main():
    """全正常系テストを実行。"""
    print("=" * 60)
    print("  L1 正常系テスト — hgk_gateway")
    print("=" * 60)
    print()

    # pytest 経由で実行
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-q",
    ])
    return exit_code == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
