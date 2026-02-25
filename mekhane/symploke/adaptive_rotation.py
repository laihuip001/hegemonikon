# PROOF: [L2/ドメイン] <- mekhane/symploke/ O4→適応ローテーション→動的モード
"""F16: Adaptive Rotation — 過去の成功率に基づいて cron モードを動的に選択する。

jules_cron.sh から呼ばれ、曜日に固定ではなく実績ベースでモードを推奨する。

Usage:
    # Python から
    from adaptive_rotation import recommend_mode
    mode = recommend_mode(day_of_week=1)  # 1=Mon ... 7=Sun

    # CLI から (jules_cron.sh 連携)
    python -c "from adaptive_rotation import recommend_mode; print(recommend_mode(1))"
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Optional


# デフォルトのログディレクトリ
DEFAULT_LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs" / "specialist_daily"

# 有効なモード
VALID_MODES = {"basanos", "hybrid", "specialist"}

# デフォルトのローテーション (フォールバック)
STATIC_ROTATION = {
    1: "basanos",   # Mon
    2: "hybrid",    # Tue
    3: "basanos",   # Wed
    4: "hybrid",    # Thu
    5: "basanos",   # Fri
    6: "specialist",  # Sat
    7: "specialist",  # Sun
}


def _parse_logs(log_dir: Path, window_days: int = 14) -> dict[str, list[float]]:
    """直近 N 日のスケジューラーログからモード別成功率を集計する。

    Returns:
        {"basanos": [0.85, 0.90, ...], "hybrid": [...], "specialist": [...]}
    """
    import datetime

    cutoff = datetime.datetime.now() - datetime.timedelta(days=window_days)
    mode_rates: dict[str, list[float]] = defaultdict(list)

    if not log_dir.exists():
        return dict(mode_rates)

    # scheduler_YYYYMMDD_HHMM.json ファイルを探索
    for log_file in sorted(log_dir.glob("scheduler_*.json")):
        try:
            # ファイル名から日付を抽出
            stem = log_file.stem  # scheduler_20260215_0600
            date_part = stem.split("_")[1]  # 20260215
            file_date = datetime.datetime.strptime(date_part, "%Y%m%d")
            if file_date < cutoff:
                continue

            data = json.loads(log_file.read_text())
            mode = data.get("mode", "").lower()
            if mode not in VALID_MODES:
                continue

            total = data.get("total_started", 0) + data.get("total_failed", 0)
            if total == 0:
                continue
            success_rate = data.get("total_started", 0) / total
            mode_rates[mode].append(success_rate)

        except (json.JSONDecodeError, ValueError, KeyError, IndexError):
            continue

    return dict(mode_rates)


def _weighted_avg(rates: list[float]) -> float:
    """最近のデータに重みをつけた加重平均。"""
    if not rates:
        return 0.0
    n = len(rates)
    weights = [i + 1 for i in range(n)]  # 古い=1, 新しい=n
    total_weight = sum(weights)
    return sum(r * w for r, w in zip(rates, weights)) / total_weight


# PURPOSE: 曜日に対する推奨モードを返す (F23: MAB ベース選択)。
def recommend_mode(
    day_of_week: int,
    log_dir: Optional[Path] = None,
    window_days: int = 14,
) -> str:
    """曜日に対する推奨モードを返す (F23: MAB ベース選択)。

    Args:
        day_of_week: 曜日 (1=Mon ... 7=Sun, date +%u 互換)
        log_dir: ログディレクトリ (None = デフォルト)
        window_days: 集計ウィンドウ日数

    Returns:
        推奨モード文字列 ("basanos", "hybrid", "specialist")

    選択戦略:
        - データ < 5 : 静的ローテーション (フォールバック)
        - 5 ≤ データ < 50 : ε-greedy (ε=0.1)
        - データ ≥ 50 : UCB1 (Upper Confidence Bound)
    """
    import math
    import random

    if log_dir is None:
        log_dir = DEFAULT_LOG_DIR

    mode_rates = _parse_logs(log_dir, window_days)

    # データ不足時はフォールバック
    total_data = sum(len(v) for v in mode_rates.values())
    if total_data < 5:
        return STATIC_ROTATION.get(day_of_week, "basanos")

    # モード別加重平均成功率
    mode_scores = {
        mode: _weighted_avg(rates)
        for mode, rates in mode_rates.items()
    }

    # 未試行モードがあれば必ず試行 (探索保証)
    untried = [m for m in VALID_MODES if m not in mode_scores]
    if untried:
        return random.choice(untried)

    if total_data >= 50:
        # UCB1: score + c * sqrt(ln(N) / n_i)
        # 探索項が少ないモードを押し上げる
        ucb_scores = {}
        for mode, avg_score in mode_scores.items():
            n_i = len(mode_rates.get(mode, []))
            if n_i == 0:
                ucb_scores[mode] = float("inf")
            else:
                exploration = math.sqrt(math.log(total_data) / n_i)
                ucb_scores[mode] = avg_score + 1.0 * exploration  # c=1.0
        return max(ucb_scores, key=lambda m: ucb_scores[m])
    else:
        # ε-greedy: 90% exploit, 10% explore
        epsilon = 0.1
        if random.random() < epsilon:
            return random.choice(list(VALID_MODES))
        else:
            return max(mode_scores, key=lambda m: mode_scores[m])


# PURPOSE: 全曜日の推奨ローテーションレポートを返す。
def get_rotation_report(
    log_dir: Optional[Path] = None,
    window_days: int = 14,
) -> dict:
    """全曜日の推奨ローテーションレポートを返す。"""
    if log_dir is None:
        log_dir = DEFAULT_LOG_DIR

    mode_rates = _parse_logs(log_dir, window_days)
    mode_scores = {
        mode: round(_weighted_avg(rates), 3)
        for mode, rates in mode_rates.items()
    }

    rotation = {}
    day_names = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}
    for dow in range(1, 8):
        rotation[day_names[dow]] = {
            "static": STATIC_ROTATION[dow],
            "adaptive": recommend_mode(dow, log_dir, window_days),
        }

    return {
        "mode_scores": mode_scores,
        "total_data_points": sum(len(v) for v in mode_rates.values()),
        "window_days": window_days,
        "rotation": rotation,
    }


# CLI エントリポイント
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "report":
        report = get_rotation_report()
        print(json.dumps(report, indent=2, ensure_ascii=False))
    elif len(sys.argv) > 1:
        try:
            dow = int(sys.argv[1])
            print(recommend_mode(dow))
        except ValueError:
            print(f"Usage: {sys.argv[0]} [day_of_week|report]", file=sys.stderr)
            sys.exit(1)
    else:
        # デフォルト: 今日の推奨
        import datetime
        today_dow = datetime.datetime.now().isoweekday()
        print(recommend_mode(today_dow))
