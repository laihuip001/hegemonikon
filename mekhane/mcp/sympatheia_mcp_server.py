#!/usr/bin/env python3
# PROOF: [L2/Sympatheia] <- mekhane/mcp/
# PURPOSE: Sympatheia MCP Server — 自律神経系への直接アクセス
"""
Sympatheia MCP Server

Claude が直接 Sympatheia 自律神経系を呼び出すための MCP サーバー。
mekhane/api/routes/sympatheia.py のロジックを MCP ツールとして公開。

Tools:
  - sympatheia_wbc: 脅威分析（白血球）
  - sympatheia_attractor: 定理推薦（反射弓）
  - sympatheia_digest: 記憶圧縮（週次集約）
  - sympatheia_feedback: 恒常性制御（閾値調整）
  - sympatheia_notifications: 通知 CRUD
  - sympatheia_status: 全 state ファイルのサマリ

Resources:
  - sympatheia://heartbeat — heartbeat.json
  - sympatheia://wbc — wbc_state.json
  - sympatheia://config — sympatheia_config.json
  - sympatheia://notifications — notifications.jsonl (最新 20 件)
  - sympatheia://digest — weekly_digest.json

CRITICAL: stdout は JSON-RPC 専用。ログは stderr に出力。
"""

import sys
import os
import io

if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

_original_stdout = sys.stdout


# PURPOSE: sympatheia_mcp_server の log 処理を実行する
def log(msg):
    print(f"[sympatheia-mcp] {msg}", file=sys.stderr, flush=True)


log("Starting Sympatheia MCP Server...")

# ============ Import path setup ============
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]  # hegemonikon/
sys.path.insert(0, str(_PROJECT_ROOT))
log(f"Project root: {_PROJECT_ROOT}")


# PURPOSE: StdoutSuppressor の機能を提供する
class StdoutSuppressor:
    def __init__(self):
        self._null = io.StringIO()
        self._old = None

    def __enter__(self):
        self._old = sys.stdout
        sys.stdout = self._null
        return self

    def __exit__(self, *args):
        sys.stdout = self._old


# ============ MCP SDK ============
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent, Resource
    log("MCP imports OK")
except Exception as e:
    log(f"MCP import error: {e}")
    sys.exit(1)

import json as _json


# ============ Sympatheia imports (lazy) ============
_sympatheia = None


def _get_sympatheia():
    """sympatheia.py のヘルパー関数群を安全にインポート。"""
    global _sympatheia
    if _sympatheia is None:
        try:
            with StdoutSuppressor():
                from mekhane.api.routes import sympatheia
            _sympatheia = sympatheia
            log("Sympatheia module loaded")
        except Exception as e:
            log(f"Sympatheia import error: {e}")
    return _sympatheia


# ============ MCP Server ============
server = Server(
    name="sympatheia",
    version="1.0.0",
    instructions=(
        "Sympatheia 自律神経系。脅威分析(WBC)、定理推薦(Attractor)、"
        "記憶圧縮(Digest)、恒常性(Feedback)、ルーティング(Route)を提供。"
    ),
)
log("Server initialized")


# ============ Resources ============
_MNEME = Path(os.getenv("HGK_MNEME", str(Path.home() / "oikos/mneme/.hegemonikon")))

_RESOURCES = {
    "sympatheia://heartbeat": ("heartbeat.json", "Heartbeat state — beats, healthy, lastBeat"),
    "sympatheia://wbc": ("wbc_state.json", "WBC state — alerts, totalAlerts, lastEscalation"),
    "sympatheia://config": ("sympatheia_config.json", "Sympatheia config — thresholds, sensitivity"),
    "sympatheia://notifications": ("notifications.jsonl", "Notification log — 最新 20 件"),
    "sympatheia://digest": ("weekly_digest.json", "Weekly digest — 最新の週次集約"),
    "sympatheia://attractor": ("attractor_dispatch.json", "Attractor dispatch history"),
}


# PURPOSE: sympatheia_mcp_server の list resources 処理を実行する
@server.list_resources()
async def list_resources():
    """公開リソース一覧。"""
    resources = []
    for uri, (filename, desc) in _RESOURCES.items():
        resources.append(Resource(
            uri=uri,
            name=filename,
            description=desc,
            mimeType="application/json",
        ))
    return resources


