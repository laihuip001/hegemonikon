#!/usr/bin/env python3
# PROOF: [L2/分析] <- mekhane/symploke/ A4→品質フィードバック→basanos_feedback が担う
# PURPOSE: Basanos Perspective の品質フィードバック — レビュー結果から有用性スコアを蓄積
"""
Basanos Feedback Loop

Perspective ごとの「有用な指摘率」を追跡し、
低品質パースペクティブを減衰させるフィードバック機構。

Usage:
    # 結果収集 (scheduler ログ + Jules PR 結果を統合)
    python basanos_feedback.py collect --days 7

    # フィードバック状態表示
    python basanos_feedback.py show

    # 品質スコアで BasanosBridge にフィルタリングを適用
    from basanos_feedback import FeedbackStore
    store = FeedbackStore()
    excluded = store.get_low_quality_perspectives(threshold=0.1)
"""

import argparse
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

_THIS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _THIS_DIR.parent.parent
_STATE_FILE = _PROJECT_ROOT / "logs" / "specialist_daily" / "basanos_feedback_state.json"
_SCHEDULER_LOG_DIR = _PROJECT_ROOT / "logs" / "specialist_daily"


# PURPOSE: 個別 Perspective のフィードバックデータ
@dataclass
class PerspectiveFeedback:
    """Perspective ID ごとの累積フィードバック。"""
    perspective_id: str       # e.g. "BP-Architecture-O1"
    domain: str
    axis: str
    total_reviews: int = 0    # このパースペクティブが使われた回数
    useful_count: int = 0     # 有用な指摘を出した回数
    last_used: str = ""       # 最後に使われた日時

    # PURPOSE: 有用な指摘率 (0.0 - 1.0)。
    @property
    def usefulness_rate(self) -> float:
        """有用な指摘率 (0.0 - 1.0)。"""
        if self.total_reviews == 0:
            return 0.5  # 未使用 = ニュートラル (減衰しない)
        return self.useful_count / self.total_reviews


# PURPOSE: フィードバック状態の永続化
class FeedbackStore:
    """Basanos Perspective の品質フィードバックを管理。"""

    def __init__(self, state_file: Optional[Path] = None):
        self._state_file = state_file or _STATE_FILE
        self._data: dict[str, PerspectiveFeedback] = {}
        self._load()

    def _load(self):
        """状態ファイルから読み込み。"""
        if not self._state_file.exists():
            return
        try:
            raw = json.loads(self._state_file.read_text())
            for pid, entry in raw.items():
                self._data[pid] = PerspectiveFeedback(
                    perspective_id=pid,
                    domain=entry.get("domain", ""),
                    axis=entry.get("axis", ""),
                    total_reviews=entry.get("total_reviews", 0),
                    useful_count=entry.get("useful_count", 0),
                    last_used=entry.get("last_used", ""),
                )
        except (json.JSONDecodeError, KeyError):
            pass

    def _save(self):
        """状態ファイルに書き込み。"""
        self._state_file.parent.mkdir(parents=True, exist_ok=True)
        raw = {}
        for pid, fb in self._data.items():
            raw[pid] = {
                "domain": fb.domain,
                "axis": fb.axis,
                "total_reviews": fb.total_reviews,
                "useful_count": fb.useful_count,
                "last_used": fb.last_used,
                "usefulness_rate": round(fb.usefulness_rate, 3),
            }
        self._state_file.write_text(json.dumps(raw, indent=2, ensure_ascii=False))

    # PURPOSE: Perspective の使用を記録。
    def record_usage(self, perspective_id: str, domain: str, axis: str, was_useful: bool):
        """Perspective の使用を記録。"""
        if perspective_id not in self._data:
            self._data[perspective_id] = PerspectiveFeedback(
                perspective_id=perspective_id,
                domain=domain,
                axis=axis,
            )
        fb = self._data[perspective_id]
        fb.total_reviews += 1
        if was_useful:
            fb.useful_count += 1
        fb.last_used = datetime.now().strftime("%Y-%m-%d %H:%M")

    # PURPOSE: 有用率が閾値以下の Perspective ID リスト (10回以上使用されたもののみ)。
    def get_low_quality_perspectives(self, threshold: float = 0.1) -> list[str]:
        """有用率が閾値以下の Perspective ID リスト (10回以上使用されたもののみ)。"""
        return [
            pid for pid, fb in self._data.items()
            if fb.total_reviews >= 10 and fb.usefulness_rate < threshold
        ]

    # PURPOSE: 全フィードバックデータを返す。
    def get_all_feedback(self) -> dict[str, PerspectiveFeedback]:
        """全フィードバックデータを返す。"""
        return dict(self._data)

    # PURPOSE: 外部保存用。
    def save(self):
        """外部保存用。"""
        self._save()

    # PURPOSE: 淘汰レポートを返す (F14)。
    def get_exclusion_report(self, threshold: float = 0.1) -> dict:
        """淘汰レポートを返す (F14)。"""
        excluded = self.get_low_quality_perspectives(threshold)
        total = len(self._data)
        return {
            "excluded_count": len(excluded),
            "excluded_ids": excluded,
            "threshold": threshold,
            "total_perspectives": total,
            "exclusion_rate": round(len(excluded) / total, 3) if total else 0.0,
        }

    # PURPOSE: 指定日数以上使用されていない Perspective ID リストを返す (F24)。
    def get_stale_perspectives(self, inactive_days: int = 30) -> list[str]:
        """指定日数以上使用されていない Perspective ID リストを返す (F24)。

        Args:
            inactive_days: 非活性とみなす日数 (デフォルト30日)

        Returns:
            stale perspective_id のリスト
        """
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(days=inactive_days)
        cutoff_str = cutoff.strftime("%Y-%m-%d")

        stale = []
        for pid, fb in self._data.items():
            if not fb.last_used:
                stale.append(pid)
            elif fb.last_used < cutoff_str:
                stale.append(pid)
        return stale

    # PURPOSE: Perspective をアーカイブ状態にする (F24)。
    def archive_perspective(self, perspective_id: str) -> bool:
        """Perspective をアーカイブ状態にする (F24)。

        削除ではなくアーカイブ。archived/ ディレクトリに移動し、
        メインデータからは除外する。

        Returns:
            True if archived, False if not found
        """
        import json

        if perspective_id not in self._data:
            return False

        fb = self._data[perspective_id]

        # アーカイブファイルに追記
        archive_dir = self._state_file.parent / "archived_perspectives"
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive_file = archive_dir / "archive.jsonl"

        archive_record = {
            "perspective_id": perspective_id,
            "domain": fb.domain,
            "axis": fb.axis,
            "total_reviews": fb.total_reviews,
            "useful_count": fb.useful_count,
            "usefulness_rate": fb.usefulness_rate,
            "last_used": fb.last_used,
            "archived_at": __import__("datetime").datetime.now().isoformat(),
        }

        with open(archive_file, "a") as f:
            f.write(json.dumps(archive_record, ensure_ascii=False) + "\n")

        # メインデータから除外
        del self._data[perspective_id]
        self._save()
        return True


