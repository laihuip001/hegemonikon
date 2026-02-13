#!/usr/bin/env python3
"""
L1 動的セキュリティテスト — hgk_gateway

直接 Python で HGKOAuthProvider + ツールのセキュリティ制約を検証する。
サーバーを起動せず、ユニットテストとして各制約を検証。
"""

import asyncio
import os
import sys

import pytest
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

# GATEWAY_TOKEN を設定（テスト用）
os.environ["HGK_GATEWAY_TOKEN"] = "test_token_for_dynamic_testing"

from mekhane.mcp.hgk_gateway import (
    HGKOAuthProvider,
    ALLOWED_CLIENT_IDS,
    hgk_idea_capture,
    hgk_ccl_execute,
    hgk_paper_search,
    hgk_digest_run,
)


# PURPOSE: Verify c1 failsafe behaves correctly
@pytest.mark.asyncio
async def test_c1_failsafe():
    """C-1: TOKEN 未設定時の起動拒否はモジュールレベルで実施済み。
    ここでは TOKEN が設定済みの場合にプロバイダーが正常動作することを確認。"""
    provider = HGKOAuthProvider("test_token")
    # load_access_token: 正しいトークン
    token = await provider.load_access_token("test_token")
    assert token is not None, "C-1: 正しいトークンで認証成功すべき"
    # load_access_token: 不正なトークン
    token = await provider.load_access_token("wrong_token")
    assert token is None, "C-1: 不正トークンは拒否すべき"
    print("✅ C-1: トークン検証 — 正常トークン通過、不正トークン拒否")


# PURPOSE: Verify c2 whitelist behaves correctly
@pytest.mark.asyncio
async def test_c2_whitelist():
    """C-2: ホワイトリスト外クライアントの拒否"""
    provider = HGKOAuthProvider("test_token")

    # ホワイトリスト内クライアント
    for cid in ALLOWED_CLIENT_IDS:
        client = await provider.get_client(cid)
        assert client is not None, f"C-2: ホワイトリスト内 {cid} は登録されるべき"

    # ホワイトリスト外クライアント
    unknown = await provider.get_client("evil-attacker.example.com")
    assert unknown is None, "C-2: ホワイトリスト外クライアントは拒否すべき"

    unknown2 = await provider.get_client("suspicious.app")
    assert unknown2 is None, "C-2: 任意の unknown client_id は拒否すべき"

    print(f"✅ C-2: ホワイトリスト — {len(ALLOWED_CLIENT_IDS)} 件通過、2件拒否")


# PURPOSE: Verify c3 size limit behaves correctly
def test_c3_size_limit():
    """C-3: idea_capture サイズ制限"""
    # 正常サイズ
    result = hgk_idea_capture("Test idea", tags="test")
    assert "✅" in result, f"C-3: 正常サイズは成功すべき: {result[:100]}"

    # 巨大入力 (10,001文字)
    big_idea = "A" * 10_001
    result = hgk_idea_capture(big_idea, tags="overflow")
    assert "❌" in result, f"C-3: 10K超過は拒否すべき: {result[:100]}"
    assert "10001" in result or "10,001" in result or "10001" in result, \
        "C-3: エラーメッセージに文字数が含まれるべき"

    # ちょうど10,000文字（境界値）
    exact = "B" * 10_000
    result = hgk_idea_capture(exact, tags="boundary")
    assert "✅" in result, f"C-3: ちょうど10K文字は成功すべき: {result[:100]}"

    print("✅ C-3: サイズ制限 — 正常通過、10K超過拒否、境界値通過")


# PURPOSE: Verify c4 token expiry behaves correctly
@pytest.mark.asyncio
async def test_c4_token_expiry():
    """C-4: トークン有効期限"""
    provider = HGKOAuthProvider("test_token")

    # クライアント登録 + 認証コード取得
    client = await provider.get_client("claude.ai")
    assert client is not None

    from mcp.server.auth.provider import AuthorizationParams
    from pydantic import AnyHttpUrl

    params = AuthorizationParams(
        client_id="claude.ai",
        redirect_uri=AnyHttpUrl("https://claude.ai/api/auth/callback"),
        state="test_state",
        scopes=["read"],
        code_challenge="test_challenge",
        code_challenge_method="S256",
        redirect_uri_provided_explicitly=True,
    )

    redirect_url = await provider.authorize(client, params)
    assert "code=" in redirect_url, "C-4: 認証コードが発行されるべき"

    # 認証コードを取得
    from urllib.parse import urlparse, parse_qs
    parsed = urlparse(redirect_url)
    code = parse_qs(parsed.query)["code"][0]

    # コードからトークンを交換
    auth_code = await provider.load_authorization_code(client, code)
    assert auth_code is not None, "C-4: 認証コードがロードされるべき"

    token = await provider.exchange_authorization_code(client, auth_code)
    assert token.expires_in == 86400, f"C-4: 有効期限は24h(86400s)であるべき: {token.expires_in}"
    assert token.expires_in != 86400 * 365, "C-4: 有効期限は1年ではないべき"

    print(f"✅ C-4: トークン有効期限 — {token.expires_in}s (24h) ✓")


