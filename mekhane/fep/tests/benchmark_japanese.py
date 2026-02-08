#!/usr/bin/env python3
# PROOF: [L3/テスト] <- mekhane/fep/tests/
# PURPOSE: FEP日本語処理のベンチマーク測定
"""
Attractor Engine 日本語入力ベンチマーク

100件の日本語入力に対して、SeriesAttractor の分類精度を定量評価する。
human-labeled expected Series と実際のアトラクター出力を比較し、
precision / recall / F1 / accuracy を算出する。

Usage:
    PYTHONPATH=. .venv/bin/python mekhane/fep/tests/benchmark_japanese.py

構成:
    - 6 Series × 15件 = 90件 (単一 Series に収束すべき入力)
    - 複合入力 5件 (2+ Series に収束すべき入力)
    - 曖昧/境界入力 5件 (分類困難 — 許容範囲内ならOK)
    計100件
"""

from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Benchmark Data: 100 Japanese Inputs
# ---------------------------------------------------------------------------

# (input_text, expected_primary_series, acceptable_series_set, category)
# expected_primary: 最も正しい Series
# acceptable: この中に含まれていれば正解とみなす (複合入力・曖昧入力用)
# category: "single" | "compound" | "ambiguous"

BENCHMARK_CASES: list[tuple[str, str, set[str], str]] = [
    # ===== O-series (Ousia / 本質) — 15件 =====
    ("このプロジェクトはなぜ存在するのか", "O", {"O"}, "single"),
    ("そもそも根本的な目的は何だろう", "O", {"O"}, "single"),
    ("本質的に何が問題なのか考えたい", "O", {"O"}, "single"),
    ("存在意義を深く問い直す必要がある", "O", {"O"}, "single"),
    ("第一原理から考え直そう", "O", {"O"}, "single"),
    ("なぜこの機能が必要なのか、根本から問う", "O", {"O"}, "single"),
    ("この概念の本質は何か", "O", {"O"}, "single"),
    ("意志と目的の関係を理解したい", "O", {"O"}, "single"),
    ("深い認識を得るために何が必要か", "O", {"O"}, "single"),
    ("このシステムの存在理由を再定義する", "O", {"O"}, "single"),
    ("パラダイム転換が必要ではないか", "O", {"O"}, "single"),
    ("行き詰まりの根本原因を探りたい", "O", {"O"}, "single"),
    ("私たちは何を見落としているのか", "O", {"O"}, "single"),
    ("前提を疑い、ゼロから再構築したい", "O", {"O"}, "single"),
    ("この問いの答えではなく、問い自体を問いたい", "O", {"O"}, "single"),

    # ===== S-series (Schema / 様態) — 15件 =====
    ("アーキテクチャを設計してほしい", "S", {"S"}, "single"),
    ("実装手順をステップバイステップで教えて", "S", {"S"}, "single"),
    ("このモジュールの構造を整理したい", "S", {"S"}, "single"),
    ("クラス設計をレビューしてください", "S", {"S"}, "single"),
    ("フレームワークの選定方法を教えて", "S", {"S"}, "single"),
    ("データベース設計のベストプラクティスは", "S", {"S"}, "single"),
    ("API の設計パターンを提案して", "S", {"S"}, "single"),
    ("リファクタリングの方針を決めたい", "S", {"S"}, "single"),
    ("このコードの構造を改善する方法は", "S", {"S"}, "single"),
    ("マイクロサービスに分割する手順は", "S", {"S"}, "single"),
    ("ディレクトリ構成を整理したい", "S", {"S"}, "single"),
    ("テスト戦略を設計する必要がある", "S", {"S"}, "single"),
    ("デプロイメントパイプラインを構築したい", "S", {"S"}, "single"),
    ("ERD を書いてデータモデルを定義する", "S", {"S"}, "single"),
    ("CI/CD の構成を最適化したい", "S", {"S"}, "single"),

    # ===== H-series (Hormē / 動機) — 15件 =====
    ("不安で仕方がない。このプロジェクト大丈夫かな", "H", {"H"}, "single"),
    ("モチベーションが下がっている", "H", {"H"}, "single"),
    ("直感的にこの方向は間違っている気がする", "H", {"H"}, "single"),
    ("確信が持てない。自信がない", "H", {"H"}, "single"),
    ("このアプローチに対する信念が揺らいでいる", "H", {"H"}, "single"),
    ("ワクワクする。この機能を作りたい", "H", {"H"}, "single"),
    ("疲れた。やる気が出ない", "H", {"H"}, "single"),
    ("怖い。失敗したらどうしよう", "H", {"H"}, "single"),
    ("この決断に対する感情を整理したい", "H", {"H"}, "single"),
    ("期待と不安が入り混じっている", "H", {"H"}, "single"),
    ("何かが引っかかる。違和感がある", "H", {"H"}, "single"),
    ("信頼していいのか迷っている", "H", {"H"}, "single"),
    ("情熱を持ってこの仕事に取り組みたい", "H", {"H"}, "single"),
    ("心配で夜も眠れない", "H", {"H"}, "single"),
    ("希望を持てるようになりたい", "H", {"H"}, "single"),

    # ===== P-series (Perigraphē / 条件) — 15件 =====
    ("このシステムのスコープを定義したい", "P", {"P"}, "single"),
    ("対象範囲はどこまでか明確にする", "P", {"P"}, "single"),
    ("境界条件を設定してほしい", "P", {"P"}, "single"),
    ("この機能は対象外にすべきか", "P", {"P"}, "single"),
    ("動作環境の制約を整理する", "P", {"P"}, "single"),
    ("どのリージョンにデプロイするか", "P", {"P"}, "single"),
    ("コンテキストの境界を明確にしたい", "P", {"P"}, "single"),
    ("このモジュールの責任範囲は", "P", {"P"}, "single"),
    ("制約条件をリストアップする", "P", {"P"}, "single"),
    ("入出力の境界を定義してください", "P", {"P"}, "single"),
    ("サポート対象のブラウザはどれか", "P", {"P"}, "single"),
    ("本番環境とステージング環境の違いは", "P", {"P"}, "single"),
    ("セキュリティ境界を設定する必要がある", "P", {"P"}, "single"),
    ("認可のスコープを絞りたい", "P", {"P"}, "single"),
    ("この機能のターゲットユーザーは誰か", "P", {"P"}, "single"),

    # ===== K-series (Kairos / 文脈) — 15件 =====
    ("今がこの機能を開発する適切なタイミングか", "K", {"K"}, "single"),
    ("締め切りはいつですか", "K", {"K"}, "single"),
    ("このトピックについて調査してほしい", "K", {"K"}, "single"),
    ("関連する論文を探してください", "K", {"K"}, "single"),
    ("スケジュールの優先度を再検討したい", "K", {"K"}, "single"),
    ("今すぐやるべきか、後回しにすべきか", "K", {"K"}, "single"),
    ("この技術の最新動向を教えて", "K", {"K"}, "single"),
    ("リリース時期を決定する必要がある", "K", {"K"}, "single"),
    ("先行研究を調べてからにしよう", "K", {"K"}, "single"),
    ("いつまでに完了させるべきか", "K", {"K"}, "single"),
    ("過去の事例を調査したい", "K", {"K"}, "single"),
    ("このタスクの緊急度はどれくらいか", "K", {"K"}, "single"),
    ("文献レビューをお願いします", "K", {"K"}, "single"),
    ("機会損失のリスクを見積もりたい", "K", {"K"}, "single"),
    ("この知識をどこかで学べないか", "K", {"K"}, "single"),

    # ===== A-series (Akribeia / 精度) — 15件 =====
    ("この実装は正しいか検証してほしい", "A", {"A"}, "single"),
    ("2つの選択肢を比較して判断したい", "A", {"A"}, "single"),
    ("品質基準を満たしているかチェックして", "A", {"A"}, "single"),
    ("この設計にはバグがないか精査して", "A", {"A"}, "single"),
    ("トレードオフを評価して最適解を選びたい", "A", {"A"}, "single"),
    ("コードレビューをお願いします", "A", {"A"}, "single"),
    ("テスト結果を評価してください", "A", {"A"}, "single"),
    ("この判断は妥当か批判的に見てほしい", "A", {"A"}, "single"),
    ("精度を上げるにはどうすればいいか", "A", {"A"}, "single"),
    ("エラー率を計測して許容範囲内か確認", "A", {"A"}, "single"),
    ("比較表を作ってベストを選定して", "A", {"A"}, "single"),
    ("この選択は間違っていないか", "A", {"A"}, "single"),
    ("性能ベンチマークを実行したい", "A", {"A"}, "single"),
    ("合格か不合格かを判定してください", "A", {"A"}, "single"),
    ("基準に照らして適切かどうか", "A", {"A"}, "single"),

    # ===== 複合入力 (Compound) — 5件 =====
    (
        "なぜこのシステムが必要なのか、そしてどう設計すべきか",
        "O", {"O", "S"}, "compound",
    ),
    (
        "締め切りに間に合うか不安だ。スケジュールを見直したい",
        "K", {"K", "H"}, "compound",
    ),
    (
        "このアーキテクチャは正しいのか、品質を評価してほしい",
        "A", {"A", "S"}, "compound",
    ),
    (
        "境界を定義してから、実装手順を考えたい",
        "P", {"P", "S"}, "compound",
    ),
    (
        "本質的な目的を再確認し、今やるべきか判断したい",
        "O", {"O", "K", "A"}, "compound",
    ),

    # ===== 曖昧/境界入力 — 5件 =====
    (
        "とりあえず進めよう",
        "O", {"O", "H", "S", "K"}, "ambiguous",  # 曖昧 — 多くが許容
    ),
    (
        "なんか違う気がする",
        "H", {"H", "O", "A"}, "ambiguous",  # 感情ベースだが認識かも
    ),
    (
        "これでいいのかな",
        "A", {"A", "H"}, "ambiguous",  # 判断 or 感情
    ),
    (
        "もっと良くできるはず",
        "A", {"A", "S", "O"}, "ambiguous",  # 品質 or 設計 or 本質
    ),
    (
        "よくわからない",
        "O", {"O", "H", "K"}, "ambiguous",  # 認識 or 感情 or 知識不足
    ),
]


