# PROOF: [L1/定理] <- mekhane/basanos/ VISION.md 第2段階: 対話する免疫
# PURPOSE: JulesFeedback — L2 Jules の結果を L0 Basanos にフィードバックする。
"""
JulesFeedback — L2 Jules の結果を L0 Basanos にフィードバックする。

FEP 解釈:
- Jules fix = 予測誤差の解消 → L0 の該当チェッカーの精度を維持/上昇
- Jules false_positive = 偽陽性 → L0 の該当チェッカーの精度を下降
- Jules partial = 部分的修正 → 判断保留

設計:
- パイプラインは非同期: 今回の実行で Jules を起動 → 次回の実行で結果を回収
- pending_sessions.json で追跡
- 結果は feedback_history.json に蓄積
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

FEEDBACK_DIR = Path.home() / "oikos/mneme/.hegemonikon/jules_feedback"
PENDING_FILE = FEEDBACK_DIR / "pending_sessions.json"
HISTORY_FILE = FEEDBACK_DIR / "feedback_history.json"


# PURPOSE: 1つの Jules セッションからのフィードバック。
@dataclass
class FeedbackEntry:
    """1つの Jules セッションからのフィードバック。"""

    session_id: str
    date: str
    verdict: str  # "fix", "false_positive", "partial", "error", "pending"
    issues_reviewed: int = 0
    issues_fixed: int = 0
    issues_dismissed: int = 0  # false positives
    checker_adjustments: Dict[str, float] = field(default_factory=dict)
    # {checker_code: adjustment} e.g. {"AI-001": -0.1} = reduce weight

    # PURPOSE: to_dict の処理
    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "date": self.date,
            "verdict": self.verdict,
            "issues_reviewed": self.issues_reviewed,
            "issues_fixed": self.issues_fixed,
            "issues_dismissed": self.issues_dismissed,
            "checker_adjustments": self.checker_adjustments,
        }

    # PURPOSE: from_dict の処理
    @classmethod
    def from_dict(cls, d: dict) -> "FeedbackEntry":
        return cls(
            session_id=d.get("session_id", ""),
            date=d.get("date", ""),
            verdict=d.get("verdict", "pending"),
            issues_reviewed=d.get("issues_reviewed", 0),
            issues_fixed=d.get("issues_fixed", 0),
            issues_dismissed=d.get("issues_dismissed", 0),
            checker_adjustments=d.get("checker_adjustments", {}),
        )


# PURPOSE: Jules L2 結果を L0 Basanos にフィードバックする。
class JulesFeedback:
    """Jules L2 結果を L0 Basanos にフィードバックする。

    Usage:
        fb = JulesFeedback()
        fb.register_session("session-123", issues=[...])
        # ... later (next pipeline run) ...
        completed = fb.collect_completed()
        adjustments = fb.compute_adjustments()
    """

    def __init__(self, feedback_dir: Path = FEEDBACK_DIR):
        self.feedback_dir = feedback_dir
        self.pending_file = feedback_dir / "pending_sessions.json"
        self.history_file = feedback_dir / "feedback_history.json"
        self._ensure_dir()

    def _ensure_dir(self) -> None:
        self.feedback_dir.mkdir(parents=True, exist_ok=True)

    def _load_pending(self) -> List[dict]:
        if self.pending_file.exists():
            try:
                return json.loads(self.pending_file.read_text("utf-8"))
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def _save_pending(self, sessions: List[dict]) -> None:
        self.pending_file.write_text(
            json.dumps(sessions, ensure_ascii=False, indent=2), "utf-8"
        )

    def _load_history(self) -> List[dict]:
        if self.history_file.exists():
            try:
                return json.loads(self.history_file.read_text("utf-8"))
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def _save_history(self, entries: List[dict]) -> None:
        self.history_file.write_text(
            json.dumps(entries, ensure_ascii=False, indent=2), "utf-8"
        )

    # PURPOSE: Jules セッションを pending に登録。
    def register_session(
        self,
        session_id: str,
        issues: List[dict],
    ) -> None:
        """Jules セッションを pending に登録。

        Args:
            session_id: Jules session ID
            issues: L0 issues that triggered L2
        """
        pending = self._load_pending()

        # Deduplicate
        if any(s.get("session_id") == session_id for s in pending):
            logger.debug(f"Session {session_id} already registered")
            return

        pending.append({
            "session_id": session_id,
            "registered_at": datetime.now().isoformat(),
            "issue_codes": [i.get("code", "") for i in issues],
            "issue_count": len(issues),
        })
        self._save_pending(pending)
        logger.info(f"Registered Jules session: {session_id} ({len(issues)} issues)")

    # PURPOSE: 完了した Jules セッションの結果を回収して分類。
    def collect_completed(self) -> List[FeedbackEntry]:
        """完了した Jules セッションの結果を回収して分類。

        Returns:
            FeedbackEntry のリスト (verdict: fix/false_positive/partial/error)
        """
        pending = self._load_pending()
        if not pending:
            return []

        completed = []
        still_pending = []

        for session in pending:
            sid = session.get("session_id", "")
            result = self._check_session_status(sid)

            if result is None:
                # Still running or API unavailable
                still_pending.append(session)
                continue

            verdict, details = result

            entry = FeedbackEntry(
                session_id=sid,
                date=datetime.now().strftime("%Y-%m-%d"),
                verdict=verdict,
                issues_reviewed=session.get("issue_count", 0),
                issues_fixed=details.get("fixed", 0),
                issues_dismissed=details.get("dismissed", 0),
                checker_adjustments=self._compute_checker_adjustments(
                    session.get("issue_codes", []),
                    verdict,
                    details,
                ),
            )
            completed.append(entry)

        # Update pending (remove completed)
        self._save_pending(still_pending)

        # Append to history
        if completed:
            history = self._load_history()
            history.extend(e.to_dict() for e in completed)
            self._save_history(history)
            logger.info(f"Collected {len(completed)} completed Jules sessions")

        return completed

    def _check_session_status(
        self, session_id: str
    ) -> Optional[tuple]:
        """Jules セッションの状態を確認。

        Returns:
            None if still pending, or (verdict, details_dict)
        """
        try:
            import asyncio
            from mekhane.symploke.jules_client import JulesClient, SessionState
            import os

            api_key = None
            for i in range(1, 10):
                key = os.environ.get(f"JULES_API_KEY_{i:02d}")
                if key:
                    api_key = key
                    break

            if not api_key:
                logger.debug("No Jules API key, cannot check session status")
                return None

            async def _poll():
                async with JulesClient(api_key) as client:
                    session = await client.get_session(session_id)
                    return session

            session = asyncio.run(_poll())

            # Classify result
            state = session.state
            if state == SessionState.COMPLETED:
                # Check if it created changes
                has_changes = bool(session.plan and session.plan.steps)
                if has_changes:
                    return ("fix", {"fixed": len(session.plan.steps)})
                else:
                    return ("false_positive", {"dismissed": 1})
            elif state == SessionState.FAILED:
                return ("error", {})
            elif state == SessionState.CANCELLED:
                return ("false_positive", {"dismissed": 1})
            else:
                # Still running
                return None

        except ImportError:
            logger.debug("JulesClient not available")
            return None
        except Exception as e:
            logger.debug(f"Session check failed for {session_id}: {e}")
            return None

    def _compute_checker_adjustments(
        self,
        issue_codes: List[str],
        verdict: str,
        details: dict,
    ) -> Dict[str, float]:
        """チェッカー別の精度調整値を計算。

        - fix → 精度維持 (adjustment = 0 or +0.05)
        - false_positive → 精度下降 (adjustment = -0.1)
        - error → 判断しない (adjustment = 0)
        """
        adjustments: Dict[str, float] = {}

        if verdict == "fix":
            # Jules が修正した → チェッカーは正しかった → 微増
            for code in issue_codes:
                adjustments[code] = adjustments.get(code, 0) + 0.05
        elif verdict == "false_positive":
            # Jules が不要と判断 → チェッカーが偽陽性 → 減少
            for code in issue_codes:
                adjustments[code] = adjustments.get(code, 0) - 0.1
        # partial, error → no adjustment

        return adjustments

    # PURPOSE: 過去N日の feedback_history から累積チェッカー調整値を算出。
    def compute_cumulative_adjustments(self, days: int = 30) -> Dict[str, float]:
        """過去N日の feedback_history から累積チェッカー調整値を算出。"""
        history = self._load_history()
        if not history:
            return {}

        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        cumulative: Dict[str, float] = {}

        for entry_dict in history:
            if entry_dict.get("date", "") < cutoff:
                continue

            for code, adj in entry_dict.get("checker_adjustments", {}).items():
                cumulative[code] = cumulative.get(code, 0) + adj

        # Clamp to [-1.0, 1.0]
        for code in cumulative:
            cumulative[code] = max(-1.0, min(1.0, round(cumulative[code], 3)))

        return cumulative

    # PURPOSE: 累積調整値を RotationState に適用。
    def apply_to_rotation(self, state: "RotationState") -> Dict[str, Any]:
        """累積調整値を RotationState に適用。

        Returns:
            変更サマリ dict。
        """
        adjustments = self.compute_cumulative_adjustments()
        changes: Dict[str, Any] = {"adjustments_applied": {}}

        if not adjustments:
            return changes

        for code, adj in adjustments.items():
            # Map issue codes to domain categories
            category = code.split("-")[0] if "-" in code else code
            domain_map = {
                "AI": "Naming",  # AI-001 etc → Naming domain
                "GIT": "Git",
            }
            domain = domain_map.get(category, category)

            if domain in state.domains:
                old_w = state.domains[domain].weight
                new_w = max(0.1, min(2.0, old_w + adj * 0.5))
                state.domains[domain].weight = round(new_w, 3)
                changes["adjustments_applied"][domain] = {
                    "old": old_w,
                    "new": round(new_w, 3),
                    "from_code": code,
                    "cumulative_adj": adj,
                }

        if changes["adjustments_applied"]:
            logger.info(f"Jules feedback: {len(changes['adjustments_applied'])} domain adjustments")

        return changes

    # PURPOSE: フィードバック履歴の要約。
    def summary(self) -> str:
        """フィードバック履歴の要約。"""
        history = self._load_history()
        if not history:
            return "📊 Jules Feedback: No sessions completed yet."

        verdicts = {}
        for e in history:
            v = e.get("verdict", "unknown")
            verdicts[v] = verdicts.get(v, 0) + 1

        lines = [
            f"📊 Jules Feedback ({len(history)} sessions)",
        ]
        for v, count in sorted(verdicts.items()):
            icon = {"fix": "✅", "false_positive": "❌", "partial": "⚠️", "error": "💥"}.get(v, "❓")
            lines.append(f"   {icon} {v}: {count}")

        adjustments = self.compute_cumulative_adjustments()
        if adjustments:
            lines.append("   Checker adjustments:")
            for code, adj in sorted(adjustments.items()):
                direction = "↑" if adj > 0 else "↓"
                lines.append(f"      {code}: {direction}{abs(adj):.2f}")

        return "\n".join(lines)
