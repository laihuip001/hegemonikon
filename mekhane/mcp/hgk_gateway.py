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
from datetime import datetime
from pathlib import Path
from typing import Any

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # hegemonikon/
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

# =============================================================================
# Configuration
# =============================================================================

GATEWAY_HOST = os.getenv("HGK_GATEWAY_HOST", "127.0.0.1")
GATEWAY_PORT = int(os.getenv("HGK_GATEWAY_PORT", "8765"))

# Allowed hosts for DNS rebinding protection
_default_hosts = "localhost,127.0.0.1,hegemonikon.tail3b6058.ts.net"
ALLOWED_HOSTS = os.getenv("HGK_GATEWAY_ALLOWED_HOSTS", _default_hosts).split(",")

# =============================================================================
# Gateway Server
# =============================================================================

mcp = FastMCP(
    "hgk-gateway",
    host=GATEWAY_HOST,
    port=GATEWAY_PORT,
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

@mcp.tool()
def hgk_idea_capture(idea: str, tags: str = "") -> str:
    """
    アイデアメモを保存する。外出先での閃きを逃さない。
    次回 /boot で自動的に読み込まれる。

    Args:
        idea: アイデアの内容
        tags: タグ (カンマ区切り、例: "FEP, 設計, 実験")
    """
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
    mcp.run(transport="streamable-http")