# ---------------------------------------------------------------------------
# Evaluation Logic
# ---------------------------------------------------------------------------

@dataclass
class BenchmarkResult:
    """1件のベンチマーク結果"""
    input_text: str
    expected_primary: str
    acceptable_series: set[str]
    category: str
    predicted_primary: str
    predicted_series: list[str]
    top_similarity: float
    oscillation: str
    is_correct_primary: bool  # primary が expected と一致
    is_correct_acceptable: bool  # primary が acceptable set に含まれる


@dataclass
class BenchmarkReport:
    """全体レポート"""
    results: list[BenchmarkResult] = field(default_factory=list)
    per_series: dict[str, dict] = field(default_factory=dict)
    elapsed_seconds: float = 0.0

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def primary_accuracy(self) -> float:
        """expected_primary と predicted_primary が一致する割合"""
        correct = sum(1 for r in self.results if r.is_correct_primary)
        return correct / self.total if self.total else 0.0

    @property
    def acceptable_accuracy(self) -> float:
        """predicted_primary が acceptable set に含まれる割合"""
        correct = sum(1 for r in self.results if r.is_correct_acceptable)
        return correct / self.total if self.total else 0.0

    def by_category(self, category: str) -> list[BenchmarkResult]:
        return [r for r in self.results if r.category == category]


