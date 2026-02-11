#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/mcp/ 出張 HGK MCP Gateway
"""
出張 HGK MCP Gateway — モバイルからの HGK アクセス

FastMCP + Streamable HTTP で、Claude/ChatGPT のモバイルアプリから
MCP 経由で HGK の認知機能にアクセスするリモートサーバー。

Usage:
    # ローカル起動 (開発)
    python -m mekhane.mcp.hgk_gateway

    # Tailscale Funnel で公開
    tailscale funnel 8765
    python -m mekhane.mcp.hgk_gateway

Architecture:
    [スマホ Claude/ChatGPT] → MCP (Streamable HTTP) → [このサーバー] → [HGK モジュール]
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # hegemonikon/
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from mcp.server.auth.provider import (
    OAuthAuthorizationServerProvider,
    AuthorizationParams,
    AuthorizationCode,
    RefreshToken,
    AccessToken,
    construct_redirect_uri,
)
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken

# =============================================================================
# Configuration
# =============================================================================

GATEWAY_HOST = os.getenv("HGK_GATEWAY_HOST", "127.0.0.1")
GATEWAY_PORT = int(os.getenv("HGK_GATEWAY_PORT", "8765"))

# Bearer Token for OAuth access token (generated once, used as the access token)
GATEWAY_TOKEN = os.getenv("HGK_GATEWAY_TOKEN", "")

# [C-1] Fail-safe: TOKEN 未設定時はサーバー起動拒否
if not GATEWAY_TOKEN:
    print("❌ FATAL: HGK_GATEWAY_TOKEN is not set. Refusing to start.", file=sys.stderr)
    print("   Set HGK_GATEWAY_TOKEN in .env or environment.", file=sys.stderr)
    sys.exit(1)

# [C-2] 許可されたクライアントIDのホワイトリスト
ALLOWED_CLIENT_IDS: set[str] = {
    "claude.ai",
    "chatgpt.com",
    "hgk-mobile",
}

# Allowed hosts for DNS rebinding protection
_default_hosts = (
    "localhost,localhost:8765,"
    "127.0.0.1,127.0.0.1:8765,"
    "hegemonikon.tail3b6058.ts.net"
)
ALLOWED_HOSTS = os.getenv("HGK_GATEWAY_ALLOWED_HOSTS", _default_hosts).split(",")


# =============================================================================
# [L2] WBC Security Event Logger — Sympatheia 統合
# =============================================================================

# Mneme パス（Sympatheia と共有）
_MNEME_DIR = Path(os.getenv("HGK_MNEME", str(Path.home() / "oikos/mneme/.hegemonikon")))


def _wbc_log_security_event(
    event_type: str,
    severity: str,
    details: str,
    source: str = "hgk_gateway",
) -> None:
    """セキュリティイベントを wbc_state.json に書き込む。

    Sympatheia WBC と同じフォーマットでアラートを追加し、
    /boot 時の sympatheia_status で検知される。
    """
    import json
    from datetime import datetime, timezone

    wbc_file = _MNEME_DIR / "wbc_state.json"
    try:
        _MNEME_DIR.mkdir(parents=True, exist_ok=True)
        if wbc_file.exists():
            state = json.loads(wbc_file.read_text("utf-8"))
        else:
            state = {"alerts": [], "totalAlerts": 0}

        alert = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": source,
            "severity": severity,
            "eventType": event_type,
            "details": details,
            "threatScore": 5 if severity == "medium" else (10 if severity == "high" else 2),
        }
        state["alerts"].append(alert)
        state["totalAlerts"] = state.get("totalAlerts", 0) + 1

        # 直近100件のみ保持
        state["alerts"] = state["alerts"][-100:]

        wbc_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"⚠️ WBC log failed: {e}", file=sys.stderr)


# =============================================================================
# OAuth 2.1 Provider (auto-approve, single-user)
# =============================================================================

# PURPOSE: の統一的インターフェースを実現する
class HGKOAuthProvider(OAuthAuthorizationServerProvider[AuthorizationCode, RefreshToken, AccessToken]):
    """
    最小 OAuth 2.1 プロバイダー。
    - claude.ai Connector 用の /authorize → /token フローを処理
    - 認証コードを自動承認 (単一ユーザー、GATEWAY_TOKEN で保護)
    - インメモリストレージ
    """

    def __init__(self, access_token: str):
        self._access_token = access_token
        self._clients: dict[str, OAuthClientInformationFull] = {}
        self._auth_codes: dict[str, AuthorizationCode] = {}
        self._refresh_tokens: dict[str, RefreshToken] = {}

    # PURPOSE: client を取得する
    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        client = self._clients.get(client_id)
        if client is None:
            # [C-2] Only allow whitelisted clients
            if client_id not in ALLOWED_CLIENT_IDS:
                print(f"⚠️ Rejected unknown client: {client_id[:32]}", file=sys.stderr)
                _wbc_log_security_event(
                    event_type="client_rejected",
                    severity="medium",
                    details=f"Unknown client_id rejected: {client_id[:32]}",
                )
                return None
            # Auto-register whitelisted clients (claude.ai skips /register)
            from pydantic import AnyHttpUrl
            client = OAuthClientInformationFull(
                client_id=client_id,
                client_secret=None,
                redirect_uris=[AnyHttpUrl("https://claude.ai/api/auth/callback")],
                client_name=f"auto-{client_id[:16]}",
                grant_types=["authorization_code", "refresh_token"],
                response_types=["code"],
                token_endpoint_auth_method="none",
            )
            self._clients[client_id] = client
        return client

    # PURPOSE: client を登録する
    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        self._clients[client_info.client_id] = client_info

    # PURPOSE: hgk_gateway の authorize 処理を実行する
    async def authorize(
        self, client: OAuthClientInformationFull, params: AuthorizationParams
    ) -> str:
        """Auto-approve: 認証コードを即発行し redirect_uri にリダイレクト。"""
        import secrets
        # Dynamically add redirect_uri to client's registered URIs
        if client.redirect_uris is None:
            client.redirect_uris = [params.redirect_uri]
        elif params.redirect_uri not in client.redirect_uris:
            client.redirect_uris.append(params.redirect_uri)
        code = secrets.token_urlsafe(32)
        self._auth_codes[code] = AuthorizationCode(
            code=code,
            scopes=params.scopes or [],
            expires_at=time.time() + 600,  # 10 min
            client_id=client.client_id,
            code_challenge=params.code_challenge,
            redirect_uri=params.redirect_uri,
            redirect_uri_provided_explicitly=params.redirect_uri_provided_explicitly,
        )
        return construct_redirect_uri(
            str(params.redirect_uri),
            code=code,
            state=params.state,
        )

    # PURPOSE: authorization code を読み込む
    async def load_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: str
    ) -> AuthorizationCode | None:
        ac = self._auth_codes.get(authorization_code)
        if ac and ac.client_id == client.client_id and ac.expires_at > time.time():
            return ac
        return None

    # PURPOSE: hgk_gateway の exchange authorization code 処理を実行する
    async def exchange_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: AuthorizationCode
    ) -> OAuthToken:
        """認証コード → アクセストークン交換。固定トークンを返す。"""
        self._auth_codes.pop(authorization_code.code, None)
        import secrets
        refresh = secrets.token_urlsafe(32)
        self._refresh_tokens[refresh] = RefreshToken(
            token=refresh,
            client_id=client.client_id,
            scopes=authorization_code.scopes,
        )
        return OAuthToken(
            access_token=self._access_token,
            token_type="bearer",
            expires_in=86400,  # [C-4] 24 hours (was 1 year)
            refresh_token=refresh,
            scope=" ".join(authorization_code.scopes) if authorization_code.scopes else None,
        )

    # PURPOSE: refresh token を読み込む
    async def load_refresh_token(
        self, client: OAuthClientInformationFull, refresh_token: str
    ) -> RefreshToken | None:
        rt = self._refresh_tokens.get(refresh_token)
        if rt and rt.client_id == client.client_id:
            return rt
        return None

    # PURPOSE: hgk_gateway の exchange refresh token 処理を実行する
    async def exchange_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: RefreshToken,
        scopes: list[str],
    ) -> OAuthToken:
        import secrets
        new_refresh = secrets.token_urlsafe(32)
        self._refresh_tokens.pop(refresh_token.token, None)
        self._refresh_tokens[new_refresh] = RefreshToken(
            token=new_refresh,
            client_id=client.client_id,
            scopes=scopes or refresh_token.scopes,
        )
        return OAuthToken(
            access_token=self._access_token,
            token_type="bearer",
            expires_in=86400,  # [C-4] 24 hours
            refresh_token=new_refresh,
            scope=" ".join(scopes) if scopes else None,
        )

    # PURPOSE: access token を読み込む
    async def load_access_token(self, token: str) -> AccessToken | None:
        if token == self._access_token:
            return AccessToken(
                token=token,
                client_id="hgk",
                scopes=[],
            )
        # [L2] Invalid token → WBC alert
        _wbc_log_security_event(
            event_type="invalid_token",
            severity="high",
            details=f"Invalid access token attempt (prefix: {token[:8]}...)",
        )
        return None

    # PURPOSE: hgk_gateway の revoke token 処理を実行する
    async def revoke_token(self, token: AccessToken | RefreshToken) -> None:
        if isinstance(token, RefreshToken):
            self._refresh_tokens.pop(token.token, None)


# =============================================================================
# Gateway Server
# =============================================================================

from mcp.server.auth.settings import AuthSettings, ClientRegistrationOptions

_GATEWAY_URL = "https://hegemonikon.tail3b6058.ts.net"

_oauth_provider = HGKOAuthProvider(GATEWAY_TOKEN) if GATEWAY_TOKEN else None
_auth_settings = AuthSettings(
    issuer_url=_GATEWAY_URL,
    resource_server_url=_GATEWAY_URL,
    client_registration_options=ClientRegistrationOptions(enabled=True),
) if GATEWAY_TOKEN else None

mcp = FastMCP(
    "hgk-gateway",
    host=GATEWAY_HOST,
    port=GATEWAY_PORT,
    auth_server_provider=_oauth_provider,
    auth=_auth_settings,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=ALLOWED_HOSTS,
    ),
    instructions=(
        "Hegemonikón 出張 MCP Gateway。"
        "モバイルから HGK の認知機能にアクセスする。"
        "/sop 調査依頼書の生成、KI/Gnōsis 検索、"
        "CCL パース、Doxa/Handoff 参照、アイデアメモ保存が可能。"
    ),
)

# Paths
MNEME_DIR = PROJECT_ROOT.parent / "mneme" / ".hegemonikon"
SESSIONS_DIR = MNEME_DIR / "sessions"
DOXA_DIR = MNEME_DIR / "doxa"
SOP_OUTPUT_DIR = MNEME_DIR / "workflows"
IDEA_DIR = MNEME_DIR / "ideas"


# =============================================================================
# P1: /sop 調査依頼書テンプレート生成
# =============================================================================

# PURPOSE: hgk_gateway の hgk sop generate 処理を実行する
@mcp.tool()
def hgk_sop_generate(
    topic: str,
    decision: str = "",
    hypothesis: str = "",
) -> str:
    """
    /sop 調査依頼書テンプレートを生成する。

    Gemini Deep Research や Perplexity にコピペして使う。
    Hegemonikón /sop ワークフローのモバイル版。

    Args:
        topic: 調査対象のテーマ (例: "FEP と Active Inference の最新動向")
        decision: この調査の結果、何を決定するか
        hypothesis: 事前仮説 (あれば)
    """
    now = datetime.now().strftime("%Y-%m-%d")

    template = f"""# 調査依頼書（深掘り版）

