# PROOF: [L1/算出] <- aristos/ Feedback 可視化
"""
Aristos Visualize — ターミナルでのフィードバック統計可視化

ASCII ヒストグラムと重み比較チャートをターミナルに表示する。
外部ライブラリ不要。

Usage:
    from aristos.visualize import render_quality_histogram, render_weight_comparison
    render_quality_histogram(feedbacks)
"""

from typing import Dict, List, Optional
from pathlib import Path


def render_quality_histogram(
    qualities: List[float],
    bins: int = 10,
    width: int = 40,
    title: str = "品質分布",
) -> str:
    """品質スコアの ASCII ヒストグラム

    Args:
        qualities: 品質スコアのリスト (0.0-1.0)
        bins: ビン数
        width: バーの最大幅 (文字数)
        title: タイトル

    Returns:
        ASCII ヒストグラム文字列
    """
    if not qualities:
        return f"  {title}: データなし"

    # ビンニング
    bin_size = 1.0 / bins
    counts = [0] * bins
    for q in qualities:
        idx = min(int(q / bin_size), bins - 1)
        counts[idx] += 1

    max_count = max(counts) if counts else 1
    lines = [f"  {title} (n={len(qualities)})"]
    lines.append(f"  {'─' * (width + 20)}")

    for i, count in enumerate(counts):
        lo = i * bin_size
        hi = (i + 1) * bin_size
        bar_len = int(count / max_count * width) if max_count > 0 else 0
        bar = "█" * bar_len
        label = f"  {lo:.1f}-{hi:.1f}"
        lines.append(f"{label} │{bar} {count}")

    lines.append(f"  {'─' * (width + 20)}")
    return "\n".join(lines)


def render_weight_comparison(
    evolved: Dict[str, float],
    default: Dict[str, float],
    width: int = 30,
    title: str = "重み比較 (evolved vs default)",
) -> str:
    """evolved vs default 重みの ASCII 棒グラフ

    Args:
        evolved: 進化済み重み
        default: デフォルト重み
        width: バーの最大幅
        title: タイトル

    Returns:
        比較チャート文字列
    """
    if not evolved and not default:
        return f"  {title}: データなし"

    all_keys = sorted(set(list(evolved.keys()) + list(default.keys())))
    max_val = max(
        max(evolved.values(), default=0),
        max(default.values(), default=0),
        0.001,
    )

    lines = [f"  {title}"]
    lines.append(f"  {'─' * (width + 25)}")

    for key in all_keys:
        ev = evolved.get(key, 0.0)
        df = default.get(key, 0.0)
        ev_bar = int(ev / max_val * width)
        df_bar = int(df / max_val * width)
        diff = ev - df
        marker = "↑" if diff > 0.01 else "↓" if diff < -0.01 else "="

        lines.append(f"  {key:>12}")
        lines.append(f"    evolved │{'█' * ev_bar} {ev:.3f}")
        lines.append(f"    default │{'░' * df_bar} {df:.3f} {marker}")

    lines.append(f"  {'─' * (width + 25)}")
    return "\n".join(lines)


def render_depth_distribution(
    distribution: Dict[str, int],
    width: int = 30,
    title: str = "深度分布",
) -> str:
    """深度分布の横棒グラフ

    Args:
        distribution: 深度レベル → カウント
        width: バーの最大幅

    Returns:
        分布チャート文字列
    """
    if not distribution:
        return f"  {title}: データなし"

    max_count = max(distribution.values(), default=1)
    total = sum(distribution.values())
    lines = [f"  {title} (total={total})"]
    lines.append(f"  {'─' * (width + 20)}")

    for depth in sorted(distribution.keys()):
        count = distribution[depth]
        bar_len = int(count / max_count * width) if max_count > 0 else 0
        pct = count / total * 100 if total > 0 else 0
        lines.append(f"  {depth:>4} │{'█' * bar_len} {count} ({pct:.0f}%)")

    lines.append(f"  {'─' * (width + 20)}")
    return "\n".join(lines)


def render_full_report(
    base_dir: Optional[Path] = None,
) -> str:
    """全統計の統合レポート"""
    try:
        from .status import get_aristos_status
        status = get_aristos_status(base_dir=base_dir)
    except ImportError:
        return "  ⚠️ aristos.status が利用できません"

    sections = []
    sections.append("╔══════════════════════════════════════╗")
    sections.append("║     Aristos Visualization Report     ║")
    sections.append("╚══════════════════════════════════════╝")

    # 品質ヒストグラム
    fb = status.feedback
    if fb.total_count > 0:
        # quality 値を再構成 (status から直接は取得できないため概算)
        sections.append(f"\n  📊 フィードバック概要")
        sections.append(f"    件数: {fb.total_count}")
        sections.append(f"    平均品質: {fb.avg_quality:.3f}")
        sections.append(f"    高品質 (>0.7): {fb.high_quality_count}")
        sections.append(f"    低品質 (<0.3): {fb.low_quality_count}")

        # 深度分布
        if fb.depth_distribution:
            sections.append("")
            sections.append(render_depth_distribution(fb.depth_distribution))
    else:
        sections.append("\n  📊 フィードバック: 未収集")

    # 重み比較
    ew = status.evolved_weights
    if ew.available:
        sections.append("")
        sections.append(render_weight_comparison(
            evolved=ew.weights,
            default=status.default_weights,
        ))
    else:
        sections.append("\n  🧬 進化済み重み: 未進化")

    return "\n".join(sections)