def compute_per_series_metrics(results: list[BenchmarkResult]) -> dict[str, dict]:
    """Series ごとの Precision / Recall / F1 を計算"""
    series_names = ["O", "S", "H", "P", "K", "A"]
    metrics = {}

    for series in series_names:
        # True Positives: expected=series AND predicted=series
        tp = sum(1 for r in results if r.expected_primary == series and r.predicted_primary == series)
        # False Positives: expected!=series BUT predicted=series
        fp = sum(1 for r in results if r.expected_primary != series and r.predicted_primary == series)
        # False Negatives: expected=series BUT predicted!=series
        fn = sum(1 for r in results if r.expected_primary == series and r.predicted_primary != series)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        metrics[series] = {
            "tp": tp, "fp": fp, "fn": fn,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }

    return metrics


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_benchmark() -> BenchmarkReport:
    """ベンチマーク実行"""
    from mekhane.fep.attractor import SeriesAttractor

    attractor = SeriesAttractor()
    report = BenchmarkReport()

    t0 = time.time()

    for text, expected, acceptable, category in BENCHMARK_CASES:
        result = attractor.diagnose(text)

        if result.attractors:
            predicted_primary = result.primary.series
            predicted_series = [r.series for r in result.attractors]
        else:
            predicted_primary = "?"
            predicted_series = []

        br = BenchmarkResult(
            input_text=text,
            expected_primary=expected,
            acceptable_series=acceptable,
            category=category,
            predicted_primary=predicted_primary,
            predicted_series=predicted_series,
            top_similarity=result.top_similarity,
            oscillation=result.oscillation.value,
            is_correct_primary=(predicted_primary == expected),
            is_correct_acceptable=(predicted_primary in acceptable),
        )
        report.results.append(br)

    report.elapsed_seconds = time.time() - t0
    report.per_series = compute_per_series_metrics(report.results)

    return report