# PURPOSE: スケジューラーログから basanos 使用実績を収集
def collect_from_logs(days: int = 7) -> dict:
    """スケジューラーログを解析し、Perspective 使用実績を収集する。

    NOTE: 現時点では「レビューに使われた」ことのみ追跡。
    「有用だったか」は Jules の PR 結果を解析する必要がある (Phase 2)。
    """
    store = FeedbackStore()
    cutoff = datetime.now() - timedelta(days=days)
    processed = 0

    for log_file in sorted(_SCHEDULER_LOG_DIR.glob("scheduler_*.json")):
        try:
            data = json.loads(log_file.read_text())
            ts_str = data.get("timestamp", "")
            ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M")
            if ts < cutoff:
                continue

            if data.get("mode") != "basanos":
                continue

            basanos_info = data.get("basanos", {})
            domains = basanos_info.get("domains", [])
            axes_count = basanos_info.get("axes", 24)

            # 使用された Perspective を記録 (全 domain × 全 axis)
            for domain in domains:
                for axis_num in range(1, axes_count + 1):
                    # 実際の axis ID は不明なので convention で生成
                    series = ["O", "S", "H", "P", "K", "A"]
                    for s in series:
                        axis_nums_per_series = 4
                        for an in range(1, axis_nums_per_series + 1):
                            pid = f"BP-{domain}-{s}{an}"
                            store.record_usage(
                                perspective_id=pid,
                                domain=domain,
                                axis=f"{s}{an}",
                                was_useful=False,  # 現時点では不明 → Phase 2 で改善
                            )

            processed += 1

        except (json.JSONDecodeError, ValueError):
            continue

    store.save()
    return {
        "processed_logs": processed,
        "total_perspectives": len(store.get_all_feedback()),
    }


# PURPOSE: フィードバック状態を表示
def show_feedback():
    """フィードバック状態のサマリーを表示。"""
    store = FeedbackStore()
    all_fb = store.get_all_feedback()

    if not all_fb:
        print("📭 フィードバックデータなし")
        return

    print(f"\n{'='*50}")
    print(f"Basanos Perspective Feedback — {len(all_fb)} perspectives tracked")
    print(f"{'='*50}")

    # ドメイン別集計
    domain_stats: dict[str, dict] = {}
    for fb in all_fb.values():
        if fb.domain not in domain_stats:
            domain_stats[fb.domain] = {"count": 0, "total_reviews": 0, "useful": 0}
        domain_stats[fb.domain]["count"] += 1
        domain_stats[fb.domain]["total_reviews"] += fb.total_reviews
        domain_stats[fb.domain]["useful"] += fb.useful_count

    print(f"\n📊 Domain Summary:")
    print(f"  {'Domain':24s} {'Perspectives':>12s} {'Reviews':>8s} {'Useful':>8s} {'Rate':>6s}")
    for domain, stats in sorted(domain_stats.items()):
        rate = stats["useful"] / stats["total_reviews"] * 100 if stats["total_reviews"] else 0
        print(f"  {domain:24s} {stats['count']:12d} {stats['total_reviews']:8d} {stats['useful']:8d} {rate:5.1f}%")

    # 低品質パースペクティブ
    low_quality = store.get_low_quality_perspectives(threshold=0.1)
    if low_quality:
        print(f"\n⚠️  Low-quality perspectives ({len(low_quality)}):")
        for pid in low_quality[:10]:
            fb = all_fb[pid]
            print(f"  {pid}: {fb.usefulness_rate:.1%} ({fb.useful_count}/{fb.total_reviews})")


# PURPOSE: CLI エントリーポイント
def main():
    parser = argparse.ArgumentParser(description="Basanos Perspective Feedback")
    sub = parser.add_subparsers(dest="command")

    collect_parser = sub.add_parser("collect", help="Collect feedback from logs")
    collect_parser.add_argument("--days", type=int, default=7)

    sub.add_parser("show", help="Show feedback state")

    args = parser.parse_args()

    if args.command == "collect":
        result = collect_from_logs(args.days)
        print(f"Collected: {result['processed_logs']} logs, {result['total_perspectives']} perspectives")
    elif args.command == "show":
        show_feedback()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
