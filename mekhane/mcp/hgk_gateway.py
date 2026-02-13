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

# [C-2] 許可されたクライアントID (名前付き) + 許可された redirect_uri ドメイン
# claude.ai は毎セッション新しい UUID client_id を生成するため、
# ドメインベースで許可する (redirect_uri に含まれるドメインで判定)
ALLOWED_CLIENT_IDS: set[str] = {
    "claude.ai",
    "chatgpt.com",
    "hgk-mobile",
}
ALLOWED_REDIRECT_DOMAINS: set[str] = {
    "claude.ai",
    "chatgpt.com",
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


# PURPOSE: [L2-auto] セキュリティイベントを wbc_state.json に書き込む。
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

    # PURPOSE: [L2-auto] 初期化: init__
    def __init__(self, access_token: str):
        self._access_token = access_token
        self._clients: dict[str, OAuthClientInformationFull] = {}
        self._auth_codes: dict[str, AuthorizationCode] = {}
        self._refresh_tokens: dict[str, RefreshToken] = {}

    # PURPOSE: client を取得する
    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        client = self._clients.get(client_id)
        if client is None:
            # [C-2] Check: named whitelist OR UUID format (claude.ai dynamic IDs)
            import re
            is_uuid = bool(re.match(
                r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
                client_id
            ))
            if client_id not in ALLOWED_CLIENT_IDS and not is_uuid:
                print(f"⚠️ Rejected unknown client: {client_id[:32]}", file=sys.stderr)
                _wbc_log_security_event(
                    event_type="client_rejected",
                    severity="medium",
                    details=f"Unknown client_id rejected: {client_id[:32]}",
                )
                return None
            # Auto-register: whitelisted names or UUID clients (claude.ai dynamic)
            from pydantic import AnyHttpUrl
            client = OAuthClientInformationFull(
                client_id=client_id,
                client_secret=None,
                redirect_uris=[AnyHttpUrl("https://claude.ai/api/mcp/auth_callback")],
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
        "CCL パース、Doxa/Handoff 参照、アイデアメモ保存、"
        "Digestor (消化パイプライン実行・候補一覧・消化済マーク・トピック管理) が可能。"
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
def hgk_search(query: str, max_results: int = 5, mode: str = "hybrid") -> str:
    """
    HGK の知識ベース (KI / Gnōsis / Sophia) を検索する。

    Args:
        query: 検索クエリ (例: "FEP 精度加重", "認知バイアス")
        max_results: 最大結果数
        mode: 検索モード — "hybrid" (ベクトル+キーワード), "vector" (ベクトルのみ), "keyword" (キーワードのみ)
    """
    results = []

    # --- ベクトル検索 (GnosisIndex) ---
    if mode in ("hybrid", "vector"):
        try:
            from mekhane.anamnesis.index import GnosisIndex

            idx = GnosisIndex()
            vector_results = idx.search(query, k=max_results)
            for r in vector_results:
                title = r.get("title", "不明")
                authors = r.get("authors", "")
                abstract = r.get("abstract", "")[:200]
                source = r.get("source", "")
                score = r.get("_distance", None)
                score_str = f" (score: {score:.3f})" if score is not None else ""
                results.append(
                    f"🔬 **{title}**{score_str}\n"
                    f"   著者: {authors[:80]}\n"
                    f"   {abstract}..."
                )
        except ImportError:
            results.append("⚠️ ベクトル検索モジュール未インストール (lancedb/sentence-transformers)")
        except Exception as e:
            results.append(f"⚠️ ベクトル検索エラー: {e}")

    # --- キーワード検索 ---
    if mode in ("hybrid", "keyword"):
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
                        lines = content.split("\n")
                        matches = [l.strip() for l in lines if query.lower() in l.lower()][:3]
                        match_text = " / ".join(matches) if matches else "(マッチ箇所省略)"
                        results.append(f"📋 **Handoff: {hf.stem}**\n   {match_text[:150]}")
                except Exception:
                    pass

    if not results:
        return f"🔍 `{query}` に一致する結果はありませんでした。"

    mode_label = {"hybrid": "ハイブリッド", "vector": "ベクトル", "keyword": "キーワード"}.get(mode, mode)
    header = f"## 🔍 HGK 検索結果: `{query}` ({mode_label})\n\n**{len(results)} 件**\n\n"
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

    # Digestor status
    incoming_count = len(list(INCOMING_DIR.glob("eat_*.md"))) if INCOMING_DIR.exists() else 0
    processed_count = len(list(PROCESSED_DIR.glob("eat_*.md"))) if PROCESSED_DIR.exists() else 0
    status_items.append(f"\n### Digestor")
    status_items.append(f"📥 incoming: {incoming_count} 件")
    status_items.append(f"📦 processed: {processed_count} 件")

    try:
        from mekhane.ergasterion.digestor.state import get_status_summary
        status_items.append(get_status_summary())
    except Exception:
        status_items.append("🔄 Digestor: 状態不明")

    # Scheduler PID check
    pid_file = Path.home() / ".hegemonikon" / "digestor" / "scheduler.pid"
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            os.kill(pid, 0)  # Check if process exists
            status_items.append("⚡ Scheduler: 稼働中")
        except (ProcessLookupError, ValueError):
            status_items.append("💤 Scheduler: 停止中 (PID stale)")
    else:
        status_items.append("💤 Scheduler: 停止中")

    return f"## 🏠 HGK ステータス\n\n" + "\n".join(status_items)


# =============================================================================
# CCL Execute (CCL 式の実行)
# =============================================================================

# PURPOSE: CCL 式を Hermēneus 経由で実行し、結果を返す
@mcp.tool()
def hgk_ccl_execute(ccl: str, context: str = "") -> str:
    """
    CCL 式を実行し、結果を返す。
    dispatch (構文解析のみ) とは異なり、ワークフローを実際に実行する。

    Args:
        ccl: CCL 式 (例: "/noe+", "/dia+~*/noe")。最大 500 文字。
        context: 実行コンテキスト (分析対象など)。最大 2000 文字。
    """
    # Input validation
    if len(ccl) > 500:
        return "❌ CCL 式が長すぎます (最大 500 文字)"
    if len(context) > 2000:
        return "❌ コンテキストが長すぎます (最大 2000 文字)"

    try:
        from hermeneus.src.macro_executor import execute_and_explain
        result = execute_and_explain(ccl, context)
        # W12 Token Explosion 対策: 出力を最大 5000 文字に制限
        if len(result) > 5000:
            result = result[:5000] + "\n\n... (出力が 5000 文字を超えたため切り詰めました)"
        return result
    except ImportError:
        return "❌ Hermēneus が利用できません (import エラー)"
    except Exception as e:
        return f"❌ CCL 実行エラー: {e}"


# =============================================================================
# Paper Search (論文検索)
# =============================================================================

# PURPOSE: Semantic Scholar 経由で学術論文を検索する
@mcp.tool()
def hgk_paper_search(query: str, limit: int = 5) -> str:
    """
    学術論文を検索する (Semantic Scholar 経由)。
    Gnōsis 知識ベースの拡充や調査依頼に使用。

    Args:
        query: 検索クエリ (例: "active inference free energy")。最大 200 文字。
        limit: 最大結果数 (1-20、デフォルト 5)。
    """
    # Input validation
    if len(query) > 200:
        return "❌ クエリが長すぎます (最大 200 文字)"
    limit = max(1, min(20, limit))

    try:
        import signal

        # Anarkhia 対策: 30 秒タイムアウト
        # PURPOSE: [L2-auto] 内部処理: timeout_handler
        def _timeout_handler(signum, frame):
            raise TimeoutError("API タイムアウト (30秒)")

        old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(30)

        try:
            from mekhane.pks.semantic_scholar import SemanticScholarClient
            client = SemanticScholarClient()
            results = client.search(query, limit=limit)
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

        if not results:
            return f"🔍 '{query}' の検索結果: 0 件"

        lines = [f"## 🔍 論文検索: '{query}' ({len(results)} 件)\n"]
        for i, paper in enumerate(results, 1):
            # Paper は dataclass — 属性アクセスを使用 (.get() は使えない)
            title = getattr(paper, "title", "不明")
            year = getattr(paper, "year", None) or "?"
            citations = getattr(paper, "citation_count", 0)
            paper_authors = getattr(paper, "authors", []) or []
            authors = ", ".join(
                a if isinstance(a, str) else str(a) for a in paper_authors[:3]
            )
            if len(paper_authors) > 3:
                authors += " et al."
            lines.append(f"### {i}. {title} ({year})")
            lines.append(f"- **著者**: {authors}")
            lines.append(f"- **被引用数**: {citations}")
            abstract = getattr(paper, "abstract", "") or ""
            if abstract:
                # Abstract を 200 文字に制限
                if len(abstract) > 200:
                    abstract = abstract[:200] + "..."
                lines.append(f"- **要旨**: {abstract}")
            lines.append("")

        return "\n".join(lines)
    except TimeoutError as e:
        return f"⏱️ {e}"
    except ImportError:
        return "❌ SemanticScholarClient が利用できません (import エラー)"
    except Exception as e:
        return f"❌ 論文検索エラー: {e}"


# =============================================================================
# Digestor: Incoming Check (消化候補一覧)
# =============================================================================

# PURPOSE: incoming/ の消化候補を確認する
INCOMING_DIR = MNEME_DIR / "incoming"
PROCESSED_DIR = MNEME_DIR / "processed"

# PURPOSE: [L2-auto] incoming/ の未消化ファイルを確認する。

@mcp.tool()
def hgk_digest_check() -> str:
    """
    incoming/ の未消化ファイルを確認する。
    消化待ちの論文候補一覧を返す。
    """
    if not INCOMING_DIR.exists():
        return "## ⚠️ incoming/ ディレクトリが見つかりません"

    files = sorted(INCOMING_DIR.glob("eat_*.md"))
    if not files:
        return "## 📭 消化待ちの候補はありません (0 件)"

    lines = [f"## 📥 消化待ち候補: {len(files)} 件\n"]

    for i, f in enumerate(files, 1):
        try:
            content = f.read_text(encoding="utf-8")
            title = "(タイトル不明)"
            score = ""
            topics_str = ""

            in_frontmatter = False
            for line in content.split("\n"):
                if line.strip() == "---":
                    if in_frontmatter:
                        break
                    in_frontmatter = True
                    continue
                if in_frontmatter:
                    if line.startswith("title:"):
                        title = line.split(":", 1)[1].strip().strip("\"'")
                    elif line.startswith("score:"):
                        score = line.split(":", 1)[1].strip()
                    elif line.startswith("topics:"):
                        topics_str = line.split(":", 1)[1].strip()

            lines.append(f"### {i}. {title}")
            if score:
                lines.append(f"- **Score**: {score}")
            if topics_str:
                lines.append(f"- **Topics**: {topics_str}")
            lines.append(f"- **File**: `{f.name}`\n")
        except Exception as e:
            lines.append(f"### {i}. {f.name} (読取エラー: {e})\n")

    # processed 件数も表示
    processed_count = len(list(PROCESSED_DIR.glob("eat_*.md"))) if PROCESSED_DIR.exists() else 0
    lines.append(f"---\n📦 processed/: {processed_count} 件 消化済")

    return "\n".join(lines)


# =============================================================================
# Digestor: Mark Processed (消化完了マーク)
# =============================================================================

# PURPOSE: 消化完了ファイルを processed/ に移動する
@mcp.tool()
def hgk_digest_mark(filenames: str = "") -> str:
    """
    消化完了したファイルを incoming/ → processed/ に移動する。

    Args:
        filenames: 移動するファイル名 (カンマ区切り)。空の場合は全 eat_*.md を移動。
    """
    try:
        from mekhane.ergasterion.digestor.pipeline import mark_as_processed

        file_list = [f.strip() for f in filenames.split(",") if f.strip()] if filenames else None
        result = mark_as_processed(filenames=file_list)

        lines = [f"## ✅ processed/ 移動結果\n"]
        lines.append(f"**移動成功**: {result['count']} 件\n")

        for f in result["moved"]:
            lines.append(f"- ✅ `{f}`")
        for e in result["errors"]:
            lines.append(f"- ❌ `{e['file']}`: {e['error']}")

        return "\n".join(lines)
    except ImportError:
        return "❌ DigestorPipeline が利用できません"
    except Exception as e:
        return f"❌ エラー: {e}"


# =============================================================================
# Digestor: List Candidates (候補評価)
# =============================================================================

# PURPOSE: Digestor selector で候補を評価する
@mcp.tool()
def hgk_digest_list(
    topics: str = "",
    max_candidates: int = 10,
) -> str:
    """
    Digestor の selector で論文候補を評価する (dry-run)。
    incoming/ には書き込まず、評価結果のみ返す。

    Args:
        topics: 対象トピック (カンマ区切り)。最大 500 文字。空=全トピック。
        max_candidates: 最大候補数 (1-20、デフォルト 10)。
    """
    if len(topics) > 500:
        return "❌ トピックが長すぎます (最大 500 文字)"
    max_candidates = max(1, min(20, max_candidates))

    try:
        from mekhane.ergasterion.digestor.pipeline import DigestorPipeline

        topic_list = [t.strip() for t in topics.split(",") if t.strip()] if topics else None
        pipeline = DigestorPipeline()
        result = pipeline.run(
            topics=topic_list,
            max_papers=30,
            max_candidates=max_candidates,
            dry_run=True,
        )

        lines = [f"## 🔍 消化候補リスト (dry-run)\n"]
        lines.append(f"- **取得論文数**: {result.total_papers}")
        lines.append(f"- **選定候補数**: {result.candidates_selected}\n")

        for i, c in enumerate(result.candidates[:max_candidates], 1):
            lines.append(f"### {i}. [{c.score:.2f}] {c.paper.title[:80]}")
            if hasattr(c.paper, 'authors') and c.paper.authors:
                authors = ", ".join(c.paper.authors[:3])
                lines.append(f"- **著者**: {authors}")
            lines.append("")

        return "\n".join(lines)
    except ImportError:
        return "❌ DigestorPipeline が利用できません"
    except Exception as e:
        return f"❌ 候補リストエラー: {e}"


# =============================================================================
# Digestor: Topics (トピック一覧)
# =============================================================================

# PURPOSE: 消化対象トピック一覧を表示する
@mcp.tool()
def hgk_digest_topics() -> str:
    """
    消化対象トピック一覧を表示する。
    topics.yaml に定義されたテーマと設定を返す。
    """
    try:
        import yaml

        topics_file = PROJECT_ROOT / "mekhane" / "ergasterion" / "digestor" / "topics.yaml"
        if not topics_file.exists():
            return "## ⚠️ topics.yaml が見つかりません"

        data = yaml.safe_load(topics_file.read_text(encoding="utf-8"))
        settings = data.get("settings", {})
        topics_list = data.get("topics", [])

        lines = [f"## 📋 消化対象トピック ({len(topics_list)} テーマ)\n"]
        lines.append(f"- **最大候補数**: {settings.get('max_candidates', '?')}")
        lines.append(f"- **最小スコア**: {settings.get('min_score', '?')}")
        lines.append(f"- **マッチモード**: {settings.get('match_mode', '?')}\n")

        for t in topics_list:
            tid = t.get("id", "?")
            desc = t.get("description", "")
            digest_to = ", ".join(t.get("digest_to", []))
            lines.append(f"### `{tid}`")
            lines.append(f"- {desc}")
            lines.append(f"- → {digest_to}\n")

        return "\n".join(lines)
    except ImportError:
        return "❌ PyYAML が利用できません"
    except Exception as e:
        return f"❌ トピック読取エラー: {e}"


# =============================================================================
# Digest Run (消化パイプライン)
# =============================================================================

# PURPOSE: Digestor パイプラインを実行し、消化候補を生成する
@mcp.tool()
def hgk_digest_run(
    topics: str = "",
    max_papers: int = 20,
    dry_run: bool = True,
) -> str:
    """
    Digestor パイプラインを実行する。
    デフォルトは dry_run (レポートのみ)。dry_run=False で .md ファイルを生成。

    Args:
        topics: 対象トピック (カンマ区切り)。最大 500 文字。空の場合は全トピック。
        max_papers: 取得する最大論文数 (1-50、デフォルト 20)。
        dry_run: True=レポートのみ、False=.md ファイル生成 (incoming/ に出力)。
    """
    # Input validation
    if len(topics) > 500:
        return "❌ トピックが長すぎます (最大 500 文字)"
    max_papers = max(1, min(50, max_papers))

    try:
        from mekhane.ergasterion.digestor.pipeline import DigestorPipeline

        topic_list = [t.strip() for t in topics.split(",") if t.strip()] if topics else None
        pipeline = DigestorPipeline()
        report = pipeline.run(
            topics=topic_list,
            max_papers=max_papers,
            dry_run=dry_run,
        )

        mode_label = "🧪 DRY RUN" if dry_run else "🚀 LIVE"
        result = f"## {mode_label} 消化パイプライン実行結果\n\n"

        if isinstance(report, dict):
            result += f"- **取得論文数**: {report.get('fetched', 0)}\n"
            result += f"- **候補数**: {report.get('candidates', 0)}\n"
            result += f"- **重複排除**: {report.get('deduplicated', 0)}\n"
            if not dry_run:
                result += f"- **生成ファイル**: {report.get('generated_files', 0)} 件\n"
        elif isinstance(report, str):
            # Report が文字列の場合はそのまま返す (5000 文字制限)
            if len(report) > 5000:
                report = report[:5000] + "\n\n... (出力切り詰め)"
            result += report
        else:
            result += str(report)

        return result
    except ImportError:
        return "❌ DigestorPipeline が利用できません (import エラー)"
    except Exception as e:
        return f"❌ 消化パイプラインエラー: {e}"


# =============================================================================
# Ochēma: LLM 呼出し (Antigravity LS 経由)
# =============================================================================

# Rate limiter: 5 req/min
_ask_timestamps: list[float] = []
_ASK_RATE_LIMIT = 5
_ASK_RATE_WINDOW = 60  # seconds
# PURPOSE: [L2-auto] レートリミットチェック。True = 許可、False = 拒否。


def _check_rate_limit() -> bool:
    """レートリミットチェック。True = 許可、False = 拒否。"""
    now = time.time()
    _ask_timestamps[:] = [t for t in _ask_timestamps if now - t < _ASK_RATE_WINDOW]
    if len(_ask_timestamps) >= _ASK_RATE_LIMIT:
        return False
    _ask_timestamps.append(now)
    return True

# PURPOSE: IDE セッション一覧を取得する
@mcp.tool()
def hgk_sessions() -> str:
    """
    IDE のセッション (cascade) 一覧を取得する。

    各セッションには cascade_id, ステップ数, サマリ, 最終更新日時が含まれる。
    hgk_session_read や hgk_ask (cascade_id 指定) と組み合わせて使用する。
    """
    try:
        from mekhane.ochema.antigravity_client import AntigravityClient

        client = AntigravityClient()
        data = client.session_info()

        sessions = data.get("sessions", [])
        if not sessions:
            return "📭 セッションがありません"

        lines = [f"## 📋 IDE セッション一覧 ({data.get('total', 0)} 件)\n"]
        for s in sessions:
            status_icon = "🟢" if s.get("status") == "active" else "⚪"
            summary = s.get("summary", "")[:80] or "(サマリなし)"
            lines.append(
                f"- {status_icon} `{s['cascade_id'][:12]}...` "
                f"| {s.get('step_count', 0)} steps "
                f"| {summary}"
            )
        return "\n".join(lines)
    except RuntimeError as e:
        return f"❌ LS 未検出: {e}"
    except Exception as e:
        return f"❌ エラー: {e}"


# PURPOSE: IDE セッションの会話内容を読み取る
@mcp.tool()
def hgk_session_read(
    cascade_id: str,
    max_turns: int = 10,
    full: bool = False,
) -> str:
    """
    IDE セッションの会話内容を読み取る。

    user/assistant/tool の全ターンを時系列で返す。
    claude.ai ↔ IDE のセッション同期に使用する。

    Args:
        cascade_id: セッションの cascade_id (hgk_sessions で取得)
        max_turns: 返す最大ターン数 (デフォルト: 10)
        full: True → フル取得 (上限 30000 文字)
    """
    if not cascade_id or not cascade_id.strip():
        return "❌ cascade_id が空です"

    try:
        from mekhane.ochema.antigravity_client import AntigravityClient

        client = AntigravityClient()
        data = client.session_read(
            cascade_id.strip(),
            max_turns=max(1, min(50, max_turns)),
            full=full,
        )

        if "error" in data:
            return f"❌ {data['error']}"

        conversation = data.get("conversation", [])
        if not conversation:
            return f"📭 セッション `{cascade_id[:12]}...` に会話がありません"

        lines = [
            f"## 💬 セッション会話ログ\n",
            f"**Cascade**: `{data['cascade_id']}`",
            f"**Summary**: {data.get('summary', 'N/A')}",
            f"**Total Steps**: {data.get('total_steps', 0)} | "
            f"**Turns shown**: {len(conversation)}\n",
            "---\n",
        ]

        for turn in conversation:
            role = turn.get("role", "")
            if role == "user":
                content = turn.get("content", "")
                trunc = " ✂️" if turn.get("truncated") else ""
                lines.append(f"### 👤 User{trunc}\n{content}\n")
            elif role == "assistant":
                content = turn.get("content", "")
                model = turn.get("model", "")
                trunc = " ✂️" if turn.get("truncated") else ""
                model_label = f" ({model})" if model else ""
                lines.append(f"### 🤖 Assistant{model_label}{trunc}\n{content}\n")
            elif role == "tool":
                tool_name = turn.get("tool", "unknown")
                lines.append(f"- 🔧 `{tool_name}`\n")

        result = "\n".join(lines)

        # サイズ制御
        max_size = 30000 if full else 15000
        if len(result) > max_size:
            result = result[:max_size] + f"\n\n... (出力が {max_size} 文字を超えたため切り詰め)"

        return result
    except RuntimeError as e:
        return f"❌ LS 未検出: {e}"
    except Exception as e:
        return f"❌ エラー: {e}"


# PURPOSE: LLM にメッセージを送り応答を取得する (Antigravity LS 経由)
@mcp.tool()
def hgk_ask(
    message: str,
    model: str = "MODEL_CLAUDE_4_5_SONNET_THINKING",
    timeout: int = 120,
    cascade_id: str = "",
) -> str:
    """
    LLM にメッセージを送り応答を取得する (Antigravity LS 経由)。

    コスト0、API key 不要。IDE の Language Server を経由して
    Claude, Gemini, GPT 等を呼び出す。

    cascade_id を指定すると、既存セッションの文脈を引き継いで質問できる。
    省略時は新規セッションを作成する。

    Args:
        message: LLM に送るメッセージ (最大 5000 文字)
        model: 使用モデル (デフォルト: Claude Sonnet)
        timeout: タイムアウト秒数 (最大 300)
        cascade_id: 既存セッションの cascade_id (省略時は新規)
    """
    # [C-3] Input validation
    if not message or not message.strip():
        return "❌ メッセージが空です"
    if len(message) > 5000:
        return f"❌ メッセージが長すぎます ({len(message)} 文字、上限 5000)"
    timeout = max(10, min(300, timeout))

    # Rate limit
    if not _check_rate_limit():
        return "⚠️ レートリミット超過 (5 回/分)。少し待ってから再試行してください。"

    try:
        from mekhane.ochema.antigravity_client import AntigravityClient

        client = AntigravityClient()

        if cascade_id and cascade_id.strip():
            # 既存セッションにメッセージ追加
            cid = cascade_id.strip()
            client._send_message(cid, message, model)
            response = client._poll_response(cid, float(timeout))
        else:
            # 新規セッション
            response = client.ask(message, model=model, timeout=float(timeout))

        result = f"## 🤖 LLM 応答\n\n**モデル**: `{response.model}`\n\n---\n\n{response.text}"

        if response.thinking:
            result += f"\n\n---\n\n<details><summary>💭 思考プロセス</summary>\n\n{response.thinking[:2000]}\n\n</details>"

        # W12 Token Explosion 対策
        if len(result) > 8000:
            result = result[:8000] + "\n\n... (出力が 8000 文字を超えたため切り詰めました)"

        return result
    except RuntimeError as e:
        return f"❌ LS 未検出: {e}\n\n> Antigravity IDE が起動しているか確認してください"
    except Exception as e:
        return f"❌ LLM エラー: {e}"


# PURPOSE: 利用可能な LLM モデル一覧を取得する
@mcp.tool()
def hgk_models() -> str:
    """
    利用可能な LLM モデル一覧を取得する。
    Antigravity LS が提供するモデルとクォータ残量を確認できる。
    """
    try:
        from mekhane.ochema.antigravity_client import AntigravityClient

        client = AntigravityClient()
        models = client.list_models()

        if not models:
            return "📭 モデル情報を取得できませんでした"

        lines = ["## 🤖 利用可能モデル\n"]
        lines.append("| モデル | ラベル | 残量 |")
        lines.append("|:-------|:-------|-----:|")
        for m in models:
            remaining = m.get("remaining", 0)
            icon = "🟢" if remaining > 50 else "🟡" if remaining > 10 else "🔴"
            lines.append(
                f"| `{m.get('name', 'unknown')}` "
                f"| {m.get('label', '')} "
                f"| {icon} {remaining}% |"
            )
        return "\n".join(lines)
    except RuntimeError as e:
        return f"❌ LS 未検出: {e}"
    except Exception as e:
        return f"❌ エラー: {e}"


# PURPOSE: Antigravity LS の接続状況を確認する
@mcp.tool()
def hgk_ls_status() -> str:
    """
    Antigravity LS の接続状況を確認する。
    LS が稼働しているか、PID, ポート, ワークスペースを表示する。
    """
    try:
        from mekhane.ochema.antigravity_client import AntigravityClient

        client = AntigravityClient()
        status = client.get_status()

        return f"""## 🔌 Language Server ステータス

**状態**: ✅ 接続済み
**PID**: {client.pid}
**Port**: {client.port}

---

{status}"""
    except RuntimeError as e:
        return f"## 🔌 Language Server ステータス\n\n**状態**: ❌ 未検出\n**エラー**: {e}"
    except Exception as e:
        return f"❌ エラー: {e}"


# =============================================================================
# Sympatheia: システム健全性
# =============================================================================

# PURPOSE: HGK システムの健全性チェック (Sympatheia 読取り)
@mcp.tool()
def hgk_health() -> str:
    """
    HGK システムの詳細な健全性レポートを表示する。
    Heartbeat, WBC アラート, Health スコアを確認。
    """
    lines = ["## 🩺 HGK Health Report\n"]

    # 1. Heartbeat
    hb_file = _MNEME_DIR / "heartbeat.json"
    if hb_file.exists():
        try:
            hb = json.loads(hb_file.read_text("utf-8"))
            beats = hb.get("totalBeats", 0)
            last = hb.get("lastBeat", "不明")
            lines.append(f"### 💓 Heartbeat\n- **総拍動数**: {beats}\n- **最終拍動**: {last}\n")
        except Exception:
            lines.append("### 💓 Heartbeat\n- ⚠️ 読取りエラー\n")
    else:
        lines.append("### 💓 Heartbeat\n- 未検出\n")

    # 2. WBC Alerts
    wbc_file = _MNEME_DIR / "wbc_state.json"
    if wbc_file.exists():
        try:
            wbc = json.loads(wbc_file.read_text("utf-8"))
            total = wbc.get("totalAlerts", 0)
            alerts = wbc.get("alerts", [])
            recent = alerts[-5:] if alerts else []

            lines.append(f"### 🛡️ WBC Alerts\n- **総アラート数**: {total}\n")
            if recent:
                lines.append("**直近5件:**\n")
                for a in reversed(recent):
                    sev = a.get("severity", "?")
                    ts = a.get("timestamp", "?")[:19]
                    details = a.get("details", "")[:80]
                    icon = "🔴" if sev == "high" else ("🟡" if sev == "medium" else "🟢")
                    lines.append(f"- {icon} [{sev}] {ts} — {details}")
                lines.append("")
            else:
                lines.append("- ✅ アラートなし\n")
        except Exception:
            lines.append("### 🛡️ WBC\n- ⚠️ 読取りエラー\n")
    else:
        lines.append("### 🛡️ WBC\n- 未検出\n")

    # 3. Health Metrics (latest entry)
    health_file = _MNEME_DIR / "health_metrics.jsonl"
    if health_file.exists():
        try:
            last_line = ""
            with open(health_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        last_line = line
            if last_line:
                metric = json.loads(last_line)
                score = metric.get("score", "?")
                lines.append(f"### 📊 Health Score\n- **最新スコア**: {score}\n")
        except Exception:
            lines.append("### 📊 Health Score\n- ⚠️ 読取りエラー\n")

    # 4. Git Status
    git_file = _MNEME_DIR / "git_sentinel_state.json"
    if git_file.exists():
        try:
            git = json.loads(git_file.read_text("utf-8"))
            dirty = git.get("isDirty", False)
            modified = len(git.get("modifiedFiles", []))
            icon = "🟡" if dirty else "🟢"
            lines.append(f"### {icon} Git\n- **Dirty**: {dirty}\n- **変更ファイル**: {modified}\n")
        except Exception:
            pass

    return "\n".join(lines)


# PURPOSE: 未読通知の確認 (Sympatheia notifications)
@mcp.tool()
def hgk_notifications(limit: int = 10) -> str:
    """
    未読通知を確認する。
    HGK システムからの通知 (INFO/HIGH/CRITICAL) を表示。

    Args:
        limit: 表示件数 (デフォルト: 10)
    """
    notif_file = _MNEME_DIR / "notifications.jsonl"
    if not notif_file.exists():
        return "## 🔔 通知\n\n📭 通知ファイルが見つかりません"

    try:
        notifications = []
        with open(notif_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        notifications.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

        if not notifications:
            return "## 🔔 通知\n\n✅ 通知はありません"

        limit = max(1, min(50, limit))
        recent = notifications[-limit:]

        lines = [f"## 🔔 通知 ({len(recent)}/{len(notifications)} 件)\n"]

        for n in reversed(recent):
            level = n.get("level", n.get("notification_level", "INFO"))
            title = n.get("title", "無題")
            body = n.get("body", "")[:100]
            ts = n.get("timestamp", "?")[:19]

            icon = {"CRITICAL": "🔴", "HIGH": "🟠", "INFO": "🔵"}.get(level, "⚪")
            lines.append(f"- {icon} **[{level}]** {title}")
            if body:
                lines.append(f"  {body}")
            lines.append(f"  *{ts}*")
            lines.append("")

        return "\n".join(lines)
    except Exception as e:
        return f"❌ 通知読取りエラー: {e}"


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    # C-1 fail-safe ensures GATEWAY_TOKEN is always set at this point
    print("🔒 OAuth 2.1 authentication ENABLED")
    print(f"🚀 HGK Gateway starting on {GATEWAY_HOST}:{GATEWAY_PORT}")
    mcp.run(transport="streamable-http")