def print_report(report: BenchmarkReport) -> None:
    """レポート表示"""
    print("=" * 72)
    print("  Attractor Engine 日本語ベンチマーク結果")
    print("=" * 72)
    print()

    # 全体精度
    print(f"  総件数:        {report.total}")
    print(f"  Primary 正解率: {report.primary_accuracy:.1%}")
    print(f"  許容 正解率:    {report.acceptable_accuracy:.1%}")
    print(f"  実行時間:       {report.elapsed_seconds:.2f}s")
    print()

    # カテゴリ別
    for cat in ["single", "compound", "ambiguous"]:
        items = report.by_category(cat)
        if not items:
            continue
        correct_p = sum(1 for r in items if r.is_correct_primary)
        correct_a = sum(1 for r in items if r.is_correct_acceptable)
        print(f"  [{cat:>9s}] {len(items):>3d}件 | "
              f"primary: {correct_p}/{len(items)} ({correct_p/len(items):.0%}) | "
              f"acceptable: {correct_a}/{len(items)} ({correct_a/len(items):.0%})")
    print()

    # Series 別 Precision/Recall/F1
    print("  Series別 (single入力 90件ベース):")
    print("  " + "-" * 60)
    print(f"  {'Series':6s} | {'Prec':>6s} | {'Recall':>6s} | {'F1':>6s} | {'TP':>3s} {'FP':>3s} {'FN':>3s}")
    print("  " + "-" * 60)
    for series in ["O", "S", "H", "P", "K", "A"]:
        m = report.per_series[series]
        print(f"  {series:6s} | {m['precision']:>6.0%} | {m['recall']:>6.0%} | "
              f"{m['f1']:>6.0%} | {m['tp']:>3d} {m['fp']:>3d} {m['fn']:>3d}")
    print("  " + "-" * 60)

    # Macro F1
    all_f1 = [report.per_series[s]["f1"] for s in ["O", "S", "H", "P", "K", "A"]]
    macro_f1 = sum(all_f1) / len(all_f1)
    print(f"  Macro F1: {macro_f1:.1%}")
    print()

    # 不正解リスト
    incorrect = [r for r in report.results if not r.is_correct_acceptable]
    if incorrect:
        print("  ❌ 不正解 (acceptable にも含まれない):")
        for r in incorrect:
            print(f"    [{r.category:>9s}] expected={r.expected_primary} got={r.predicted_primary} "
                  f"(sim={r.top_similarity:.3f} osc={r.oscillation}) "
                  f"「{r.input_text[:40]}」")
        print()

    # Similarity 統計
    sims = [r.top_similarity for r in report.results]
    print(f"  Similarity 統計: min={min(sims):.3f} max={max(sims):.3f} "
          f"mean={sum(sims)/len(sims):.3f} median={sorted(sims)[len(sims)//2]:.3f}")
    print()

    # confusion pattern
    confusion = defaultdict(int)
    for r in report.results:
        if not r.is_correct_primary:
            confusion[f"{r.expected_primary}→{r.predicted_primary}"] += 1
    if confusion:
        print("  混同パターン (top):")
        for pattern, count in sorted(confusion.items(), key=lambda x: -x[1])[:10]:
            print(f"    {pattern}: {count}件")
        print()

    print("=" * 72)

    # JSON 出力 (保存用)
    output_path = Path(__file__).parent / "benchmark_result.json"
    json_data = {
        "total": report.total,
        "primary_accuracy": round(report.primary_accuracy, 4),
        "acceptable_accuracy": round(report.acceptable_accuracy, 4),
        "macro_f1": round(macro_f1, 4),
        "elapsed_seconds": round(report.elapsed_seconds, 2),
        "per_series": {
            s: {
                "precision": round(m["precision"], 4),
                "recall": round(m["recall"], 4),
                "f1": round(m["f1"], 4),
            }
            for s, m in report.per_series.items()
        },
        "incorrect_count": len(incorrect),
    }
    output_path.write_text(json.dumps(json_data, indent=2, ensure_ascii=False))
    print(f"\n  📄 結果保存: {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n  🚀 Attractor Engine 日本語ベンチマーク 実行中...\n", file=sys.stderr)
    report = run_benchmark()
    print_report(report)