# PURPOSE: Verify auth code reuse behaves correctly
@pytest.mark.asyncio
async def test_auth_code_reuse():
    """追加検証: 認証コードの再利用防止"""
    provider = HGKOAuthProvider("test_token")
    client = await provider.get_client("claude.ai")

    from mcp.server.auth.provider import AuthorizationParams
    from pydantic import AnyHttpUrl

    params = AuthorizationParams(
        client_id="claude.ai",
        redirect_uri=AnyHttpUrl("https://claude.ai/api/auth/callback"),
        state="test_state_2",
        scopes=["read"],
        code_challenge="test_challenge",
        code_challenge_method="S256",
        redirect_uri_provided_explicitly=True,
    )

    redirect_url = await provider.authorize(client, params)
    from urllib.parse import urlparse, parse_qs
    parsed = urlparse(redirect_url)
    code = parse_qs(parsed.query)["code"][0]

    # 1回目: 成功
    auth_code = await provider.load_authorization_code(client, code)
    assert auth_code is not None
    await provider.exchange_authorization_code(client, auth_code)

    # 2回目: コード再利用 → 失敗すべき
    auth_code_reuse = await provider.load_authorization_code(client, code)
    assert auth_code_reuse is None, "認証コードの再利用は拒否されるべき"

    print("✅ 追加: 認証コード再利用防止 — 使用済みコードを拒否")


# PURPOSE: Verify refresh token rotation behaves correctly
@pytest.mark.asyncio
async def test_refresh_token_rotation():
    """追加検証: リフレッシュトークンのローテーション"""
    provider = HGKOAuthProvider("test_token")
    client = await provider.get_client("claude.ai")

    from mcp.server.auth.provider import AuthorizationParams
    from pydantic import AnyHttpUrl

    params = AuthorizationParams(
        client_id="claude.ai",
        redirect_uri=AnyHttpUrl("https://claude.ai/api/auth/callback"),
        state="test_rotation",
        scopes=["read"],
        code_challenge="test_challenge",
        code_challenge_method="S256",
        redirect_uri_provided_explicitly=True,
    )

    redirect_url = await provider.authorize(client, params)
    from urllib.parse import urlparse, parse_qs
    parsed = urlparse(redirect_url)
    code = parse_qs(parsed.query)["code"][0]

    auth_code = await provider.load_authorization_code(client, code)
    token1 = await provider.exchange_authorization_code(client, auth_code)

    # Refresh
    rt = await provider.load_refresh_token(client, token1.refresh_token)
    assert rt is not None
    token2 = await provider.exchange_refresh_token(client, rt, ["read"])

    # 古いリフレッシュトークンは無効化されるべき
    old_rt = await provider.load_refresh_token(client, token1.refresh_token)
    assert old_rt is None, "リフレッシュ後、旧トークンは無効化されるべき"

    # 新しいリフレッシュトークンは有効
    new_rt = await provider.load_refresh_token(client, token2.refresh_token)
    assert new_rt is not None, "新リフレッシュトークンは有効であるべき"

    print("✅ 追加: リフレッシュトークン・ローテーション — 旧トークン無効化確認")


# PURPOSE: Verify CCL execute size limits
def test_ccl_execute_size_limit():
    """C-5: hgk_ccl_execute のサイズ制限テスト"""
    # CCL 式が 500 文字を超える場合
    long_ccl = "a" * 501
    result = hgk_ccl_execute(long_ccl)
    assert "最大 500 文字" in result, f"CCL サイズ制限が効いていない: {result}"

    # Context が 2000 文字を超える場合
    result = hgk_ccl_execute("/noe+", context="x" * 2001)
    assert "最大 2000 文字" in result, f"Context サイズ制限が効いていない: {result}"

    print("✅ C-5: hgk_ccl_execute サイズ制限 — 正常拒否")


# PURPOSE: Verify paper search size limits
def test_paper_search_size_limit():
    """C-6: hgk_paper_search のサイズ制限テスト"""
    # クエリが 200 文字を超える場合
    long_query = "a" * 201
    result = hgk_paper_search(long_query)
    assert "最大 200 文字" in result, f"クエリサイズ制限が効いていない: {result}"

    print("✅ C-6: hgk_paper_search サイズ制限 — 正常拒否")


# PURPOSE: Verify digest run size limits
def test_digest_run_size_limit():
    """C-7: hgk_digest_run のサイズ制限テスト"""
    # トピックが 500 文字を超える場合
    long_topics = "a" * 501
    result = hgk_digest_run(topics=long_topics)
    assert "最大 500 文字" in result, f"トピックサイズ制限が効いていない: {result}"

    print("✅ C-7: hgk_digest_run サイズ制限 — 正常拒否")


# PURPOSE: Verify main behaves correctly
async def main():
    """Verify main behavior."""
    print("=" * 60)
    print("  L1 動的セキュリティテスト — hgk_gateway")
    print("=" * 60)
    print()

    passed = 0
    failed = 0

    tests = [
        ("C-1: フェイルセーフ", test_c1_failsafe),
        ("C-2: ホワイトリスト", test_c2_whitelist),
        ("C-3: サイズ制限", test_c3_size_limit),
        ("C-4: トークン有効期限", test_c4_token_expiry),
        ("追加: 認証コード再利用防止", test_auth_code_reuse),
        ("追加: リフレッシュトークン・ローテーション", test_refresh_token_rotation),
        ("C-5: CCL Execute サイズ制限", test_ccl_execute_size_limit),
        ("C-6: Paper Search サイズ制限", test_paper_search_size_limit),
        ("C-7: Digest Run サイズ制限", test_digest_run_size_limit),
    ]

    for name, test_fn in tests:
        try:
            result = test_fn()
            if asyncio.iscoroutine(result):
                await result
            passed += 1
        except Exception as e:
            print(f"❌ {name}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print()
    print("=" * 60)
    print(f"  結果: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
