#!/usr/bin/env python3
# PROOF: [L2/Sympatheia] <- mekhane/mcp/
# PURPOSE: Sympatheia MCP Server v1.1 — Hegemonikón Autonomic Nervous System
"""
Sympatheia MCP Server v1.1 — Hegemonikón Autonomic Nervous System

Tools: wbc, attractor, digest, feedback, notifications, status
Resources: heartbeat, wbc, config, notifications, digest, attractor
"""

import sys
import os
from pathlib import Path
from mekhane.mcp.mcp_base import MCPBase, StdoutSuppressor

_base = MCPBase(
    name="sympatheia",
    version="1.1.0",
    instructions=(
        "Sympatheia 自律神経系。脅威分析(WBC)、定理推薦(Attractor)、"
        "記憶圧縮(Digest)、恒常性(Feedback)、ルーティング(Route)を提供。"
    ),
)
server = _base.server
log = _base.log
TextContent = _base.TextContent
Tool = _base.Tool

# Also need Resource for this server
from mcp.types import Resource

import json as _json

# Lazy Sympatheia import
_sympatheia = None


def _get_sympatheia():
    """‪sympatheia.py のヘルパー関数群を安全にインポート。"""
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
        # === Basanos/Peira integration ===
        Tool(
            name="sympatheia_basanos_scan",
            description=(
                "Basanos L0 スキャン: AST ベース静的解析で Python ファイルの品質問題を検出する。"
                "DailyReviewPipeline の L0 フェーズを手動実行。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "スキャン対象パス (ファイルまたはディレクトリ)"},
                    "max_issues": {"type": "integer", "description": "最大 issue 数", "default": 20},
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="sympatheia_peira_health",
            description=(
                "Peira ヘルスチェック: 全サービスの死活と品質を一覧表示。"
                "Systemd, Docker, Handoff, Dendron, 定理活性度, Digest 鮮度を検証。"
            ),
            inputSchema={"type": "object", "properties": {}},
        ),
        # === BC Violation Logger ===
        Tool(
            name="sympatheia_log_violation",
            description=(
                "BC違反/フィードバック記録: Creator の叱責・承認・AI 自己検出を JSONL に即時記録。"
                "記録後にセッション統計サマリーを返す。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "feedback_type": {
                        "type": "string",
                        "enum": ["reprimand", "acknowledgment", "self_detected"],
                        "description": "種別: reprimand(叱責), acknowledgment(承認), self_detected(自己検出)",
                    },
                    "bc_ids": {
                        "type": "array", "items": {"type": "string"},
                        "description": "違反した BC ID (例: ['BC-1', 'BC-3'])",
                        "default": [],
                    },
                    "pattern": {
                        "type": "string",
                        "description": "パターンID (skip_bias, selective_omission 等)",
                        "default": "",
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "default": "medium",
                    },
                    "description": {"type": "string", "description": "何が起きたか"},
                    "context": {"type": "string", "description": "そのとき何をしていたか", "default": ""},
                    "creator_words": {"type": "string", "description": "Creator の原文 (叱責/承認の言葉)", "default": ""},
                    "corrective": {"type": "string", "description": "取った是正行動", "default": ""},
                },
                "required": ["feedback_type", "description"],
            },
        ),
        Tool(
            name="sympatheia_violation_dashboard",
            description=(
                "BC違反ダッシュボード: パターン別・BC別・深刻度別の統計 + 週次トレンド + Creator の言葉。"
                "叱責率と自己検出率を可視化する。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "period": {
                        "type": "string",
                        "enum": ["today", "week", "month", "all"],
                        "default": "all",
                        "description": "集計期間",
                    },
                },
            },
        ),
        Tool(
            name="sympatheia_escalate",
            description=(
                "BC違反の昇格候補検出: 深刻度や再発回数に基づき violations.md への昇格候補を提案。"
                "自動書込みはしない (LBYL)。テンプレートを表示するのみ。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "min_severity": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "default": "high",
                        "description": "最低深刻度",
                    },
                    "min_occurrences": {
                        "type": "integer",
                        "default": 2,
                        "description": "最低出現回数",
                    },
                },
            },
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

        elif name == "sympatheia_basanos_scan":
            return await _handle_basanos_scan(arguments)

        elif name == "sympatheia_peira_health":
            return await _handle_peira_health()

        elif name == "sympatheia_log_violation":
            return await _handle_log_violation(arguments)

        elif name == "sympatheia_violation_dashboard":
            return await _handle_violation_dashboard(arguments)

        elif name == "sympatheia_escalate":
            return await _handle_escalate(arguments)

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        log(f"Error in {name}: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        return [TextContent(type="text", text=f"Error: {e}")]




# ============ Basanos/Peira handlers ============

async def _handle_basanos_scan(arguments: dict) -> list[TextContent]:
    """Basanos L0 scan via AIAuditor."""
    target = arguments.get("path", "")
    max_issues = arguments.get("max_issues", 20)
    if not target:
        return [TextContent(type="text", text="Error: path is required")]

    try:
        with StdoutSuppressor():
            from mekhane.basanos.ai_auditor import AIAuditor

        target_path = Path(target)
        if not target_path.exists():
            return [TextContent(type="text", text=f"Error: path not found: {target}")]

        auditor = AIAuditor(strict=False)
        all_issues = []

        if target_path.is_file():
            result = auditor.audit_file(target_path)
            all_issues.extend(result.issues)
        else:
            # Scan all .py files in directory
            for py_file in sorted(target_path.glob("**/*.py")):
                if py_file.name.startswith("__"):
                    continue
                try:
                    result = auditor.audit_file(py_file)
                    all_issues.extend(result.issues)
                except Exception:
                    pass  # Skip unparseable files

        if not all_issues:
            return [TextContent(type="text", text=f"✅ Basanos: no issues in `{target_path.name}`")]

        lines = [f"# 🔍 Basanos Scan: {target_path.name}\n"]
        lines.append(f"**Issues**: {len(all_issues)} (showing max {max_issues})\n")
        for issue in all_issues[:max_issues]:
            lines.append(f"- **{issue.severity.value}** [{issue.code}] L{issue.line}: {issue.message}")

        return [TextContent(type="text", text="\n".join(lines))]
    except Exception as e:
        log(f"Basanos scan error: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _handle_peira_health() -> list[TextContent]:
    """Peira health check."""
    try:
        with StdoutSuppressor():
            from mekhane.peira.hgk_health import run_health_check, format_terminal

        report = run_health_check()
        text = format_terminal(report)
        return [TextContent(type="text", text=text)]
    except Exception as e:
        log(f"Peira health error: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# ============ BC Violation Logger handlers ============

async def _handle_log_violation(arguments: dict) -> list[TextContent]:
    """BC違反/フィードバックを記録。"""
    try:
        from scripts.bc_violation_logger import (
            FeedbackEntry, log_entry, read_all_entries,
            format_session_summary, compute_stats,
        )
        from datetime import datetime

        entry = FeedbackEntry(
            timestamp=datetime.now().isoformat(),
            feedback_type=arguments.get("feedback_type", "self_detected"),
            bc_ids=arguments.get("bc_ids", []),
            pattern=arguments.get("pattern", ""),
            severity=arguments.get("severity", "medium"),
            description=arguments.get("description", ""),
            context=arguments.get("context", ""),
            creator_words=arguments.get("creator_words", ""),
            corrective=arguments.get("corrective", ""),
        )

        path = log_entry(entry)

        # セッション統計
        all_entries = read_all_entries()
        stats = compute_stats(all_entries)
        summary = format_session_summary(all_entries)

        TYPE_ICONS = {"reprimand": "⚡", "acknowledgment": "✨", "self_detected": "🔍"}
        icon = TYPE_ICONS.get(entry.feedback_type, "")

        lines = [
            f"# {icon} フィードバック記録完了\n",
            f"- **種別**: {entry.feedback_type}",
            f"- **BC**: {', '.join(entry.bc_ids) or 'N/A'}",
            f"- **パターン**: {entry.pattern or 'N/A'}",
            f"- **深刻度**: {entry.severity}",
            f"- **説明**: {entry.description}",
        ]
        if entry.creator_words:
            lines.append(f"- **Creator の言葉**: \"{entry.creator_words}\"")
        lines.append(f"\n{summary}")
        lines.append(f"\n📁 ログ: `{path}`")

        return [TextContent(type="text", text="\n".join(lines))]
    except Exception as e:
        log(f"Log violation error: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _handle_violation_dashboard(arguments: dict) -> list[TextContent]:
    """BC違反ダッシュボードを表示。"""
    try:
        from scripts.bc_violation_logger import (
            read_all_entries, format_dashboard,
        )

        period = arguments.get("period", "all")
        entries = read_all_entries()

        if not entries:
            return [TextContent(type="text", text="✅ フィードバック記録なし — まだログがありません")]

        dashboard = format_dashboard(entries, period=period)
        return [TextContent(type="text", text=dashboard)]
    except Exception as e:
        log(f"Violation dashboard error: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _handle_escalate(arguments: dict) -> list[TextContent]:
    """violations.md への昇格候補を表示。"""
    try:
        from scripts.bc_violation_logger import (
            read_all_entries, suggest_escalation,
        )

        min_severity = arguments.get("min_severity", "high")
        min_occurrences = arguments.get("min_occurrences", 2)
        entries = read_all_entries()

        if not entries:
            return [TextContent(type="text", text="✅ フィードバック記録なし")]

        candidates = suggest_escalation(
            entries, min_severity=min_severity, min_occurrences=min_occurrences,
        )

        if not candidates:
            return [TextContent(type="text", text="✅ 昇格候補なし — 条件に合致するパターンがありません")]

        lines = [f"# 📋 昇格候補: {len(candidates)} 件\n"]
        for c in candidates:
            lines.append(f"## {c['pattern']} ({c['reason']}, {c['count']}件)\n")
            lines.append(f"```yaml\n{c['template']}```\n")

        return [TextContent(type="text", text="\n".join(lines))]
    except Exception as e:
        log(f"Escalate error: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


if __name__ == "__main__":
    from mekhane.mcp.mcp_guard import guard
    guard("sympatheia")
    _base.run()

