#!/usr/bin/env python3
"""
Mnēmē Synthesis CLI - 統合セッション記憶インジェストツール

/boot から呼び出される Sophia/Kairos/Chronos 統合 CLI.

Usage:
    python mneme_cli.py ingest --all     # 全インデックス更新
    python mneme_cli.py ingest --sophia  # KI のみ
    python mneme_cli.py ingest --kairos  # Handoff のみ
    python mneme_cli.py stats            # 統計情報

Architecture:
    anamnesis/ = 記憶系 CLI 統合層
    symploke/  = ベクトルDB 実装詳細層
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add Hegemonikon root to path for imports
_THIS_DIR = Path(__file__).parent
_HEGEMONIKON_ROOT = _THIS_DIR.parent.parent  # mekhane/anamnesis -> mekhane -> Hegemonikon
if str(_HEGEMONIKON_ROOT) not in sys.path:
    sys.path.insert(0, str(_HEGEMONIKON_ROOT))

from mekhane.anamnesis.ux_utils import Colors, Spinner, print_header, print_success, print_error, print_warning, print_info


def cmd_ingest(args):
    """統合インジェスト実行"""
    results = {
        "chronos": 0,
        "sophia": 0,
        "kairos": 0,
    }
    
    # Sophia (Knowledge Items)
    if args.all or args.sophia:
        try:
            from mekhane.symploke.sophia_ingest import (
                get_ki_directories, 
                parse_ki_directory, 
                ingest_to_sophia,
                DEFAULT_INDEX_PATH
            )
            
            with Spinner("Indexing Sophia (Knowledge Items)..."):
                ki_dirs = get_ki_directories()
                all_docs = []
                for ki_dir in ki_dirs:
                    docs = parse_ki_directory(ki_dir)
                    all_docs.extend(docs)

                if all_docs:
                    # Ensure directory exists
                    DEFAULT_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
                    count = ingest_to_sophia(all_docs, save_path=str(DEFAULT_INDEX_PATH))
                    results["sophia"] = count
                else:
                    print_warning("[Sophia] No documents found")
        except ImportError as e:
            print_error(f"[Sophia] Import error: {e}")
        except Exception as e:
            print_error(f"[Sophia] Error: {e}")
    
    # Kairos (Handoffs)
    if args.all or args.kairos:
        try:
            from mekhane.symploke.kairos_ingest import (
                get_handoff_files,
                parse_handoff,
                ingest_to_kairos
            )
            
            with Spinner("Indexing Kairos (Handoffs)..."):
                files = get_handoff_files()
                if files:
                    docs = [parse_handoff(f) for f in files]
                    count = ingest_to_kairos(docs)
                    results["kairos"] = count
                else:
                    print_warning("[Kairos] No handoff files found")
        except ImportError as e:
            print_error(f"[Kairos] Import error: {e}")
        except Exception as e:
            print_error(f"[Kairos] Error: {e}")
    
    # Chronos (Conversation History) - Not yet implemented
    if args.all or args.chronos:
        # TODO: Implement when conversation history indexing is ready
        results["chronos"] = 0
    
    # Output in /boot expected format
    total = sum(results.values())
    print_header("Mnēmē Synthesis Results")
    print(f"  Chronos: {results['chronos']} documents")
    print(f"  Sophia:  {results['sophia']} documents")
    print(f"  Kairos:  {results['kairos']} documents")
    print(f"  {Colors.BOLD}Total:   {total} documents{Colors.ENDC}")
    
    return 0


def cmd_stats(args):
    """統計情報表示"""
    from mekhane.symploke.sophia_ingest import DEFAULT_INDEX_PATH, load_sophia_index
    from mekhane.symploke.kairos_ingest import HANDOFF_DIR
    
    print_header("Mnēmē Synthesis Stats")
    
    # Sophia stats
    if DEFAULT_INDEX_PATH.exists():
        try:
            adapter = load_sophia_index(str(DEFAULT_INDEX_PATH))
            print(f"Sophia:  {adapter.count()} vectors")
        except Exception as e:
            print_error(f"Sophia: Error - {e}")
    else:
        print("Sophia:  Not indexed")
    
    # Kairos stats
    handoff_count = len(list(HANDOFF_DIR.glob("handoff_*.md"))) if HANDOFF_DIR.exists() else 0
    print(f"Kairos:  {handoff_count} handoff files")
    
    # Chronos stats (placeholder)
    print("Chronos: Not implemented")
    
    print("-" * 40)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Mnēmē Synthesis - 統合セッション記憶CLI",
        prog="mneme",
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # ingest
    p_ingest = subparsers.add_parser("ingest", help="インデックス更新")
    p_ingest.add_argument("--all", action="store_true", help="全インデックス更新 (default)")
    p_ingest.add_argument("--sophia", action="store_true", help="Sophia (KI) のみ")
    p_ingest.add_argument("--kairos", action="store_true", help="Kairos (Handoff) のみ")
    p_ingest.add_argument("--chronos", action="store_true", help="Chronos (会話履歴) のみ")
    p_ingest.set_defaults(func=cmd_ingest)
    
    # stats
    p_stats = subparsers.add_parser("stats", help="統計情報表示")
    p_stats.set_defaults(func=cmd_stats)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Default to --all if no specific index is selected for ingest
    if args.command == "ingest":
        if not (args.sophia or args.kairos or args.chronos):
            args.all = True
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
