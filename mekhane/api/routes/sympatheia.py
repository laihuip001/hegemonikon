#!/usr/bin/env python3
# PROOF: [L2/Sympatheia] <- mekhane/api/routes/
# PURPOSE: Sympatheia 自律神経系 API — n8n Code node ロジックの中枢化
"""
Sympatheia Routes — 自律神経系 API

POST /api/sympatheia/wbc            — WF-09: 白血球（脅威分析）
POST /api/sympatheia/digest         — WF-10: 記憶圧縮（週次集約）
POST /api/sympatheia/attractor      — WF-11: 反射弓（定理推薦）
POST /api/sympatheia/feedback       — WF-12: 恒常性（閾値調整）
POST /api/sympatheia/route          — WF-14: 視床（ルーティング+転送）
POST /api/sympatheia/notifications  — 通知受信（n8n WF → HGK App）
GET  /api/sympatheia/notifications  — 通知一覧取得
"""

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional
import uuid

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

logger = logging.getLogger("hegemonikon.api.sympatheia")

# PURPOSE: State ファイルのベースパス
MNEME = Path(os.getenv("HGK_MNEME", "/home/makaron8426/oikos/mneme/.hegemonikon"))

router = APIRouter(prefix="/sympatheia", tags=["sympatheia"])


# ===========================================================================
# Pydantic Models
# ===========================================================================

# --- WBC ---
# PURPOSE: の統一的インターフェースを実現する
class WBCRequest(BaseModel):
    source: str = "unknown"
    severity: str = "medium"
    details: str = "No details"
    files: list[str] = Field(default_factory=list)


# PURPOSE: の統一的インターフェースを実現する
class WBCResponse(BaseModel):
    timestamp: str
    source: str
    severity: str
    threatScore: int
    level: str
    details: str
    files: list[str]
    recentAlertCount: int
    shouldEscalate: bool


# --- Digest ---
# PURPOSE: の統一的インターフェースを実現する
class DigestRequest(BaseModel):
    pass  # webhook trigger, no payload needed


# PURPOSE: の統一的インターフェースを実現する
class DigestResponse(BaseModel):
    timestamp: str
    weekEnding: str
    heartbeat: dict = Field(default_factory=dict)
    fileMon: dict = Field(default_factory=dict)
    git: dict = Field(default_factory=dict)
    wbc: dict = Field(default_factory=dict)
    health: dict = Field(default_factory=dict)
    sessions: int = 0


# --- Attractor ---
# PURPOSE: の統一的インターフェースを実現する
class AttractorRequest(BaseModel):
    context: str = ""
    text: str = ""  # fallback


# PURPOSE: の統一的インターフェースを実現する
class AttractorResponse(BaseModel):
    timestamp: str
    recommendation: dict | None = None
    autoDispatch: bool = False
    context: str = ""


# --- Feedback ---
# PURPOSE: の統一的インターフェースを実現する
class FeedbackRequest(BaseModel):
    pass


# PURPOSE: の統一的インターフェースを実現する
class FeedbackResponse(BaseModel):
    timestamp: str
    metrics: dict = Field(default_factory=dict)
    thresholds: dict = Field(default_factory=dict)
    adjusted: bool = False
    adjustments: list[str] = Field(default_factory=list)


# --- Route ---
# PURPOSE: の統一的インターフェースを実現する
class RouteRequest(BaseModel):
    type: str = ""
    source: str = "unknown"
    payload: dict = Field(default_factory=dict)


# PURPOSE: の統一的インターフェースを実現する
class RouteResponse(BaseModel):
    routed: bool = False
    target: str = ""
    wf: str = ""
    timestamp: str = ""
    error: str = ""
    available: list[str] = Field(default_factory=list)
    forwardResult: dict | None = None


# --- Notification ---
# PURPOSE: の統一的インターフェースを実現する
class NotificationRequest(BaseModel):
    source: str = "unknown"  # e.g. "WF-09", "WF-13"
    level: str = "INFO"  # INFO | HIGH | CRITICAL
    title: str = ""
    body: str = ""
    data: dict = Field(default_factory=dict)


