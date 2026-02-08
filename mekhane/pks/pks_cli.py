# noqa: AI-ALL
# PROOF: [L2/インフラ] <- mekhane/pks/
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

A0 (FEP) → 能動的知識表面化には操作インターフェースが必要
→ pks_cli.py が担う

# PURPOSE: PKS v2 CLI — 能動的知識プッシュの対話インターフェース
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_PKS_DIR = Path(__file__).resolve().parent
_MEKHANE_DIR = _PKS_DIR.parent
_HEGEMONIKON_ROOT = _MEKHANE_DIR.parent

if str(_HEGEMONIKON_ROOT) not in sys.path:
    sys.path.insert(0, str(_HEGEMONIKON_ROOT))


# PURPOSE: `pks push` — コンテキストに基づく能動的プッシュ
def cmd_push(args: argparse.Namespace) -> None:
    """コンテキストに基づく能動的プッシュ"""
    from mekhane.pks.pks_engine import PKSEngine

    engine = PKSEngine(
        threshold=args.threshold,
        max_push=args.max,
        enable_questions=not args.no_questions,
        enable_serendipity=True,
    )

    if args.topics:
        topics = [t.strip() for t in args.topics.split(",")]
        engine.set_context(topics=topics)
        print(f"[PKS] トピック設定: {topics}")
    elif args.auto:
        topics = engine.auto_context_from_handoff()
        if not topics:
            print("[PKS] Handoff からのトピック抽出に失敗しました。--topics を指定してください。")
            return
    elif hasattr(args, 'infer') and args.infer:
        user_input = args.infer
        topics = engine.auto_context_from_input(user_input)
        if not topics:
            print("[PKS] Attractor によるコンテキスト推論に失敗しました。")
            return
    else:
        print("[PKS] --topics / --auto / --infer を指定してください。")
        return

    print("[PKS] Gnōsis 検索中...")
    nuggets = engine.proactive_push(k=args.k)

    if not nuggets:
        print("📭 プッシュ対象の知識はありません。")
        return

    # 質問生成
    if not args.no_questions:
        print("[PKS] 質問生成中...")
        nuggets = engine.suggest_questions(nuggets)

    # レポート出力
    report = engine.format_push_report(nuggets)
    print(report)


# PURPOSE: `pks suggest` — トピック指定で「聞くべき質問」を生成
def cmd_suggest(args: argparse.Namespace) -> None:
    """トピック指定で「聞くべき質問」を生成"""
    from mekhane.pks.pks_engine import PKSEngine

    engine = PKSEngine(enable_questions=True, enable_serendipity=False)

    topic = args.topic
    engine.set_context(topics=[topic])

    print(f"[PKS] '{topic}' に関する知識を検索中...")
    nuggets = engine.search_and_push(topic, k=args.k)

    if not nuggets:
        print(f"📭 '{topic}' に関連する知識がありません。")
        return

    # 上位 N 件に質問を生成
    top_nuggets = nuggets[: args.max]
    top_nuggets = engine.suggest_questions(top_nuggets)

    for i, nugget in enumerate(top_nuggets, 1):
        print(f"\n### [{i}] {nugget.title}")
        print(f"_関連度: {nugget.relevance_score:.2f} | ソース: {nugget.source}_")
        if nugget.suggested_questions:
            print("\n**💡 聞くべき質問:**")
            for q in nugget.suggested_questions:
                print(f"  - {q}")
    print()


# PURPOSE: `pks backlinks` — 擬似バックリンクを表示
def cmd_backlinks(args: argparse.Namespace) -> None:
    """指定トピックの擬似バックリンクを表示"""
    from mekhane.pks.matrix_view import PKSBacklinks
    from mekhane.pks.pks_engine import PKSEngine

    engine = PKSEngine(enable_questions=False, enable_serendipity=False)

    query = args.query
    print(f"[PKS] '{query}' の擬似バックリンクを検索中...")

    nuggets = engine.search_and_push(query, k=args.k)

    if not nuggets:
        print(f"📭 '{query}' に関連する知識がありません。")
        return

    backlinks = PKSBacklinks()
    report = backlinks.generate(query, nuggets)
    print(report)


# PURPOSE: `pks auto` — Handoff から自動でプッシュ
def cmd_auto(args: argparse.Namespace) -> None:
    """Handoff から自動的にトピック抽出してプッシュ"""
    from mekhane.pks.pks_engine import PKSEngine

    engine = PKSEngine(
        enable_questions=not args.no_questions,
        enable_serendipity=True,
    )

    topics = engine.auto_context_from_handoff()
    if not topics:
        print("📭 Handoff からのトピック抽出に失敗しました。")
        return

    print(f"[PKS] 抽出トピック: {topics}")
    print("[PKS] Gnōsis 検索中...")

    nuggets = engine.proactive_push(k=args.k)

    if not nuggets:
        print("📭 プッシュ対象の知識はありません。")
        return

    if not args.no_questions:
        print("[PKS] 質問生成中...")
        nuggets = engine.suggest_questions(nuggets)

    report = engine.format_push_report(nuggets)
    print(report)


# PURPOSE: `pks infer` — Attractor ベースのコンテキスト推論 + プッシュ
def cmd_infer(args: argparse.Namespace) -> None:
    """ユーザー入力から Attractor でコンテキスト推論してプッシュ"""
    from mekhane.pks.pks_engine import PKSEngine

    engine = PKSEngine(
        enable_questions=not args.no_questions,
        enable_serendipity=True,
    )

    user_input = " ".join(args.input)
    topics = engine.auto_context_from_input(user_input)
    if not topics:
        print("📭 Attractor コンテキスト推論に失敗しました。")
        return

    print(f"[PKS] 推論トピック: {topics}")
    print("[PKS] Gnōsis 検索中...")

    nuggets = engine.proactive_push(k=args.k)

    if not nuggets:
        print("📭 プッシュ対象の知識はありません。")
        return

    if not args.no_questions:
        print("[PKS] 質問生成中...")
        nuggets = engine.suggest_questions(nuggets)

    report = engine.format_push_report(nuggets)
    print(report)