> テーマ: {topic}
> 生成日: {now}
> 生成元: HGK /sop (出張版)

---

## 出力形式

以下の4列テーブルで構造化して回答してください：

| 項目 | 値 | 根拠（出典） | URL |
|:-----|:---|:-----------|:----|

---

## タスク定義

{topic}について、以下の論点を**網羅的かつ最新の情報**に基づいて調査してください。

## 時間制約

- **過去6ヶ月の情報を優先**
- 2025年以降の論文・記事を重視

## 決定事項

{decision if decision else "（調査結果に基づいて決定する）"}

## 仮説

{hypothesis if hypothesis else "（仮説なし — 探索的調査）"}

---

## 論点（必須項目）

A. {topic}の現状
- A1: 最新の定義・分類はどうなっているか？
- A2: 主要な研究グループ・実装は？
- A3: 2025年以降の重要な変化・ブレイクスルーは？

B. 実践・応用
- B1: 現時点で最も有効な手法・ツールは？
- B2: 成功事例と失敗事例は？
- B3: コスト・実装の現実的な制約は？

C. 将来展望
- C1: 今後6-12ヶ月で予想される変化は？
- C2: リスクや注意すべき点は？

---

> この調査依頼書は Hegemonikón /sop ワークフロー (出張版) で生成されました。
> Gemini Deep Research または Perplexity にコピペして実行してください。
"""

    # Save to file
    SOP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    safe_topic = topic[:30].replace("/", "_").replace(" ", "_")
    output_path = SOP_OUTPUT_DIR / f"sop_{safe_topic}_{now}.md"
    output_path.write_text(template, encoding="utf-8")

    return f"## ✅ 調査依頼書を生成しました\n\n保存先: `{output_path}`\n\n---\n\n{template}"


# =============================================================================
# P1: KI / Gnōsis 検索
# =============================================================================

# PURPOSE: hgk_gateway の hgk search 処理を実行する
@mcp.tool()
def hgk_search(query: str, max_results: int = 5) -> str:
    """
    HGK の知識ベース (KI / Gnōsis / Sophia) を検索する。

    Args:
        query: 検索クエリ (例: "FEP 精度加重", "認知バイアス")
        max_results: 最大結果数
    """
    results = []

    # 1. KI (Knowledge Items) — ファイル名検索
    ki_base = Path.home() / ".gemini" / "antigravity" / "knowledge"
    if ki_base.exists():
        ki_dirs = sorted(ki_base.iterdir())
        query_lower = query.lower()
        for ki_dir in ki_dirs:
            if ki_dir.is_dir():
                metadata_path = ki_dir / "metadata.json"
                if metadata_path.exists():
                    try:
                        meta = json.loads(metadata_path.read_text(encoding="utf-8"))
                        summary = meta.get("summary", "")
                        title = meta.get("title", ki_dir.name)
                        if query_lower in title.lower() or query_lower in summary.lower():
                            results.append(f"📚 **KI: {title}**\n   {summary[:150]}...")
                    except Exception:
                        pass

    # 2. Doxa (信念)
    if DOXA_DIR.exists():
        for doxa_file in sorted(DOXA_DIR.glob("*.json")):
            try:
                doxa = json.loads(doxa_file.read_text(encoding="utf-8"))
                content = json.dumps(doxa, ensure_ascii=False)
                if query.lower() in content.lower():
                    results.append(f"💡 **Doxa: {doxa_file.stem}**\n   {content[:150]}...")
            except Exception:
                pass

    # 3. Handoff — 最新3件を検索
    if SESSIONS_DIR.exists():
        handoffs = sorted(SESSIONS_DIR.glob("handoff_*.md"), reverse=True)[:3]
        for hf in handoffs:
            try:
                content = hf.read_text(encoding="utf-8")
                if query.lower() in content.lower():
                    # Find matching context
                    lines = content.split("\n")
                    matches = [l.strip() for l in lines if query.lower() in l.lower()][:3]
                    match_text = " / ".join(matches) if matches else "(マッチ箇所省略)"
                    results.append(f"📋 **Handoff: {hf.stem}**\n   {match_text[:150]}")
            except Exception:
                pass

    if not results:
        return f"🔍 `{query}` に一致する結果はありませんでした。\n\n> ヒント: ベクトル検索 (Gnōsis) は PC でのみ利用可能です。"

    header = f"## 🔍 HGK 検索結果: `{query}`\n\n**{len(results)} 件**\n\n"
    return header + "\n\n".join(results[:max_results])


# =============================================================================
# P2: CCL Dispatch
# =============================================================================

# PURPOSE: hgk_gateway の hgk ccl dispatch 処理を実行する
@mcp.tool()
def hgk_ccl_dispatch(ccl: str) -> str:
    """
    CCL (Cognitive Control Language) 式をパースし、構造を解析する。

    Args:
        ccl: CCL 式 (例: "/noe+", "/dia+~*/noe", "/sop")
    """
    try:
        from hermeneus.src.dispatch import dispatch

        result = dispatch(ccl)

        if not result["success"]:
            return f"## ❌ CCL パースエラー\n\n**CCL**: `{ccl}`\n**エラー**: {result['error']}"

        return f"""## ✅ CCL ディスパッチ結果

