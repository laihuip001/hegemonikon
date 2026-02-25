# PROOF: [L1/定理] <- mekhane/basanos/ VISION.md G7/G8 の具体化
"""
TrendAnalyzer — daily_reviews/ データからパターンを学習する「記憶する免疫」。

G7: ファイル別重みマトリクス (file_heat → RotationState)
G8: FEP π(ε) 動的閾値 (category_velocity → threshold 調整)

設計原則:
- 空データでもクラッシュしない (graceful degradation)
- 合成データでテスト可能 (fixture first)
- 漸進的学習 (1日分でも有用、蓄積で精度向上)
"""

import json
import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

DAILY_REVIEWS_DIR = Path.home() / "oikos/mneme/.hegemonikon/daily_reviews"


# PURPOSE: ファイル別のissue履歴プロファイル。
@dataclass
class FileProfile:
    """ファイル別のissue履歴プロファイル。"""

    path: str
    total_issues: int = 0
    issue_types: Dict[str, int] = field(default_factory=dict)
    first_seen: str = ""
    last_seen: str = ""
    streak: int = 0  # consecutive days with issues
    days_active: int = 0  # total days with issues

    # PURPOSE: ヒートスコア: issues/day × streak × recency_decay。
    @property
    def heat(self) -> float:
        """ヒートスコア: issues/day × streak × recency_decay。

        FEP 解釈: 予測誤差が繰り返し発生するファイルは
        生成モデルの更新が必要 = 重点監視対象。
        """
        if self.days_active == 0:
            return 0.0

        issues_per_day = self.total_issues / max(self.days_active, 1)
        streak_factor = math.log2(self.streak + 1) + 1  # 1.0 → 1.0, 3 → 2.0, 7 → 3.0
        recency = self._recency_decay()

        return issues_per_day * streak_factor * recency

    def _recency_decay(self, half_life_days: int = 7) -> float:
        """最終検出日からの指数減衰。half_life_days で半減。"""
        if not self.last_seen:
            return 0.0
        try:
            last = datetime.strptime(self.last_seen, "%Y-%m-%d")
            days_ago = (datetime.now() - last).days
            return math.exp(-0.693 * days_ago / half_life_days)  # ln(2) ≈ 0.693
        except ValueError:
            return 0.5