# PURPOSE: `pks feedback` — プッシュ反応を記録
def cmd_feedback(args: argparse.Namespace) -> None:
    """プッシュされた知識へのリアクションを記録"""
    from mekhane.pks.pks_engine import PKSEngine

    engine = PKSEngine(
        enable_questions=False,
        enable_serendipity=False,
        enable_feedback=True,
    )

    if args.stats:
        # 統計表示
        if engine._feedback:
            stats = engine._feedback.get_stats()
            if not stats:
                print("📭 フィードバック履歴がありません。")
                return
            print("## 📊 PKS Feedback Stats\n")
            print("| Series | Count | Avg Score | Threshold Adj |")
            print("|:------:|------:|----------:|--------------:|")
            for series, s in sorted(stats.items()):
                adj = s['threshold_adjustment']
                sign = "+" if adj >= 0 else ""
                print(f"| {series} | {s['count']} | {s['avg_score']:.2f} | {sign}{adj:.3f} |")
        return

    # 反応記録
    engine.record_feedback(
        nugget_title=args.title,
        reaction=args.reaction,
        series=args.series or "",
    )
    print(f"✅ Feedback recorded: '{args.title}' → {args.reaction}")


# PURPOSE: メインエントリポイント
def main() -> None:
    """PKS CLI メインエントリポイント"""
    parser = argparse.ArgumentParser(
        description="PKS v2 — Proactive Knowledge Surface CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  pks push --topics 'FEP,CCL'     # 指定トピックでプッシュ\n"
            "  pks push --auto                  # Handoff から自動検出\n"
            "  pks push --infer 'FEPを調査'     # Attractor 推論でプッシュ\n"
            "  pks infer 'FEPの理論的基盤'       # Attractor 推論 + プッシュ\n"
            "  pks suggest 'Active Inference'   # 質問生成\n"
            "  pks backlinks 'FEP'              # 擬似バックリンク\n"
            "  pks auto                         # 全自動プッシュ\n"
            "  pks feedback -t 'paper' -r used   # 反応記録\n"
            "  pks feedback --stats              # 統計表示\n"
        ),
    )
    subparsers = parser.add_subparsers(dest="command", help="サブコマンド")

    # --- push ---
    p_push = subparsers.add_parser("push", help="能動的プッシュを実行")
    p_push.add_argument("--topics", "-t", help="トピック (カンマ区切り)")
    p_push.add_argument("--auto", "-a", action="store_true", help="Handoff からトピック自動抽出")
    p_push.add_argument("--infer", "-i", help="Attractor でコンテキスト推論 (テキスト入力)")
    p_push.add_argument("--threshold", type=float, default=0.65, help="関連度閾値 (default: 0.65)")
    p_push.add_argument("--max", "-m", type=int, default=5, help="最大プッシュ件数 (default: 5)")
    p_push.add_argument("--k", type=int, default=20, help="検索候補数 (default: 20)")
    p_push.add_argument("--no-questions", action="store_true", help="質問生成を無効化")
    p_push.set_defaults(func=cmd_push)

    # --- suggest ---
    p_suggest = subparsers.add_parser("suggest", help="「聞くべき質問」を生成")
    p_suggest.add_argument("topic", help="トピック")
    p_suggest.add_argument("--max", "-m", type=int, default=3, help="対象件数 (default: 3)")
    p_suggest.add_argument("--k", type=int, default=10, help="検索候補数 (default: 10)")
    p_suggest.set_defaults(func=cmd_suggest)

    # --- backlinks ---
    p_backlinks = subparsers.add_parser("backlinks", help="擬似バックリンクを表示")
    p_backlinks.add_argument("query", help="検索クエリ")
    p_backlinks.add_argument("--k", type=int, default=15, help="検索候補数 (default: 15)")
    p_backlinks.set_defaults(func=cmd_backlinks)

    # --- auto ---
    p_auto = subparsers.add_parser("auto", help="Handoff から全自動プッシュ")
    p_auto.add_argument("--k", type=int, default=20, help="検索候補数 (default: 20)")
    p_auto.add_argument("--no-questions", action="store_true", help="質問生成を無効化")
    p_auto.set_defaults(func=cmd_auto)

    # --- infer ---
    p_infer = subparsers.add_parser("infer", help="Attractor 推論でプッシュ")
    p_infer.add_argument("input", nargs="+", help="推論入力テキスト")
    p_infer.add_argument("--k", type=int, default=20, help="検索候補数 (default: 20)")
    p_infer.add_argument("--no-questions", action="store_true", help="質問生成を無効化")
    p_infer.set_defaults(func=cmd_infer)

    # --- feedback ---
    p_feedback = subparsers.add_parser("feedback", help="プッシュ反応を記録")
    p_feedback.add_argument("--title", "-t", help="ナゲットタイトル")
    p_feedback.add_argument(
        "--reaction", "-r",
        choices=["used", "dismissed", "deepened", "ignored"],
        help="反応タイプ",
    )
    p_feedback.add_argument("--series", "-s", help="Attractor series (任意)")
    p_feedback.add_argument("--stats", action="store_true", help="フィードバック統計を表示")
    p_feedback.set_defaults(func=cmd_feedback)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
