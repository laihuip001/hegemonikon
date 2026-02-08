#!/usr/bin/env python3
"""Unseen input validation — exemplar/benchmark と重複しない入力で精度を検証.

PURPOSE: multi-prototype の overfitting 検知。
REASON: exemplar ↔ benchmark の近接性が 97% を膨らませている可能性がある。
"""
import sys
import time

sys.path.insert(0, ".")

# 18 cases: 3 per series, all novel phrasing
# Creator の日常的な発言パターンに近い自然文
VALIDATION_CASES = [
    # --- O (Ousia: 本質) ---
    {"input": "そもそもこのプロジェクトは誰のためにあるの", "expected": "O"},
    {"input": "根本から考え直した方がいいかもしれない", "expected": "O"},
    {"input": "この仕組みの存在意義って結局なんだ", "expected": "O"},

    # --- S (Schema: 様態) ---
    {"input": "まずディレクトリ構成を決めてからコーディングしよう", "expected": "S"},
    {"input": "REST APIのエンドポイント設計をしたい", "expected": "S"},
    {"input": "マイクロサービスかモノリスか、方針を決める", "expected": "S"},

    # --- H (Hormē: 動機) ---
    {"input": "正直、最近やる気が出なくて困ってる", "expected": "H"},
    {"input": "なんかうまくいきそうな予感がする", "expected": "H"},
    {"input": "このバグ、イライラしてきた", "expected": "H"},

    # --- P (Perigraphē: 条件) ---
    {"input": "Windows版もサポートすべきか悩んでいる", "expected": "P"},
    {"input": "このAPIは社内限定にするか外部公開するか", "expected": "P"},
    {"input": "テスト環境はDockerで統一する方針で", "expected": "P"},

    # --- K (Kairos: 文脈) ---
    {"input": "来月のリリースに間に合うか確認したい", "expected": "K"},
    {"input": "競合他社がどうやってるか調べてほしい", "expected": "K"},
    {"input": "この機能、今入れるべきか次のスプリントに回すか", "expected": "K"},

    # --- A (Akribeia: 精度) ---
    {"input": "プルリクのレビューコメントを見てほしい", "expected": "A"},
    {"input": "A案とB案、どっちがマシか判定して", "expected": "A"},
    {"input": "リグレッションテストを通して確認したい", "expected": "A"},
]


def run_validation():
    from mekhane.fep.attractor import SeriesAttractor

    sa = SeriesAttractor()
    sa._ensure_initialized()

    correct = 0
    errors = []
    total = len(VALIDATION_CASES)

    print("=" * 70)
    print("  Unseen Input Validation (overfitting check)")
    print("=" * 70)
    print()

    t0 = time.time()
    for case in VALIDATION_CASES:
        result = sa.diagnose(case["input"])
        got = result.primary.series if result.primary else "?"
        expected = case["expected"]
        ok = got == expected

        if ok:
            correct += 1
            mark = "✅"
        else:
            mark = "❌"
            errors.append(case | {"got": got, "sim": result.top_similarity})

        print(f"  {mark} [{expected}→{got}] sim={result.top_similarity:.3f} 「{case['input']}」")

    elapsed = time.time() - t0
    pct = correct / total * 100

    print()
    print(f"  正解率: {correct}/{total} ({pct:.0f}%)")
    print(f"  実行時間: {elapsed:.2f}s")
    print()

    if errors:
        print("  ❌ 不正解:")
        for e in errors:
            print(f"    {e['expected']}→{e['got']} (sim={e['sim']:.3f}) 「{e['input']}」")
    else:
        print("  🏆 全問正解!")

    print()
    print("=" * 70)

    # Verdict
    if pct >= 90:
        print("  VERDICT: ✅ Healthy — multi-prototype is NOT overfitting")
    elif pct >= 80:
        print("  VERDICT: ⚠️ Marginal — some exemplar bias may exist")
    else:
        print("  VERDICT: 🔴 Overfitting suspected — exemplars need abstraction")
    print("=" * 70)


if __name__ == "__main__":
    run_validation()