# PURPOSE: daily_reviews/ データからトレンドを分析する。
class TrendAnalyzer:
    """daily_reviews/ データからトレンドを分析する。

    Usage:
        analyzer = TrendAnalyzer()
        profiles = analyzer.file_profiles()
        hot = analyzer.hot_files(top_n=5)
        thresholds = analyzer.suggest_thresholds()
    """

    def __init__(
        self,
        reviews_dir: Path = DAILY_REVIEWS_DIR,
        days: int = 14,
    ):
        self.reviews_dir = reviews_dir
        self.days = days
        self._reports: Optional[List[dict]] = None
        self._dates: Optional[List[str]] = None

    # PURPOSE: daily_reviews/ から過去N日分のレポートを読み込む。
    def load_reports(self) -> List[dict]:
        """daily_reviews/ から過去N日分のレポートを読み込む。"""
        if self._reports is not None:
            return self._reports

        reports = []
        if not self.reviews_dir.exists():
            self._reports = reports
            self._dates = []
            return reports

        cutoff = datetime.now() - timedelta(days=self.days)
        dates = []

        for json_file in sorted(self.reviews_dir.glob("*.json")):
            try:
                date_str = json_file.stem  # YYYY-MM-DD
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                if file_date < cutoff:
                    continue

                data = json.loads(json_file.read_text("utf-8"))
                # Normalize: single report → list
                if isinstance(data, dict):
                    data = [data]

                for report in data:
                    report["_date"] = date_str
                    reports.append(report)

                dates.append(date_str)
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Skipping {json_file}: {e}")

        self._reports = reports
        self._dates = sorted(set(dates))
        logger.info(f"Loaded {len(reports)} reports from {len(self._dates)} days")
        return reports

    # PURPOSE: レポートが存在する日付のリスト。
    @property
    def dates(self) -> List[str]:
        """レポートが存在する日付のリスト。"""
        if self._dates is None:
            self.load_reports()
        return self._dates or []

    # PURPOSE: ファイル別のプロファイルを集計。
    def file_profiles(self) -> Dict[str, FileProfile]:
        """ファイル別のプロファイルを集計。"""
        reports = self.load_reports()
        profiles: Dict[str, FileProfile] = {}
        # Track per-date file presence for streak calculation
        file_dates: Dict[str, set] = {}

        for report in reports:
            date = report.get("_date", "")
            for issue in report.get("l0_issues", []):
                file_path = issue.get("file", "")
                if not file_path:
                    continue

                if file_path not in profiles:
                    profiles[file_path] = FileProfile(
                        path=file_path,
                        first_seen=date,
                    )
                    file_dates[file_path] = set()

                p = profiles[file_path]
                p.total_issues += 1
                p.last_seen = max(p.last_seen, date) if p.last_seen else date

                # Category counting
                name = issue.get("name", "Unknown")
                category = name.split()[0] if name else "Unknown"
                p.issue_types[category] = p.issue_types.get(category, 0) + 1

                file_dates[file_path].add(date)

        # Calculate days_active and streak
        all_dates = self.dates
        for file_path, p in profiles.items():
            p.days_active = len(file_dates.get(file_path, set()))
            p.streak = self._calculate_streak(
                file_dates.get(file_path, set()), all_dates
            )

        return profiles

    def _calculate_streak(self, file_dates: set, all_dates: List[str]) -> int:
        """最新日からの連続検出日数を計算。"""
        if not file_dates or not all_dates:
            return 0

        streak = 0
        for date in reversed(all_dates):
            if date in file_dates:
                streak += 1
            else:
                break

        return streak

    # PURPOSE: ヒートスコア上位のファイルを返す。
    def hot_files(self, top_n: int = 10) -> List[FileProfile]:
        """ヒートスコア上位のファイルを返す。"""
        profiles = self.file_profiles()
        ranked = sorted(profiles.values(), key=lambda p: p.heat, reverse=True)
        return ranked[:top_n]

    # PURPOSE: カテゴリ別の日次issue数推移。
    def category_trends(self) -> Dict[str, List[int]]:
        """カテゴリ別の日次issue数推移。

        Returns:
            {category: [day1_count, day2_count, ...]}
        """
        reports = self.load_reports()
        all_dates = self.dates

        # Initialize
        daily: Dict[str, Dict[str, int]] = {}  # {category: {date: count}}

        for report in reports:
            date = report.get("_date", "")
            for issue in report.get("l0_issues", []):
                name = issue.get("name", "Unknown")
                category = name.split()[0] if name else "Unknown"
                if category not in daily:
                    daily[category] = {}
                daily[category][date] = daily[category].get(date, 0) + 1

        # Convert to ordered lists
        result: Dict[str, List[int]] = {}
        for category, date_counts in daily.items():
            result[category] = [date_counts.get(d, 0) for d in all_dates]

        return result

    # PURPOSE: カテゴリ別のissue増減速度 (issues/day)。
    def category_velocity(self) -> Dict[str, float]:
        """カテゴリ別のissue増減速度 (issues/day)。

        正 = 増加傾向、負 = 減少傾向。
        線形回帰の傾きで算出。
        """
        trends = self.category_trends()
        velocities: Dict[str, float] = {}

        for category, counts in trends.items():
            if len(counts) < 2:
                velocities[category] = 0.0
                continue

            # Simple linear regression slope
            n = len(counts)
            x_mean = (n - 1) / 2.0
            y_mean = sum(counts) / n

            numerator = sum((i - x_mean) * (c - y_mean) for i, c in enumerate(counts))
            denominator = sum((i - x_mean) ** 2 for i in range(n))

            if denominator == 0:
                velocities[category] = 0.0
            else:
                velocities[category] = round(numerator / denominator, 4)

        return velocities

    # PURPOSE: G8: カテゴリ別の推奨閾値を算出。
    def suggest_thresholds(self) -> Dict[str, float]:
        """G8: カテゴリ別の推奨閾値を算出。

        FEP π(ε): 上昇トレンドのカテゴリは精度 π を上げる (= 閾値を下げる)。
        """
        velocity = self.category_velocity()
        thresholds: Dict[str, float] = {}

        for category, v in velocity.items():
            # Base threshold: 1.0
            # Rising velocity → lower threshold (more sensitive)
            # Falling velocity → higher threshold (less sensitive)
            adjustment = -0.1 * v  # velocity 1.0/day → threshold -0.1
            threshold = max(0.3, min(1.5, 1.0 + adjustment))
            thresholds[category] = round(threshold, 3)

        return thresholds

    # PURPOSE: G7: 分析結果を RotationState に反映。
    def apply_to_rotation(self, state: "RotationState") -> Dict[str, Any]:
        """G7: 分析結果を RotationState に反映。

        Returns:
            変更のサマリ dict。
        """
        from mekhane.basanos.pipeline import DomainWeight

        changes: Dict[str, Any] = {"hot_files": [], "weight_adjustments": {}}

        # 1. Hot files → ドメイン重みを上げる
        hot = self.hot_files(top_n=5)
        for fp in hot:
            changes["hot_files"].append({"path": fp.path, "heat": round(fp.heat, 3)})

            # Top issue type → domain weight increase
            if fp.issue_types:
                top_category = max(fp.issue_types, key=fp.issue_types.get)
                if top_category in state.domains:
                    old_w = state.domains[top_category].weight
                    boost = min(0.3, fp.heat * 0.1)
                    new_w = min(2.0, old_w + boost)
                    state.domains[top_category].weight = round(new_w, 3)
                    changes["weight_adjustments"][top_category] = {
                        "old": old_w,
                        "new": round(new_w, 3),
                        "reason": f"hot file: {fp.path}",
                    }

        # 2. Category velocity → 下降トレンドの重みを下げる
        velocity = self.category_velocity()
        for category, v in velocity.items():
            if v < -0.5 and category in state.domains:
                old_w = state.domains[category].weight
                new_w = max(0.1, old_w - 0.1)
                state.domains[category].weight = round(new_w, 3)
                if category not in changes["weight_adjustments"]:
                    changes["weight_adjustments"][category] = {
                        "old": old_w,
                        "new": round(new_w, 3),
                        "reason": f"declining trend (v={v})",
                    }

        logger.info(
            f"Trend applied: {len(changes['hot_files'])} hot files, "
            f"{len(changes['weight_adjustments'])} weight changes"
        )
        return changes

    # PURPOSE: 分析結果の要約テキスト。
    def summary(self) -> str:
        """分析結果の要約テキスト。"""
        reports = self.load_reports()
        if not reports:
            return "No data available yet."

        profiles = self.file_profiles()
        hot = self.hot_files(top_n=3)
        velocity = self.category_velocity()

        lines = [
            f"📊 Trend Analysis ({len(self.dates)} days, {len(reports)} reports)",
            f"   Files tracked: {len(profiles)}",
        ]

        if hot:
            lines.append("   🔥 Hot files:")
            for fp in hot:
                lines.append(f"      {fp.path} (heat={fp.heat:.2f}, streak={fp.streak})")

        rising = {k: v for k, v in velocity.items() if v > 0.3}
        if rising:
            lines.append("   📈 Rising categories:")
            for cat, v in sorted(rising.items(), key=lambda x: -x[1]):
                lines.append(f"      {cat}: +{v:.2f}/day")

        return "\n".join(lines)
