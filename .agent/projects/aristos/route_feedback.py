# PROOF: [L3/フィードバック] <- aristos/ ルーティングフィードバック収集
"""
Aristos Route Feedback — ルーティングフィードバックの収集・永続化

WF ルーティング結果に対するフィードバックを記録し、
CostVector.scalar() の重み最適化に使用する。

Usage:
    from aristos.route_feedback import RouteFeedback, log_route_feedback
    fb = RouteFeedback(
        source="noe", target="dia",
        chosen_route=["noe", "bou", "dia"],
        quality=0.8,
    )
    log_route_feedback(fb)
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import yaml


# =============================================================================
# Config
# =============================================================================

ROUTE_FEEDBACK_PATH = Path.home() / "oikos/mneme/.hegemonikon/route_feedback.yaml"
ROUTE_FEEDBACK_MAX_ENTRIES = 2000


# =============================================================================
# Types
# =============================================================================

@dataclass
class RouteFeedback:
    """ルーティングフィードバックエントリ

    Attributes:
        source: 起点 WF 名
        target: 終点 WF 名
        chosen_route: 選択された経路 (WF 名のリスト)
        quality: 品質スコア (0.0-1.0)。1.0 = 完璧、0.0 = 完全に不適切
        cost_scalar: 計算されたスカラーコスト
        actual_time_min: 実際にかかった時間 (分)
        depth: 実行深度 (L0-L3)
        timestamp: 記録日時
        notes: 補足コメント
    """
    source: str
    target: str
    chosen_route: List[str]
    quality: float
    cost_scalar: float = 0.0
    actual_time_min: float = 0.0
    depth: str = "L2"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    notes: str = ""


# =============================================================================
# I/O
# =============================================================================

def log_route_feedback(
    feedback: RouteFeedback,
    path: Optional[Path] = None,
) -> None:
    """ルーティングフィードバックを YAML に記録"""
    p = path or ROUTE_FEEDBACK_PATH
    p.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "source": feedback.source,
        "target": feedback.target,
        "route": feedback.chosen_route,
        "quality": round(feedback.quality, 3),
        "cost_scalar": round(feedback.cost_scalar, 3),
        "actual_time_min": round(feedback.actual_time_min, 1),
        "depth": feedback.depth,
        "timestamp": feedback.timestamp,
    }
    if feedback.notes:
        entry["notes"] = feedback.notes

    existing: List[dict] = []
    if p.exists():
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data and isinstance(data.get("route_feedback"), list):
                    existing = data["route_feedback"]
        except Exception:
            existing = []

    existing.append(entry)

    # Keep last N entries
    existing = existing[-ROUTE_FEEDBACK_MAX_ENTRIES:]

    with open(p, "w", encoding="utf-8") as f:
        yaml.dump(
            {"route_feedback": existing},
            f,
            allow_unicode=True,
            default_flow_style=False,
        )


def load_route_feedback(
    path: Optional[Path] = None,
) -> List[RouteFeedback]:
    """YAML からフィードバックを読込"""
    p = path or ROUTE_FEEDBACK_PATH
    if not p.exists():
        return []

    try:
        with open(p, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception:
        return []

    if not data or not isinstance(data.get("route_feedback"), list):
        return []

    results = []
    for entry in data["route_feedback"]:
        try:
            results.append(RouteFeedback(
                source=entry["source"],
                target=entry["target"],
                chosen_route=entry.get("route", []),
                quality=float(entry.get("quality", 0.5)),
                cost_scalar=float(entry.get("cost_scalar", 0.0)),
                actual_time_min=float(entry.get("actual_time_min", 0.0)),
                depth=entry.get("depth", "L2"),
                timestamp=entry.get("timestamp", ""),
                notes=entry.get("notes", ""),
            ))
        except (KeyError, TypeError, ValueError):
            continue

    return results


def clear_route_feedback(path: Optional[Path] = None) -> int:
    """フィードバックをクリアし、削除件数を返す"""
    p = path or ROUTE_FEEDBACK_PATH
    if not p.exists():
        return 0
    feedback = load_route_feedback(p)
    count = len(feedback)
    p.unlink()
    return count


# =============================================================================
# Helpers
# =============================================================================


def estimate_quality(
    actual_time_min: float = 0.0,
    estimated_time_min: float = 5.0,
    had_errors: bool = False,
    was_corrected: bool = False,
    depth: str = "L2",
) -> float:
    """WF 実行結果から品質を自動推定 (0.0-1.0)

    ヒューリスティクス:
    - 時間効率: 予測時間との比率 (予測以下なら高品質)
    - エラー有無: エラーがあれば -0.3
    - 修正有無: Creator が修正したら -0.2
    - 深度ボーナス: L3 で完走なら +0.1 (高難度の成功)
    """
    quality = 0.7  # baseline

    # 時間効率 (0.0-0.2)
    if estimated_time_min > 0 and actual_time_min > 0:
        ratio = actual_time_min / estimated_time_min
        if ratio <= 1.0:
            quality += 0.2  # faster than expected
        elif ratio <= 1.5:
            quality += 0.1  # slightly over
        else:
            quality -= 0.1  # significantly over

    # エラーペナルティ
    if had_errors:
        quality -= 0.3

    # 修正ペナルティ
    if was_corrected:
        quality -= 0.2

    # 深度ボーナス
    if depth == "L3" and not had_errors:
        quality += 0.1

    return max(0.0, min(1.0, round(quality, 2)))


def log_from_dispatch(
    dispatch_result: dict,
    quality: Optional[float] = None,
    actual_time_min: float = 0.0,
    had_errors: bool = False,
    was_corrected: bool = False,
    notes: str = "",
    path: Optional[Path] = None,
) -> Optional[RouteFeedback]:
    """dispatch() の結果から直接フィードバックをログする便利関数

    Args:
        dispatch_result: dispatch() が返す dict
        quality: 品質 (0.0-1.0)。None なら自動推定
        actual_time_min: 実行にかかった時間 (分)
        had_errors: エラーが発生したか
        was_corrected: Creator による修正があったか
        notes: 補足
        path: 保存先 (テスト用)

    Returns:
        作成した RouteFeedback (失敗時は None)
    """
    if not dispatch_result.get("success") or not dispatch_result.get("workflows"):
        return None

    workflows = dispatch_result["workflows"]
    if len(workflows) < 2:
        # 単一 WF ではルーティング品質を評価できない
        return None

    source = workflows[0].lstrip("/")
    target = workflows[-1].lstrip("/")
    route = [w.lstrip("/") for w in workflows]

    # 深度推定
    depth_level = dispatch_result.get("depth_level", 2)
    depth_str = f"L{depth_level}"

    # コスト計算 (可能であれば)
    cost_scalar = 0.0
    try:
        from aristos.cost import CostCalculator, Depth
        calc = CostCalculator()
        depth_enum = Depth(depth_level)
        for wf in route:
            cost = calc.calculate(wf, depth=depth_enum)
            cost_scalar += cost.scalar()
    except Exception:
        pass

    # 品質推定 (手動指定なし)
    if quality is None:
        # 推定時間 (DEFAULT_TIME_ESTIMATES から)
        estimated = 5.0
        try:
            from aristos.cost import DEFAULT_TIME_ESTIMATES
            estimated = sum(
                DEFAULT_TIME_ESTIMATES.get(w, 5.0) for w in route
            )
        except Exception:
            pass
        quality = estimate_quality(
            actual_time_min=actual_time_min,
            estimated_time_min=estimated,
            had_errors=had_errors,
            was_corrected=was_corrected,
            depth=depth_str,
        )

    fb = RouteFeedback(
        source=source,
        target=target,
        chosen_route=route,
        quality=quality,
        cost_scalar=round(cost_scalar, 2),
        actual_time_min=actual_time_min,
        depth=depth_str,
        notes=notes,
    )
    log_route_feedback(fb, path=path)
    return fb
