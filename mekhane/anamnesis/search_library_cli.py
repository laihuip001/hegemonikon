#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/anamnesis/ A0→Library検索CLIが必要→search_library_cliが担う
"""
Library Search CLI — /lib ワークフローのバックエンド

USAGE:
    python mekhane/anamnesis/search_library_cli.py search "品質"
    python mekhane/anamnesis/search_library_cli.py mapping "/dia"
    python mekhane/anamnesis/search_library_cli.py semantic "開発プロトコル"
    python mekhane/anamnesis/search_library_cli.py detail "prompt_品質_敵対的レビュー凸"
    python mekhane/anamnesis/search_library_cli.py stats
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# PURPOSE: Layer 1: activation_triggers キーワード検索
def cmd_search(args):
    """Layer 1: activation_triggers キーワード検索"""
    from mekhane.anamnesis.library_search import LibrarySearch

    searcher = LibrarySearch()
    results = searcher.search_by_triggers(args.query, limit=args.limit)

    if not results:
        print(f"📚 '{args.query}' に一致するモジュールはありません")
        return

    print(f"📚 Library 検索結果: \"{args.query}\" ({len(results)}件)")
    print()
    print(f"{'#':>3} | {'モジュール':<30} | {'カテゴリ':<12} | HGK対応")
    print(f"{'─'*3}-+-{'─'*30}-+-{'─'*12}-+-{'─'*30}")

    for i, m in enumerate(results, 1):
        name = m.name[:28] if len(m.name) > 28 else m.name
        cat = m.category[:10] if len(m.category) > 10 else m.category
        mapping = m.hegemonikon_mapping[:28] if len(m.hegemonikon_mapping) > 28 else m.hegemonikon_mapping
        print(f"{i:>3} | {name:<30} | {cat:<12} | {mapping}")

    if args.verbose:
        print()
        for i, m in enumerate(results, 1):
            if m.essence:
                print(f"  [{i}] {m.name}")
                for line in m.essence.strip().split("\n")[:3]:
                    print(f"      {line.strip()}")
                print()


# PURPOSE: Layer 2: hegemonikon_mapping ベース WF 連携検索
def cmd_mapping(args):
    """Layer 2: hegemonikon_mapping ベース WF 連携検索"""
    from mekhane.anamnesis.library_search import LibrarySearch

    searcher = LibrarySearch()
    results = searcher.search_by_mapping(args.wf)

    if not results:
        print(f"📚 '{args.wf}' に対応するモジュールはありません")
        return

    print(f"📚 WF連携検索: \"{args.wf}\" ({len(results)}件)")
    print()

    for i, m in enumerate(results, 1):
        print(f"  {i}. [{m.hegemonikon_mapping}] {m.name}")
        if m.essence:
            essence_first = m.essence.strip().split("\n")[0][:80]
            print(f"     → {essence_first}")
        print(f"     📄 {m.filepath}")
        print()


# PURPOSE: Layer 3: セマンティック検索
def cmd_semantic(args):
    """Layer 3: セマンティック検索"""
    from mekhane.anamnesis.library_search import LibrarySearch

    searcher = LibrarySearch()
    results = searcher.search_semantic(args.query, limit=args.limit)

    if not results:
        print(f"📚 '{args.query}' に関連するモジュールはありません")
        return

    print(f"🔍 セマンティック検索: \"{args.query}\" ({len(results)}件)")
    print()

    for i, r in enumerate(results, 1):
        score = r["score"]
        name = r["name"]
        mapping = r["mapping"]
        essence = r["essence"][:100] if r["essence"] else ""

        print(f"  {i}. [{score:.3f}] {name}")
        print(f"     HGK: {mapping}")
        if essence:
            print(f"     → {essence}")
        print()


# PURPOSE: モジュール詳細表示
def cmd_detail(args):
    """モジュール詳細表示"""
    from mekhane.anamnesis.library_search import LibrarySearch

    searcher = LibrarySearch()
    module = searcher.get_module(args.module_id)

    if not module:
        print(f"❌ モジュール '{args.module_id}' が見つかりません")
        return

    print(f"📚 {module.name}")
    print(f"{'─'*50}")
    print(f"ID:       {module.id}")
    print(f"カテゴリ: {module.category}")
    print(f"HGK対応:  {module.hegemonikon_mapping}")
    print(f"原典:     {module.origin}")
    print(f"トリガー: {', '.join(module.activation_triggers)}")
    print(f"ファイル: {module.filepath}")
    print()

    if module.essence:
        print("── essence ──")
        print(module.essence.strip())
        print()

    if module.body:
        print("── 本文 (先頭500文字) ──")
        print(module.body[:500])


# PURPOSE: 統計情報
def cmd_stats(args):
    """統計情報"""
    from mekhane.anamnesis.library_search import LibrarySearch

    searcher = LibrarySearch()
    total = searcher.count()
    categories = searcher.list_categories()

    print(f"📊 Library 統計")
    print(f"{'─'*40}")
    print(f"  総モジュール数: {total}")
    print()
    print(f"  カテゴリ別:")
    for cat, count in categories.items():
        print(f"    {cat:<30} {count:>3}件")


# PURPOSE: 関数: main
def main():
    parser = argparse.ArgumentParser(
        description="Library Search CLI — /lib ワークフローのバックエンド",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="検索コマンド")

    # search
    p_search = subparsers.add_parser("search", help="キーワード検索 (Layer 1)")
    p_search.add_argument("query", help="検索キーワード")
    p_search.add_argument("-n", "--limit", type=int, default=20, help="最大件数")
    p_search.add_argument("-v", "--verbose", action="store_true", help="essence 表示")
    p_search.set_defaults(func=cmd_search)

    # mapping
    p_mapping = subparsers.add_parser("mapping", help="WF連携検索 (Layer 2)")
    p_mapping.add_argument("wf", help="WF名 (例: /dia, A2, O1)")
    p_mapping.set_defaults(func=cmd_mapping)

    # semantic
    p_semantic = subparsers.add_parser("semantic", help="セマンティック検索 (Layer 3)")
    p_semantic.add_argument("query", help="自然言語クエリ")
    p_semantic.add_argument("-n", "--limit", type=int, default=5, help="最大件数")
    p_semantic.set_defaults(func=cmd_semantic)

    # detail
    p_detail = subparsers.add_parser("detail", help="モジュール詳細")
    p_detail.add_argument("module_id", help="モジュールID")
    p_detail.set_defaults(func=cmd_detail)

    # stats
    p_stats = subparsers.add_parser("stats", help="統計情報")
    p_stats.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    import warnings
    warnings.filterwarnings("ignore")

    args.func(args)


if __name__ == "__main__":
    main()