# PURPOSE: の統一的インターフェースを実現する
class NotificationResponse(BaseModel):
    id: str
    timestamp: str
    source: str
    level: str
    title: str
    body: str
    data: dict = Field(default_factory=dict)


# ===========================================================================
# Helpers
# ===========================================================================

def _read_json(path: Path, default: Any = None) -> Any:
    """JSON ファイルを安全に読む。"""
    try:
        return json.loads(path.read_text("utf-8"))
    except Exception:
        return default if default is not None else {}


def _write_json(path: Path, data: Any) -> None:
    """JSON ファイルを安全に書く。"""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")
    except Exception as e:
        logger.warning("Failed to write %s: %s", path, e)


def _load_config() -> dict:
    """sympatheia_config.json を読み込む（WF-12 の出力を WF-09 が読む = 閉ループ）。"""
    default = {
        "thresholds": {"health_high": 0.5, "health_low": 0.3, "stale_minutes": 60},
        "sensitivity": 1.0,
        "lastAdjusted": None,
        "adjustmentHistory": [],
    }
    return _read_json(MNEME / "sympatheia_config.json", default)


def _send_notification(source: str, level: str, title: str, body: str, data: Optional[dict] = None) -> str:
    """ローカル通知を JSONL に保存する。Slack 代替。"""
    notif_id = str(uuid.uuid4())[:8]
    now = datetime.now(timezone.utc)
    record = {
        "id": notif_id,
        "timestamp": now.isoformat(),
        "source": source,
        "level": level,
        "title": title,
        "body": body,
        "data": data or {},
    }
    notif_file = MNEME / "notifications.jsonl"
    try:
        notif_file.parent.mkdir(parents=True, exist_ok=True)
        with open(notif_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        logger.info("Notification [%s] %s: %s", notif_id, source, title)
    except Exception as e:
        logger.warning("Notification write failed: %s", e)
    return notif_id


# ===========================================================================
# WF-09: White Blood Cell (脅威分析)
# ===========================================================================

# PURPOSE: ファイル重要度テーブル — registry.yaml から動的読込も将来対応
THREAT_WEIGHTS: dict[str, int] = {
    "SACRED_TRUTH.md": 10,
    "behavioral_constraints.md": 8,
    "registry.yaml": 7,
    "docker-compose.yml": 7,
    "hegemonikon.md": 6,
    "CONSTITUTION.md": 6,
    "axiom_hierarchy.md": 5,
    "safety-invariants.md": 5,
}


# PURPOSE: sympatheia の wbc analyze 処理を実行する
@router.post("/wbc", response_model=WBCResponse)
async def wbc_analyze(req: WBCRequest) -> WBCResponse:
    """白血球: 脅威分析 + エスカレーション。"""
    now = datetime.now(timezone.utc)
    state_file = MNEME / "wbc_state.json"
    state = _read_json(state_file, {"alerts": [], "totalAlerts": 0, "lastEscalation": None})

    # --- 閾値を config.json から読む (閉ループ) ---
    config = _load_config()
    sensitivity = config.get("sensitivity", 1.0)

    # --- 脅威スコア計算 ---
    threat_score = 0
    if req.severity == "critical":
        threat_score += 5
    elif req.severity == "high":
        threat_score += 3
    else:
        threat_score += 1

    for f in req.files:
        for key, weight in THREAT_WEIGHTS.items():
            if key in f:
                threat_score += weight

    # 直近1時間のアラート数 (連続攻撃検知)
    one_hour_ago = (now - timedelta(hours=1)).isoformat()
    recent = [a for a in state.get("alerts", []) if a.get("timestamp", "") > one_hour_ago]
    if len(recent) >= 3:
        threat_score += 5

    # sensitivity 適用 (WF-12 からのフィードバック)
    threat_score = int(threat_score * sensitivity)

    level = "CRITICAL" if threat_score >= 8 else "HIGH" if threat_score >= 4 else "LOW"
    should_escalate = level in ("CRITICAL", "HIGH")

    diagnosis = WBCResponse(
        timestamp=now.isoformat(),
        source=req.source,
        severity=req.severity,
        threatScore=threat_score,
        level=level,
        details=req.details,
        files=req.files,
        recentAlertCount=len(recent),
        shouldEscalate=should_escalate,
    )

    # --- 状態保存 (24h window) ---
    one_day_ago = (now - timedelta(days=1)).isoformat()
    state["alerts"] = [a for a in state.get("alerts", []) if a.get("timestamp", "") > one_day_ago]
    state["alerts"].append(diagnosis.model_dump())
    state["totalAlerts"] = state.get("totalAlerts", 0) + 1
    if should_escalate:
        state["lastEscalation"] = now.isoformat()
    _write_json(state_file, state)

    # --- 通知 ---
    if should_escalate:
        emoji = "🚨" if level == "CRITICAL" else "⚠️"
        file_list = ", ".join(req.files[:5]) or "N/A"
        _send_notification(
            source="WF-09",
            level=level,
            title=f"{emoji} WBC: {level} threat detected",
            body=f"Source: {req.source}\nScore: {threat_score}/15\nFiles: {file_list}\nTotal: {state['totalAlerts']}",
            data={"threatScore": threat_score, "files": req.files[:5]},
        )

    return diagnosis


# ===========================================================================
# WF-10: Weekly Digest (記憶圧縮)
# ===========================================================================

# PURPOSE: sympatheia の weekly digest 処理を実行する
@router.post("/digest", response_model=DigestResponse)
async def weekly_digest(req: DigestRequest) -> DigestResponse:
    """記憶圧縮: 全メトリクス集約。"""
    now = datetime.now(timezone.utc)
    one_week_ago = (now - timedelta(weeks=1)).isoformat()

    # --- Heartbeat ---
    hb = _read_json(MNEME / "heartbeat.json")

    # --- File Monitor ---
    fm = _read_json(MNEME / "file_monitor_state.json")

    # --- Git Sentinel ---
    git = _read_json(MNEME / "git_sentinel.json")

    # --- WBC (週間フィルタ) ---
    wbc = _read_json(MNEME / "wbc_state.json", {"alerts": []})
    week_alerts = [a for a in wbc.get("alerts", []) if a.get("timestamp", "") > one_week_ago]

    # --- Health Metrics (週間平均) ---
    health_file = MNEME / "health_metrics.jsonl"
    health_scores: list[float] = []
    try:
        for line in health_file.read_text("utf-8").strip().split("\n")[-200:]:
            try:
                m = json.loads(line)
                if m.get("timestamp", "") > one_week_ago:
                    health_scores.append(m.get("score", 0))
            except Exception:
                pass
    except Exception:
        pass

    # --- Sessions (週間) ---
    sessions_dir = Path.home() / "oikos/mneme/.hegemonikon/sessions"
    session_count = 0
    try:
        for f in sessions_dir.glob("handoff_*.md"):
            try:
                if f.stat().st_mtime > (now - timedelta(weeks=1)).timestamp():
                    session_count += 1
            except Exception:
                pass
    except Exception:
        pass

    result = DigestResponse(
        timestamp=now.isoformat(),
        weekEnding=now.strftime("%Y-%m-%d"),
        heartbeat={"beats": hb.get("beats", 0), "healthy": hb.get("healthy", True)},
        fileMon={"scans": fm.get("scanCount", 0), "changes": fm.get("changeCount", 0)},
        git={"dirty": git.get("dirty", False), "changes": git.get("totalChanges", 0),
             "branch": git.get("branch", "unknown")},
        wbc={"weekAlerts": len(week_alerts),
             "criticals": sum(1 for a in week_alerts if a.get("level") == "CRITICAL"),
             "highs": sum(1 for a in week_alerts if a.get("level") == "HIGH")},
        health={"avg": round(sum(health_scores) / len(health_scores), 2) if health_scores else 0,
                "samples": len(health_scores)},
        sessions=session_count,
    )

    _write_json(MNEME / "weekly_digest.json", result.model_dump())

    # 通知
    _send_notification(
        source="WF-10",
        level="INFO",
        title=f"📊 Weekly Digest — {result.weekEnding}",
        body=(
            f"Heart: {result.heartbeat.get('beats',0)} beats\n"
            f"Files: {result.fileMon.get('scans',0)} scans\n"
            f"Git: {result.git.get('changes',0)} changes\n"
            f"WBC: {result.wbc.get('weekAlerts',0)} alerts\n"
            f"Sessions: {result.sessions}"
        ),
        data=result.model_dump(),
    )

    return result


# ===========================================================================
# WF-11: Attractor Dispatch (反射弓) — 本物の TheoremAttractor
# ===========================================================================

# lazy init (モデルロードが重いため)
_advisor = None


def _get_advisor():
    """AttractorAdvisor の遅延初期化。"""
    global _advisor
    if _advisor is None:
        try:
            from mekhane.fep.attractor_advisor import AttractorAdvisor
            _advisor = AttractorAdvisor(force_cpu=True, use_gnosis=False)
            logger.info("AttractorAdvisor initialized")
        except Exception as e:
            logger.warning("AttractorAdvisor init failed: %s", e)
    return _advisor


# PURPOSE: sympatheia の attractor dispatch 処理を実行する
@router.post("/attractor", response_model=AttractorResponse)
async def attractor_dispatch(req: AttractorRequest) -> AttractorResponse:
    """反射弓: TheoremAttractor による定理推薦。"""
    now = datetime.now(timezone.utc)
    context = req.context or req.text or ""
    state_file = MNEME / "attractor_dispatch.json"
    state = _read_json(state_file, {"dispatches": [], "totalDispatches": 0})

    recommendation = None
    auto_dispatch = False

    advisor = _get_advisor()
    if advisor and context:
        try:
            rec = advisor.recommend_theorem(context, top_k=1)
            if rec and rec.primary_theorem:
                recommendation = {
                    "theorem": rec.primary_theorem,
                    "name": rec.theorem_workflows[0][1] if rec.theorem_workflows else "",
                    "series": rec.primary_theorem[0],  # "O1" → "O"
                    "command": rec.primary_command,
                    "confidence": round(rec.confidence, 3),
                }
                auto_dispatch = rec.confidence >= 0.7
        except Exception as e:
            logger.warning("TheoremAttractor error: %s", e)

    # --- 状態保存 ---
    state["dispatches"] = state.get("dispatches", [])[-50:]
    state["dispatches"].append({
        "timestamp": now.isoformat(),
        "context": context[:200],
        "recommendation": recommendation,
        "autoDispatched": auto_dispatch,
    })
    state["totalDispatches"] = state.get("totalDispatches", 0) + 1
    _write_json(state_file, state)

    return AttractorResponse(
        timestamp=now.isoformat(),
        recommendation=recommendation,
        autoDispatch=auto_dispatch,
        context=context[:100],
    )


# ===========================================================================
# WF-12: Feedback Loop (恒常性)
# ===========================================================================

# PURPOSE: sympatheia の feedback loop 処理を実行する
@router.post("/feedback", response_model=FeedbackResponse)
async def feedback_loop(req: FeedbackRequest) -> FeedbackResponse:
    """恒常性: 閾値の動的調整。"""
    now = datetime.now(timezone.utc)
    three_days_ago = (now - timedelta(days=3)).isoformat()
    config = _load_config()

    # --- Health Metrics 分析 ---
    scores: list[float] = []
    try:
        for line in (MNEME / "health_metrics.jsonl").read_text("utf-8").strip().split("\n")[-200:]:
            try:
                m = json.loads(line)
                if m.get("timestamp", "") > three_days_ago:
                    scores.append(m.get("score", 0))
            except Exception:
                pass
    except Exception:
        pass

    # --- WBC Alert 頻度 ---
    wbc = _read_json(MNEME / "wbc_state.json", {"alerts": []})
    wbc_alerts = len([a for a in wbc.get("alerts", []) if a.get("timestamp", "") > three_days_ago])

    # --- トレンド ---
    avg = sum(scores) / len(scores) if scores else 0.5
    trend = 0.0
    if len(scores) >= 6:
        recent3 = sum(scores[-3:]) / 3
        prev3 = sum(scores[-6:-3]) / 3
        trend = recent3 - prev3

    adjustments: list[str] = []
    old_th = {**config.get("thresholds", {})}

    # 高スコア持続 → 感度向上
    if avg > 0.9 and len(scores) >= 10:
        config["thresholds"]["health_high"] = max(0.3, config["thresholds"].get("health_high", 0.5) - 0.05)
        adjustments.append(f"health_high: {old_th.get('health_high')} → {config['thresholds']['health_high']}")

    # 低スコア持続 → 感度低下
    if avg < 0.4 and len(scores) >= 5:
        config["thresholds"]["health_high"] = min(0.7, config["thresholds"].get("health_high", 0.5) + 0.05)
        adjustments.append(f"health_high: {old_th.get('health_high')} → {config['thresholds']['health_high']}")

    # アラート過多 → stale 延長
    if wbc_alerts > 10:
        config["thresholds"]["stale_minutes"] = min(120, config["thresholds"].get("stale_minutes", 60) + 15)
        adjustments.append(f"stale_minutes: → {config['thresholds']['stale_minutes']}")

    adjusted = len(adjustments) > 0
    if adjusted:
        config["lastAdjusted"] = now.isoformat()
        history = config.get("adjustmentHistory", [])[-20:]
        history.append({"timestamp": now.isoformat(), "changes": adjustments})
        config["adjustmentHistory"] = history
        _write_json(MNEME / "sympatheia_config.json", config)

        _send_notification(
            source="WF-12",
            level="INFO",
            title="⚖️ Homeostasis: 閾値調整",
            body="\n".join(f"• {a}" for a in adjustments),
            data={"adjustments": adjustments},
        )

    return FeedbackResponse(
        timestamp=now.isoformat(),
        metrics={"avg": round(avg, 2), "trend": round(trend, 2), "samples": len(scores), "wbcAlerts": wbc_alerts},
        thresholds=config.get("thresholds", {}),
        adjusted=adjusted,
        adjustments=adjustments,
    )


# ===========================================================================
# WF-14: Incoming Router (視床) — 分類 + 転送
# ===========================================================================

ROUTES: dict[str, dict[str, str]] = {
    "health": {"target": "health-alert", "wf": "WF-05"},
    "session-start": {"target": "session-state", "wf": "WF-06"},
    "session-end": {"target": "session-state", "wf": "WF-06"},
    "paper": {"target": "incoming-digest", "wf": "WF-03"},
    "alert": {"target": "wbc-alert", "wf": "WF-09"},
    "wbc": {"target": "wbc-alert", "wf": "WF-09"},
    "feedback": {"target": "feedback-loop", "wf": "WF-12"},
    "git": {"target": "git-sentinel", "wf": "WF-13"},
    "digest": {"target": "weekly-digest", "wf": "WF-10"},
    "heartbeat": {"target": "heartbeat", "wf": "WF-15"},
    "attractor": {"target": "attractor", "wf": "WF-11"},
}


# PURPOSE: sympatheia の incoming route 処理を実行する
@router.post("/route", response_model=RouteResponse)
async def incoming_route(req: RouteRequest) -> RouteResponse:
    """視床: 入力分類 + 実際に転送。"""
    now = datetime.now(timezone.utc)
    route_type = req.type.lower()
    route = ROUTES.get(route_type)

    # ログ
    log_file = MNEME / "incoming_router.jsonl"
    try:
        with open(log_file, "a") as f:
            f.write(json.dumps({
                "timestamp": now.isoformat(),
                "type": route_type,
                "routed": route["wf"] if route else "UNKNOWN",
                "source": req.source,
            }) + "\n")
    except Exception:
        pass

    if not route:
        return RouteResponse(
            error="Unknown type",
            timestamp=now.isoformat(),
            available=list(ROUTES.keys()),
        )

    # --- 実際に転送 (n8n webhook) ---
    import httpx
    n8n_base = os.getenv("N8N_BASE_URL", "http://localhost:5678")
    target_url = f"{n8n_base}/webhook/{route['target']}"
    forward_result = None

    try:
        resp = httpx.post(target_url, json=req.payload, timeout=15.0)
        try:
            forward_result = resp.json()
        except Exception:
            forward_result = {"status": resp.status_code, "text": resp.text[:200]}
    except Exception as e:
        forward_result = {"error": str(e)}

    return RouteResponse(
        routed=True,
        target=route["target"],
        wf=route["wf"],
        timestamp=now.isoformat(),
        forwardResult=forward_result,
    )


# ===========================================================================
# Notifications（通知受信 + 一覧）
# ===========================================================================

# PURPOSE: sympatheia の receive notification 処理を実行する
@router.post("/notifications", response_model=NotificationResponse, status_code=201)
async def receive_notification(req: NotificationRequest) -> NotificationResponse:
    """通知受信: n8n WF や内部モジュールからの通知を JSONL に保存。"""
    notif_id = _send_notification(
        source=req.source,
        level=req.level,
        title=req.title,
        body=req.body,
        data=req.data,
    )
    return NotificationResponse(
        id=notif_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        source=req.source,
        level=req.level,
        title=req.title,
        body=req.body,
        data=req.data,
    )


# PURPOSE: Digestor 最新候補を仮想通知に変換する
def _digestor_virtual_notifications(max_candidates: int = 5) -> list[dict]:
    """最新 Digestor レポートの上位候補を仮想通知に変換。"""
    try:
        from mekhane.api.routes.digestor import _list_report_files, _load_report
        files = _list_report_files()
        if not files:
            return []
        report = _load_report(files[0])
        if not report or not report.candidates:
            return []
        virtuals = []
        for c in report.candidates[:max_candidates]:
            topics_str = ", ".join(c.matched_topics[:3]) if c.matched_topics else ""
            body_parts = [f"スコア: {c.score:.0%}"]
            if c.rationale:
                body_parts.append(c.rationale[:200])
            if topics_str:
                body_parts.append(f"トピック: {topics_str}")
            if c.url:
                body_parts.append(f"URL: {c.url}")
            virtuals.append({
                "id": f"digestor-{hash(c.title) & 0xFFFF:04x}",
                "timestamp": report.timestamp,
                "source": "🧬 Digestor",
                "level": "INFO",
                "title": f"📰 {c.title}",
                "body": "\n".join(body_parts),
                "data": {"digestor": True, "score": c.score, "url": c.url or ""},
            })
        return virtuals
    except Exception as e:
        logger.debug("Digestor virtual notifications skipped: %s", e)
        return []


# PURPOSE: sympatheia の list notifications 処理を実行する
@router.get("/notifications")
async def list_notifications(
    limit: int = Query(50, ge=1, le=500),
    since: Optional[str] = Query(None, description="ISO8601 timestamp filter"),
    level: Optional[str] = Query(None, description="Filter by level: INFO|HIGH|CRITICAL"),
    include_digestor: bool = Query(True, description="Include Digestor candidates as virtual notifications"),
) -> list[NotificationResponse]:
    """通知一覧: JSONL から読み込み、最新順で返す。Digestor 候補も仮想通知としてマージ可能。"""
    notif_file = MNEME / "notifications.jsonl"
    results: list[dict] = []
    try:
        for line in notif_file.read_text("utf-8").strip().split("\n"):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                if since and record.get("timestamp", "") < since:
                    continue
                if level and record.get("level", "") != level.upper():
                    continue
                results.append(record)
            except Exception:
                continue
    except FileNotFoundError:
        pass
    except Exception as e:
        logger.warning("Notification read failed: %s", e)

    # Digestor 仮想通知をマージ
    if include_digestor and (not level or level.upper() == "INFO"):
        digestor_notifs = _digestor_virtual_notifications()
        for dn in digestor_notifs:
            if since and dn.get("timestamp", "") < since:
                continue
            results.append(dn)

    # 最新順、limit 適用
    results.sort(key=lambda r: r.get("timestamp", ""), reverse=True)
    return [NotificationResponse(**r) for r in results[:limit]]
