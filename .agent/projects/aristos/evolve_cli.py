#!/usr/bin/env python3
"""Aristos Evolution CLI

GA 進化を手動実行し、重みを最適化する。

Modes:
    derivative (L2): derivative_selector の重みを最適化
    pt (L3):         CostCalculator のスカラー重みを最適化

Usage:
    python evolve_cli.py --theorem O1 --gen 50         # L2: 派生重み
    python evolve_cli.py --all --gen 20                # L2: 全定理
    python evolve_cli.py --mode pt --gen 30            # L3: コスト重み
    python evolve_cli.py --status
    python evolve_cli.py --convert-feedback
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

import yaml

# プロジェクトルートを PATH に追加
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # hegemonikon/
PROJECTS_DIR = Path(__file__).resolve().parents[1]   # .agent/projects/
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECTS_DIR))

from aristos.evolve import (  # noqa: E402
    Chromosome,
    EvolutionEngine,
    FeedbackCollector,
    FeedbackEntry,
    FitnessVector,
    Scale,
)

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
MNEME_DIR = Path("/home/makaron8426/oikos/mneme/.hegemonikon")
SELECTION_LOG = MNEME_DIR / "derivative_selections.yaml"
FEEDBACK_JSON = MNEME_DIR / "feedback.json"
EVOLVED_WEIGHTS = MNEME_DIR / "evolved_weights.json"

# 24 定理のコード一覧
ALL_THEOREMS = [
    "O1", "O2", "O3", "O4",
    "S1", "S2", "S3", "S4",
    "H1", "H2", "H3", "H4",
    "P1", "P2", "P3", "P4",
    "K1", "K2", "K3", "K4",
    "A1", "A2", "A3", "A4",
]

# 定理 → 派生コードのマッピング (derivative_selector.py のパターンキーと一致させる)
# NOTE: v2 — derivative_selector.py の実際のパターン辞書から抽出 (2026-02-15)
THEOREM_DERIVATIVES: Dict[str, List[str]] = {
    "O1": ["nous", "phro", "meta"],
    "O2": ["desir", "voli", "akra"],
    "O3": ["anom", "hypo", "eval"],
    "O4": ["flow", "prax", "pois"],
    "S1": ["cont", "disc", "abst"],
    "S2": ["comp", "inve", "adap"],
    "S3": ["norm", "empi", "rela"],
    "S4": ["prax", "pois", "temp"],
    "H1": ["appr", "avoi", "arre"],
    "H2": ["subj", "inte", "obje"],
    "H3": ["targ", "acti", "stat"],
    "H4": ["sens", "conc", "form"],
    "P1": ["phys", "conc", "rela"],
    "P2": ["line", "bran", "cycl"],
    "P3": ["fixe", "adap", "emer"],
    "P4": ["manu", "mech", "auto"],
    "K1": ["urge", "opti", "miss"],
    "K2": ["shor", "medi", "long"],
    "K3": ["intr", "inst", "ulti"],
    "K4": ["taci", "expl", "meta"],
    "A1": ["prim", "seco", "regu"],
    "A2": ["affi", "nega", "susp"],
    "A3": ["conc", "abst", "univ"],
    "A4": ["tent", "just", "cert"],
}


def convert_yaml_to_feedback() -> List[FeedbackEntry]:
    """YAML 選択ログを FeedbackEntry に変換"""
    if not SELECTION_LOG.exists():
        print(f"  ログ未検出: {SELECTION_LOG}")
        return []

    try:
        with open(SELECTION_LOG, "rb") as f:
            raw = f.read()
        # null バイト除去 (バイナリレベル)
        raw = raw.replace(b"\x00", b"")
        content = raw.decode("utf-8", errors="replace")
        data = yaml.safe_load(content)
    except Exception:
        # YAML パーサー失敗 → 正規表現で直接抽出
        print("  YAML パーサー失敗 — 正規表現フォールバック")
        import re as _re
        with open(SELECTION_LOG, "rb") as f:
            raw = f.read()
        content = raw.replace(b"\x00", b"").decode("utf-8", errors="replace")
        pattern = _re.compile(
            r"- confidence:\s*([\d.]+)\s*\n"
            r"\s+derivative:\s*(\S+)\s*\n"
            r"\s+method:\s*(\S+)\s*\n"
            r"\s+problem:\s*(.*?)\s*\n"
            r"\s+theorem:\s*(\S+)\s*\n"
            r"\s+timestamp:\s*'?\"?([^'\"\n]+)",
            _re.MULTILINE,
        )
        matches = pattern.findall(content)
        if not matches:
            print("  正規表現でも抽出失敗")
            return []
        entries = []
        for m in matches:
            entries.append(
                FeedbackEntry(
                    theorem=m[4], problem=m[3], selected=m[1],
                    corrected_to=None, confidence=float(m[0]), method=m[2],
                )
            )
        print(f"  {len(entries)} 件のフィードバックを正規表現で抽出")
        collector = FeedbackCollector(FEEDBACK_JSON)
        for entry in entries:
            collector.add(entry)
        collector.save()
        print(f"  保存先: {FEEDBACK_JSON}")
        return entries

    if not data or not isinstance(data.get("selections"), list):
        print("  ログが空またはフォーマットエラー")
        return []

    entries = []
    for item in data["selections"]:
        entries.append(
            FeedbackEntry(
                theorem=item.get("theorem", ""),
                problem=item.get("problem", ""),
                selected=item.get("derivative", ""),
                corrected_to=item.get("corrected_to"),
                confidence=item.get("confidence", 0.0),
                method=item.get("method", "keyword"),
            )
        )

    print(f"  {len(entries)} 件のフィードバックを変換")

    # FeedbackCollector 形式で保存
    collector = FeedbackCollector(FEEDBACK_JSON)
    for entry in entries:
        collector.add(entry)
    collector.save()
    print(f"  保存先: {FEEDBACK_JSON}")

    return entries


def get_gene_keys(theorem: str) -> List[str]:
    """定理の派生コードから gene keys を生成

    Format: "theorem:derivative" (e.g., "O1:nous")
    """
    derivs = THEOREM_DERIVATIVES.get(theorem, [])
    return [f"{theorem}:{d}" for d in derivs]


def run_evolution(
    theorem: str,
    generations: int = 50,
    pop_size: int = 20,
    dry_run: bool = False,
) -> Optional[Chromosome]:
    """特定の定理に対して GA 進化を実行"""
    print(f"\n{'='*50}")
    print(f"  定理: {theorem}")
    print(f"  世代数: {generations}")
    print(f"  個体数: {pop_size}")
    print(f"{'='*50}")

    # フィードバック読み込み
    collector = FeedbackCollector(FEEDBACK_JSON)
    feedback = collector.load()
    theorem_feedback = [e for e in feedback if e.theorem == theorem]

    if not theorem_feedback:
        print(f"  ⚠ {theorem} のフィードバックなし — 合成データで初期進化")
        # フィードバックなしでも初期進化は実行可能 (default fitness)

    print(f"  フィードバック: {len(theorem_feedback)} 件")

    # Gene keys
    gene_keys = get_gene_keys(theorem)
    if not gene_keys:
        print(f"  ❌ {theorem} に対応する派生が見つかりません")
        return None

    print(f"  遺伝子: {gene_keys}")

    # 進化エンジン
    engine = EvolutionEngine(scale=Scale.MICRO)

    # 既存重みがあれば初期個体に注入
    existing_weights = load_current_weights(theorem)
    population = engine.create_population(gene_keys, pop_size)
    if existing_weights:
        # 最良個体を既存重みで初期化
        population[0].genes = existing_weights
        print(f"  既存重み注入: {existing_weights}")

    # 進化実行
    final_pop = engine.evolve(population, theorem_feedback, generations)
    best = final_pop[0]

    print(f"\n  ── 結果 ──")
    print(f"  最良適合度: {best.fitness}")
    print(f"  最良重み:")
    for key, val in sorted(best.genes.items()):
        print(f"    {key}: {val:.4f}")

    if not dry_run:
        save_evolved_weights(theorem, best)
        print(f"  ✅ 重み保存: {EVOLVED_WEIGHTS}")

    return best


def load_current_weights(theorem: str) -> Optional[Dict[str, float]]:
    """現在の進化済み重みを読み込み (該当定理のみ)"""
    if not EVOLVED_WEIGHTS.exists():
        return None

    try:
        with open(EVOLVED_WEIGHTS, "r", encoding="utf-8") as f:
            data = json.load(f)
        weights = data.get("weights", {})
        # theorem: prefix のキーだけ抽出
        return {k: v for k, v in weights.items() if k.startswith(f"{theorem}:")}
    except (json.JSONDecodeError, KeyError):
        return None


def save_evolved_weights(theorem: str, best: Chromosome) -> None:
    """進化済み重みを保存 (既存の他定理の重みとマージ)"""
    existing = {}
    if EVOLVED_WEIGHTS.exists():
        try:
            with open(EVOLVED_WEIGHTS, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except (json.JSONDecodeError, KeyError):
            existing = {}

    # 既存重みから、この定理以外のものを保持
    weights = existing.get("weights", {})
    # 古い定理の重みを削除
    weights = {k: v for k, v in weights.items() if not k.startswith(f"{theorem}:")}
    # 新しい重みをマージ
    weights.update(best.genes)

    # fitness 情報も保存
    fitness_info = existing.get("fitness_by_theorem", {})
    fitness_info[theorem] = {
        "depth": best.fitness.depth,
        "precision": best.fitness.precision,
        "efficiency": best.fitness.efficiency,
        "novelty": best.fitness.novelty,
        "scalar": best.fitness.scalar(),
        "generation": best.generation,
    }

    data = {
        "weights": weights,
        "fitness_by_theorem": fitness_info,
    }

    EVOLVED_WEIGHTS.parent.mkdir(parents=True, exist_ok=True)
    with open(EVOLVED_WEIGHTS, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def show_status() -> None:
    """現在の重みとフィードバック状況を表示"""
    print("\n╔══════════════════════════════════════╗")
    print("║   Aristos L2 Evolution Engine Status ║")
    print("╚══════════════════════════════════════╝")

    # フィードバック状況
    print("\n📊 フィードバック:")
    if SELECTION_LOG.exists():
        try:
            with open(SELECTION_LOG, "r", encoding="utf-8", errors="replace") as f:
                content = f.read().replace("\x00", "")  # null バイト除去
            data = yaml.safe_load(content)
            selections = data.get("selections", []) if data else []
            print(f"  YAML ログ: {len(selections)} 件")

            # 定理別集計
            from collections import Counter
            theorem_counts = Counter(s.get("theorem", "?") for s in selections)
            corrections = sum(1 for s in selections if s.get("corrected_to"))
            print(f"  修正 (explicit): {corrections} 件")
            print(f"  定理別:")
            for th, cnt in sorted(theorem_counts.items()):
                print(f"    {th}: {cnt} 件")
        except Exception as e:
            print(f"  YAML ログ読み込みエラー: {e}")
    else:
        print(f"  YAML ログ未検出: {SELECTION_LOG}")

    if FEEDBACK_JSON.exists():
        collector = FeedbackCollector(FEEDBACK_JSON)
        entries = collector.load()
        print(f"  JSON フィードバック: {len(entries)} 件")
    else:
        print(f"  JSON フィードバック: 未変換")

    # 進化済み重み (L2: derivative)
    print(f"\n🧬 進化済み重み (L2 Derivative):")
    if EVOLVED_WEIGHTS.exists():
        with open(EVOLVED_WEIGHTS, "r", encoding="utf-8") as f:
            data = json.load(f)
        weights = data.get("weights", {})
        fitness = data.get("fitness_by_theorem", {})
        print(f"  重み数: {len(weights)}")
        for th, info in sorted(fitness.items()):
            scalar = info.get("scalar", 0.0)
            gen = info.get("generation", 0)
            print(f"    {th}: scalar={scalar:.3f}, gen={gen}")
    else:
        print(f"  未進化 (初回 --theorem/--all で進化を実行)")

    # 進化済み重み & フィードバック (L3: PT cost) — 統合ステータス
    print(f"\n🧬 L3 PT Optimization Status:")
    try:
        from aristos.status import get_aristos_status
        status = get_aristos_status()

        # Evolved Weights
        ew = status.evolved_weights
        if ew.available:
            print(f"  ✅ 進化済み重み (gen={ew.generation}, fitness={ew.fitness_scalar:.3f})")
            for k, v in sorted(ew.weights.items()):
                default_v = status.default_weights.get(k, 0.0)
                diff = v - default_v
                marker = "↑" if diff > 0.01 else "↓" if diff < -0.01 else "="
                print(f"    {k}: {v:.3f} ({marker} default={default_v:.1f})")
        else:
            print(f"  ⬜ 未進化 (--mode pt で進化を実行)")

        # Feedback Stats
        fb = status.feedback
        print(f"\n  📊 ルーティングフィードバック:")
        print(f"    件数: {fb.total_count}")
        if fb.total_count > 0:
            print(f"    平均品質: {fb.avg_quality:.3f}")
            print(f"    高品質 (>0.7): {fb.high_quality_count}")
            print(f"    低品質 (<0.3): {fb.low_quality_count}")
            if fb.depth_distribution:
                dist_str = ", ".join(
                    f"{d}={c}" for d, c in sorted(fb.depth_distribution.items())
                )
                print(f"    深度分布: {dist_str}")
        else:
            print(f"    未収集")
    except ImportError:
        print(f"  ⚠️ aristos.status モジュールが見つかりません")


def run_pt_evolution(
    generations: int = 30,
    pop_size: int = 30,
    dry_run: bool = False,
) -> None:
    """L3 PT コスト重み進化を実行"""
    from aristos.pt_optimizer import PTOptimizer
    from aristos.route_feedback import load_route_feedback

    cost_weights_path = MNEME_DIR / "cost_weights.json"

    print(f"\n{'='*50}")
    print(f"  🧬 PT Cost Weight Evolution (L3)")
    print(f"  世代: {generations}, 個体: {pop_size}")
    print(f"{'='*50}")

    # フィードバック読込
    route_fb_path = MNEME_DIR / "route_feedback.yaml"
    feedbacks = load_route_feedback(route_fb_path)
    print(f"\n📊 ルーティングフィードバック: {len(feedbacks)} 件")

    if not feedbacks:
        print("⚠️  フィードバックなし — ダミー進化 (baselineのみ)")

    # PT Optimizer 実行
    opt = PTOptimizer(
        population_size=pop_size,
        weights_path=cost_weights_path,
    )
    best = opt.optimize(feedbacks, generations=generations)

    print(f"\n🏆 最適重み:")
    for k, v in sorted(best.genes.items()):
        print(f"    {k}: {v:.3f}")
    print(f"  fitness: {best.fitness.scalar():.3f}")

    if dry_run:
        print("\n⚠️  --dry-run: 保存をスキップ")
    else:
        opt.save_weights(best)
        print(f"\n💾 保存先: {cost_weights_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Aristos Evolution CLI (L2 Derivative + L3 PT Cost)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python evolve_cli.py --status                  # 現状確認
  python evolve_cli.py --convert-feedback         # YAML → JSON 変換
  python evolve_cli.py --theorem O1 --gen 50      # L2: O1 を 50 世代進化
  python evolve_cli.py --all --gen 20             # L2: 全定理を 20 世代進化
  python evolve_cli.py --mode pt --gen 30         # L3: コスト重みを 30 世代進化
  python evolve_cli.py --theorem O1 --dry-run     # 保存せず進化結果のみ表示
        """,
    )
    parser.add_argument("--mode", choices=["derivative", "pt"], default="derivative",
                        help="進化モード: derivative (L2) or pt (L3, default: derivative)")
    parser.add_argument("--theorem", type=str, help="進化させる定理 (e.g., O1, S2, mode=derivative のみ)")
    parser.add_argument("--all", action="store_true", help="全 24 定理を進化 (mode=derivative のみ)")
    parser.add_argument("--gen", type=int, default=50, help="世代数 (default: 50)")
    parser.add_argument("--pop", type=int, default=20, help="個体数 (default: 20)")
    parser.add_argument("--status", action="store_true", help="現在の状態を表示")
    parser.add_argument("--viz", action="store_true", help="フィードバック統計を可視化")
    parser.add_argument("--convert-feedback", action="store_true", help="YAML → JSON 変換")
    parser.add_argument("--dry-run", action="store_true", help="進化結果を表示のみ")

    args = parser.parse_args()

    if args.status:
        show_status()
        return

    if args.viz:
        try:
            from aristos.visualize import render_full_report
            print(render_full_report())
        except ImportError:
            print("⚠️ aristos.visualize が利用できません")
        return

    if args.convert_feedback:
        print("📥 フィードバック変換:")
        convert_yaml_to_feedback()
        return

    # L3 PT mode
    if args.mode == "pt":
        run_pt_evolution(args.gen, args.pop, args.dry_run)
        return

    # L2 Derivative mode (default)
    if args.theorem:
        theorem = args.theorem.upper()
        if theorem not in ALL_THEOREMS:
            print(f"❌ 不明な定理: {theorem}")
            print(f"   有効な定理: {', '.join(ALL_THEOREMS)}")
            sys.exit(1)

        # フィードバック変換 (最新を取り込み)
        print("📥 フィードバック変換:")
        convert_yaml_to_feedback()

        run_evolution(theorem, args.gen, args.pop, args.dry_run)
        return

    if args.all:
        # フィードバック変換
        print("📥 フィードバック変換:")
        convert_yaml_to_feedback()

        results = {}
        for theorem in ALL_THEOREMS:
            best = run_evolution(theorem, args.gen, args.pop, args.dry_run)
            if best:
                results[theorem] = best.fitness.scalar()

        print(f"\n{'='*50}")
        print("  全定理進化完了")
        print(f"{'='*50}")
        for th, scalar in sorted(results.items(), key=lambda x: x[1], reverse=True):
            print(f"  {th}: scalar = {scalar:.3f}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