**CCL**: `{ccl}`

### AST 構造
```
{result['tree']}
```

### 関連ワークフロー
{', '.join(f'`{wf}`' for wf in result['workflows'])}

### 実行計画
{result['plan_template']}"""
    except Exception as e:
        return f"## ❌ エラー\n\n`{e}`"


# =============================================================================
# P2: Doxa 読み取り
# =============================================================================

# PURPOSE: hgk_gateway の hgk doxa read 処理を実行する
@mcp.tool()
def hgk_doxa_read() -> str:
    """
    Doxa (信念ストア) の内容を一覧表示する。
    HGK で蓄積された法則・教訓・信念を参照する。
    """
    if not DOXA_DIR.exists():
        return "## ⚠️ Doxa ディレクトリが見つかりません"

    doxa_files = sorted(DOXA_DIR.glob("*.json"))
    if not doxa_files:
        return "## 📭 Doxa は空です"

    lines = ["## 💡 Doxa (信念ストア)\n"]
    for df in doxa_files:
        try:
            data = json.loads(df.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for item in data:
                    strength = item.get("strength", "?")
                    text = item.get("text", item.get("law", str(item)))
                    lines.append(f"- **[{strength}]** {text}")
            elif isinstance(data, dict):
                for key, value in data.items():
                    lines.append(f"- **{key}**: {value}")
        except Exception:
            lines.append(f"- ⚠️ {df.name}: 読み取りエラー")

    return "\n".join(lines)


# =============================================================================
# P3: Handoff 参照
# =============================================================================

# PURPOSE: hgk_gateway の hgk handoff read 処理を実行する
@mcp.tool()
def hgk_handoff_read(count: int = 1) -> str:
    """
    最新の Handoff (セッション引き継ぎ書) を読む。
    前回のセッションで何をしたか、次に何をすべきかを確認する。

    Args:
        count: 読む Handoff の数 (デフォルト: 1)
    """
    if not SESSIONS_DIR.exists():
        return "## ⚠️ セッションディレクトリが見つかりません"

    handoffs = sorted(SESSIONS_DIR.glob("handoff_*.md"), reverse=True)
    if not handoffs:
        return "## 📭 Handoff がありません"

    lines = [f"## 📋 最新 Handoff ({min(count, len(handoffs))}/{len(handoffs)} 件)\n"]

    for hf in handoffs[:count]:
        try:
            content = hf.read_text(encoding="utf-8")
            # First 50 lines
            summary = "\n".join(content.split("\n")[:50])
            lines.append(f"### {hf.stem}\n\n{summary}\n\n---")
        except Exception:
            lines.append(f"### {hf.stem}\n\n⚠️ 読み取りエラー")

    return "\n".join(lines)


# =============================================================================
# P3: アイデアメモ保存
# =============================================================================

# PURPOSE: hgk_gateway の hgk idea capture 処理を実行する
@mcp.tool()
def hgk_idea_capture(idea: str, tags: str = "") -> str:
    """
    アイデアメモを保存する。外出先での閃きを逃さない。
    次回 /boot で自動的に読み込まれる。

    Args:
        idea: アイデアの内容 (最大10,000文字)
        tags: タグ (カンマ区切り、例: "FEP, 設計, 実験")
    """
    # [C-3] Content size limit
    MAX_IDEA_SIZE = 10_000
    if len(idea) > MAX_IDEA_SIZE:
        return f"❌ エラー: アイデアが長すぎます ({len(idea)} 文字)。上限は {MAX_IDEA_SIZE} 文字です。"
    IDEA_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    filename = f"idea_{now.strftime('%Y%m%d_%H%M%S')}.md"
    filepath = IDEA_DIR / filename

    content = f"""# 💡 アイデアメモ