# PURPOSE: sympatheia_mcp_server の read resource 処理を実行する
@server.read_resource()
async def read_resource(uri: str):
    """リソース読み取り。"""
    log(f"read_resource: {uri}")
    uri_str = str(uri)
    if uri_str not in _RESOURCES:
        return f"Unknown resource: {uri_str}"
    filename, _ = _RESOURCES[uri_str]
    fpath = _MNEME / filename
    try:
        raw = fpath.read_text("utf-8")
        if filename.endswith(".jsonl"):
            # JSONL: 最新 20 行を JSON array に変換
            lines = [l.strip() for l in raw.strip().split("\n") if l.strip()][-20:]
            lines.reverse()
            return "[" + ",".join(lines) + "]"
        return raw
    except FileNotFoundError:
        return f"{{}}"
    except Exception as e:
        return f"Error reading {filename}: {e}"


# ============ Tools ============

# PURPOSE: sympatheia_mcp_server の list tools 処理を実行する
@server.list_tools()
async def list_tools():
    """利用可能なツール一覧。"""
    return [
        Tool(
            name="sympatheia_wbc",
            description=(
                "白血球 (WBC): ファイル変更や異常にスコアリングして脅威レベルを判定する。"
                "SACRED_TRUTH.md 変更時は threatScore=15。CRITICAL/HIGH ならエスカレーション。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {"type": "string", "description": "アラート発生元 (e.g. WF-08, manual)", "default": "claude"},
                    "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"], "default": "medium"},
                    "details": {"type": "string", "description": "何が起きたかの説明"},
                    "files": {"type": "array", "items": {"type": "string"}, "description": "関連ファイルパス", "default": []},
                },
                "required": ["details"],
            },
        ),
        Tool(
            name="sympatheia_attractor",
            description=(
                "定理推薦 (Attractor): 入力テキストから最適な Hegemonikón 定理とワークフローを推薦する。"
                "TF-IDF ベクトル類似度で 24 定理から選択。例: '理由を知りたい' → O3 Zētēsis /zet"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "context": {"type": "string", "description": "推薦対象のテキスト (ユーザー入力など)"},
                },
                "required": ["context"],
            },
        ),
        Tool(
            name="sympatheia_digest",
            description=(
                "記憶圧縮 (Digest): 全 Sympatheia state ファイルを集約して週次サマリを生成する。"
                "Heartbeat, FileMonitor, Git, WBC, Health, Sessions を統合。"
            ),
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="sympatheia_feedback",
            description=(
                "恒常性 (Feedback): 直近 3 日の Health スコアと WBC アラート頻度からシステム閾値を動的調整する。"
                "高スコア持続→感度向上、低スコア→感度低下、アラート過多→間隔延長。"
            ),
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="sympatheia_notifications",
            description=(
                "通知 CRUD: 未読通知の取得と新規通知の送信。"
                "action='list' で最新通知を取得、action='send' で通知を送信。"
                "/boot 時に CRITICAL 通知がないか確認するのに使う。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["list", "send"], "default": "list"},
                    "limit": {"type": "integer", "description": "取得件数 (list時)", "default": 10},
                    "level": {"type": "string", "description": "フィルタ: INFO|HIGH|CRITICAL (list時)"},
                    "source": {"type": "string", "description": "通知元 (send時)", "default": "claude"},
                    "title": {"type": "string", "description": "通知タイトル (send時)"},
                    "body": {"type": "string", "description": "通知本文 (send時)"},
                    "notification_level": {"type": "string", "enum": ["INFO", "HIGH", "CRITICAL"], "default": "INFO"},
                },
            },
        ),
        Tool(
            name="sympatheia_status",
            description=(
                "Sympatheia 全体ステータス: 全 state ファイルのサマリを一発で確認。"
                "Heartbeat beats, WBC alert count, Git dirty status, Config thresholds, 未読通知数を返す。"
                "セッション開始時 (/boot Phase 4.9) に呼ぶことを推奨。"
            ),
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


# PURPOSE: sympatheia_mcp_server の call tool 処理を実行する
@server.call_tool(validate_input=True)
async def call_tool(name: str, arguments: dict):
    """ツール実行。"""
    log(f"call_tool: {name}")
    sym = _get_sympatheia()
    if sym is None:
        return [TextContent(type="text", text="Error: Sympatheia module not available")]

    import json
    from datetime import datetime, timezone

    try:
        if name == "sympatheia_wbc":
            req = sym.WBCRequest(
                source=arguments.get("source", "claude"),
                severity=arguments.get("severity", "medium"),
                details=arguments.get("details", ""),
                files=arguments.get("files", []),
            )
            # call the sync logic directly (avoid async nesting issues)
            import asyncio
            result = await sym.wbc_analyze(req)
            d = result.model_dump()

            lines = [
                "# 🩸 WBC 脅威分析結果\n",
                f"- **Threat Score**: {d['threatScore']}/15",
                f"- **Level**: {d['level']}",
                f"- **Severity**: {d['severity']}",
                f"- **Source**: {d['source']}",
                f"- **Should Escalate**: {'🚨 YES' if d['shouldEscalate'] else 'No'}",
                f"- **Recent Alerts (1h)**: {d['recentAlertCount']}",
                f"- **Details**: {d['details']}",
                f"- **Files**: {', '.join(d['files']) or 'N/A'}",
            ]
            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "sympatheia_attractor":
            context = arguments.get("context", "")
            req = sym.AttractorRequest(context=context)
            result = await sym.attractor_dispatch(req)
            d = result.model_dump()

            if d["recommendation"]:
                r = d["recommendation"]
                lines = [
                    "# ⚡ Attractor 定理推薦\n",
                    f"- **Theorem**: {r['theorem']} ({r['name']})",
                    f"- **Series**: {r['series']}",
                    f"- **Command**: `{r['command']}`",
                    f"- **Confidence**: {r['confidence']:.1%}",
                    f"- **Auto-dispatch**: {'Yes' if d['autoDispatch'] else 'No'}",
                    f"\n> Input: {d['context']}",
                ]
            else:
                lines = [
                    "# ⚡ Attractor 定理推薦\n",
                    "引力圏外。定理レベルで収束しません。",
                    f"\n> Input: {d['context']}",
                ]
            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "sympatheia_digest":
            req = sym.DigestRequest()
            result = await sym.weekly_digest(req)
            d = result.model_dump()

            lines = [
                "# 📊 Weekly Digest\n",
                f"**Week ending**: {d['weekEnding']}\n",
                f"- **Heartbeat**: {d['heartbeat'].get('beats', 0)} beats",
                f"- **File Monitor**: {d['fileMon'].get('scans', 0)} scans, {d['fileMon'].get('changes', 0)} changes",
                f"- **Git**: branch={d['git'].get('branch')}, dirty={d['git'].get('dirty')}, {d['git'].get('changes', 0)} changes",
                f"- **WBC**: {d['wbc'].get('weekAlerts', 0)} alerts ({d['wbc'].get('criticals', 0)} critical, {d['wbc'].get('highs', 0)} high)",
                f"- **Health**: avg={d['health'].get('avg', 0)}, {d['health'].get('samples', 0)} samples",
                f"- **Sessions**: {d['sessions']}",
            ]
            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "sympatheia_feedback":
            req = sym.FeedbackRequest()
            result = await sym.feedback_loop(req)
            d = result.model_dump()

            lines = [
                "# ⚖️ Feedback Loop\n",
                "## Metrics (3 days)",
                f"- **Avg Score**: {d['metrics'].get('avg', 0)}",
                f"- **Trend**: {d['metrics'].get('trend', 0):+.2f}",
                f"- **Samples**: {d['metrics'].get('samples', 0)}",
                f"- **WBC Alerts**: {d['metrics'].get('wbcAlerts', 0)}",
                "\n## Thresholds",
                f"- health_high: {d['thresholds'].get('health_high', 'N/A')}",
                f"- health_low: {d['thresholds'].get('health_low', 'N/A')}",
                f"- stale_minutes: {d['thresholds'].get('stale_minutes', 'N/A')}",
                f"\n**Adjusted**: {'⚙️ YES' if d['adjusted'] else 'No'}",
            ]
            if d["adjustments"]:
                lines.append("\n## Adjustments")
                for a in d["adjustments"]:
                    lines.append(f"- {a}")
            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "sympatheia_notifications":
            action = arguments.get("action", "list")
            if action == "send":
                notif_id = sym._send_notification(
                    source=arguments.get("source", "claude"),
                    level=arguments.get("notification_level", "INFO"),
                    title=arguments.get("title", ""),
                    body=arguments.get("body", ""),
                    data={},
                )
                return [TextContent(type="text", text=f"✅ Notification sent: id={notif_id}")]
            else:
                # list
                limit = arguments.get("limit", 10)
                level_filter = arguments.get("level")
                notif_file = sym.MNEME / "notifications.jsonl"
                results = []
                try:
                    for line in notif_file.read_text("utf-8").strip().split("\n"):
                        if not line.strip():
                            continue
                        try:
                            record = _json.loads(line)
                            if level_filter and record.get("level", "") != level_filter.upper():
                                continue
                            results.append(record)
                        except Exception:
                            continue
                except FileNotFoundError:
                    pass
                results.reverse()
                results = results[:limit]
                if not results:
                    return [TextContent(type="text", text="📭 通知なし")]
                lines = [f"# 🔔 通知一覧 ({len(results)} 件)\n"]
                for r in results:
                    emoji = "🚨" if r.get("level") == "CRITICAL" else "⚠️" if r.get("level") == "HIGH" else "ℹ️"
                    lines.append(f"{emoji} **[{r.get('source')}]** {r.get('title')}")
                    lines.append(f"  {r.get('body', '')[:100]}")
                    lines.append(f"  _{r.get('timestamp', '')}_ | level={r.get('level')}")
                    lines.append("")
                return [TextContent(type="text", text="\n".join(lines))]

        elif name == "sympatheia_status":
            # 全 state ファイルサマリ
            mneme = sym.MNEME
            status = {}

            # Heartbeat
            hb = sym._read_json(mneme / "heartbeat.json")
            status["heartbeat"] = f"beats={hb.get('beats', '?')}, healthy={hb.get('healthy', '?')}"

            # WBC
            wbc = sym._read_json(mneme / "wbc_state.json", {"alerts": [], "totalAlerts": 0})
            status["wbc"] = f"totalAlerts={wbc.get('totalAlerts', 0)}, active={len(wbc.get('alerts', []))}"

            # Git
            git = sym._read_json(mneme / "git_sentinel.json")
            status["git"] = f"dirty={git.get('dirty', '?')}, branch={git.get('branch', '?')}"

            # File Monitor
            fm = sym._read_json(mneme / "file_monitor_state.json")
            status["fileMon"] = f"scans={fm.get('scanCount', 0)}, changes={fm.get('changeCount', 0)}"

            # Attractor
            att = sym._read_json(mneme / "attractor_dispatch.json", {"totalDispatches": 0})
            status["attractor"] = f"totalDispatches={att.get('totalDispatches', 0)}"

            # Config
            cfg = sym._load_config()
            th = cfg.get("thresholds", {})
            status["config"] = f"health_high={th.get('health_high')}, stale={th.get('stale_minutes')}min"

            # Weekly Digest
            wd = sym._read_json(mneme / "weekly_digest.json")
            status["digest"] = f"weekEnding={wd.get('weekEnding', 'N/A')}"

            # Notifications (未読 CRITICAL)
            try:
                notif_raw = (mneme / "notifications.jsonl").read_text("utf-8").strip().split("\n")
                crits = [l for l in notif_raw if '"CRITICAL"' in l]
                status["notifications"] = f"total={len(notif_raw)}, critical={len(crits)}"
            except Exception:
                status["notifications"] = "no data"

            lines = ["# 🧬 Sympatheia Status\n"]
            for k, v in status.items():
                lines.append(f"- **{k}**: {v}")

            return [TextContent(type="text", text="\n".join(lines))]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        log(f"Error in {name}: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        return [TextContent(type="text", text=f"Error: {e}")]


# PURPOSE: sympatheia_mcp_server の main 処理を実行する
async def main():
    """MCP サーバー起動。"""
    log("Starting stdio server...")
    try:
        async with stdio_server() as streams:
            log("stdio connected")
            await server.run(
                streams[0],
                streams[1],
                server.create_initialization_options(),
            )
    except Exception as e:
        log(f"Server error: {e}")
        raise


if __name__ == "__main__":
    import asyncio

    log("Running main...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Stopped by user")
    except Exception as e:
        log(f"Fatal error: {e}")
        sys.exit(1)