> **日時**: {now.strftime('%Y-%m-%d %H:%M:%S')}
> **タグ**: {tags if tags else '未分類'}
> **ソース**: HGK 出張版 (モバイル)

---

{idea}

---

*Captured via HGK Gateway*
"""
    filepath.write_text(content, encoding="utf-8")

    return f"## ✅ アイデア保存完了\n\n保存先: `{filepath}`\nタグ: {tags if tags else '未分類'}\n\n次回 `/boot` で自動的に確認されます。"


# =============================================================================
# HGK Status (ヘルスチェック)
# =============================================================================

# PURPOSE: hgk_gateway の hgk status 処理を実行する
@mcp.tool()
def hgk_status() -> str:
    """
    HGK システムの概要ステータスを表示する。
    モバイルから現在の状態を確認する。
    """
    status_items = []

    # Handoff count
    handoff_count = len(list(SESSIONS_DIR.glob("handoff_*.md"))) if SESSIONS_DIR.exists() else 0
    status_items.append(f"📋 Handoff: {handoff_count} 件")

    # KI count
    ki_base = Path.home() / ".gemini" / "antigravity" / "knowledge"
    ki_count = len([d for d in ki_base.iterdir() if d.is_dir()]) if ki_base.exists() else 0
    status_items.append(f"📚 KI: {ki_count} 件")

    # Doxa count
    doxa_count = len(list(DOXA_DIR.glob("*.json"))) if DOXA_DIR.exists() else 0
    status_items.append(f"💡 Doxa: {doxa_count} 件")

    # Ideas count
    idea_count = len(list(IDEA_DIR.glob("*.md"))) if IDEA_DIR.exists() else 0
    status_items.append(f"🌟 Ideas: {idea_count} 件")

    # Latest handoff
    if SESSIONS_DIR.exists():
        handoffs = sorted(SESSIONS_DIR.glob("handoff_*.md"), reverse=True)
        if handoffs:
            status_items.append(f"📅 最新 Handoff: `{handoffs[0].name}`")

    return f"## 🏠 HGK ステータス\n\n" + "\n".join(status_items)


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    # C-1 fail-safe ensures GATEWAY_TOKEN is always set at this point
    print("🔒 OAuth 2.1 authentication ENABLED")
    print(f"🚀 HGK Gateway starting on {GATEWAY_HOST}:{GATEWAY_PORT}")
    mcp.run(transport="streamable-http")

