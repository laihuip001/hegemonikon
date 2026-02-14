#!/usr/bin/env python3
"""Handoff 情報保存率 (R) の定量測定スクリプト.

HGK ブートストラップの十分条件 S2:
  Handoff 情報保存率 R > R_min

測定方法:
  R = |entities(Handoff) ∩ entities(ChatExport)| / |entities(ChatExport)|

entities = ファイルパス, WF名, 技術用語, 決定事項 etc.
"""

import argparse
import re
import sys
from pathlib import Path
from collections import Counter


def extract_entities(text: str) -> set[str]:
    """テキストからエンティティ (ファイルパス, WF名, 技術用語) を抽出."""
    entities = set()

    # ファイルパス (~/oikos/..., /home/..., relative paths with extensions)
    for m in re.finditer(r'[~/\w.-]+\.\w{1,5}', text):
        path = m.group()
        if len(path) > 5 and '/' in path:
            entities.add(f"PATH:{path}")

    # WF名 (/noe, /bye, /boot etc.)
    for m in re.finditer(r'/[a-z]{2,6}[+\-*]?', text):
        entities.add(f"WF:{m.group()}")

    # BC番号 (BC-1, BC-18 etc.)
    for m in re.finditer(r'BC-\d+', text):
        entities.add(f"BC:{m.group()}")

    # 技術用語 (backtick内)
    for m in re.finditer(r'`([^`]+)`', text):
        term = m.group(1).strip()
        if len(term) > 2 and len(term) < 80:
            entities.add(f"TERM:{term}")

    # Markdown ヘッダー (## 以上)
    for m in re.finditer(r'^#{1,3}\s+(.+)$', text, re.MULTILINE):
        entities.add(f"HEADER:{m.group(1).strip()}")

    # 決定事項 (✅, ❌, →, [x] etc.)
    for m in re.finditer(r'(?:✅|❌|→|⚠️)\s*(.+?)$', text, re.MULTILINE):
        decision = m.group(1).strip()[:60]
        if len(decision) > 5:
            entities.add(f"DECISION:{decision}")

    return entities


def measure_retention(handoff_path: Path, chat_path: Path) -> dict:
    """Handoff と ChatExport の情報保存率を測定."""
    handoff_text = handoff_path.read_text(encoding='utf-8')
    chat_text = chat_path.read_text(encoding='utf-8')

    handoff_entities = extract_entities(handoff_text)
    chat_entities = extract_entities(chat_text)

    if not chat_entities:
        return {
            'handoff': str(handoff_path.name),
            'chat': str(chat_path.name),
            'R': 0.0,
            'retained': 0,
            'total_chat': 0,
            'total_handoff': 0,
            'handoff_only': 0,
            'error': 'No entities in chat export',
        }

    retained = handoff_entities & chat_entities
    chat_only = chat_entities - handoff_entities
    handoff_only = handoff_entities - chat_entities

    R = len(retained) / len(chat_entities)

    return {
        'handoff': str(handoff_path.name),
        'chat': str(chat_path.name),
        'R': round(R, 3),
        'retained': len(retained),
        'total_chat': len(chat_entities),
        'total_handoff': len(handoff_entities),
        'handoff_only': len(handoff_only),
        'lost': sorted(list(chat_only))[:10],
        'gained': sorted(list(handoff_only))[:10],
    }


def find_pairs(sessions_dir: Path) -> list[tuple[Path, Path]]:
    """同日の Handoff と ChatExport のペアを検出."""
    handoffs = sorted(sessions_dir.glob('handoff_*.md'))
    chats = sorted(sessions_dir.glob('chat_export_*.md'))

    pairs = []
    for h in handoffs:
        # handoff_2026-02-14_1830.md → 2026-02-14
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', h.name)
        if not date_match:
            continue
        date = date_match.group(1)

        # 同日の chat_export を検索
        for c in chats:
            if date in c.name:
                pairs.append((h, c))
                break

    return pairs


def main():
    parser = argparse.ArgumentParser(description='Handoff 情報保存率 R の定量測定')
    parser.add_argument('--sessions-dir', type=Path,
                        default=Path.home() / 'oikos/mneme/.hegemonikon/sessions',
                        help='sessions ディレクトリ')
    parser.add_argument('--handoff', type=Path, help='特定の Handoff ファイル')
    parser.add_argument('--chat', type=Path, help='特定の Chat Export ファイル')
    parser.add_argument('--all', action='store_true', help='全ペアを測定')
    parser.add_argument('--verbose', '-v', action='store_true', help='詳細出力')
    args = parser.parse_args()

    if args.handoff and args.chat:
        # 特定ペアの測定
        result = measure_retention(args.handoff, args.chat)
        print_result(result, args.verbose)
    elif args.all:
        # 全ペアの測定
        pairs = find_pairs(args.sessions_dir)
        if not pairs:
            print("⚠️ Handoff-ChatExport ペアが見つかりません")
            print(f"  sessions_dir: {args.sessions_dir}")
            sys.exit(1)

        results = []
        for h, c in pairs:
            result = measure_retention(h, c)
            results.append(result)

        print(f"\n📊 Handoff 情報保存率レポート ({len(results)} ペア)")
        print("=" * 60)

        total_R = 0
        for r in results:
            print_result(r, args.verbose)
            total_R += r['R']

        avg_R = total_R / len(results) if results else 0
        print(f"\n{'=' * 60}")
        print(f"📈 平均保存率 R = {avg_R:.1%}")
        print(f"   ペア数: {len(results)}")

        if avg_R < 0.3:
            print("   ⚠️ R < 30%: 十分条件 S2 に懸念あり")
        elif avg_R < 0.5:
            print("   🟡 R < 50%: 改善の余地あり")
        else:
            print("   ✅ R ≥ 50%: 十分条件 S2 充足")
    else:
        # 最新ペアの測定
        pairs = find_pairs(args.sessions_dir)
        if pairs:
            result = measure_retention(*pairs[-1])
            print_result(result, args.verbose)
        else:
            print("⚠️ Handoff-ChatExport ペアが見つかりません")
            print("  使い方: --handoff FILE --chat FILE で個別指定可能")


def print_result(result: dict, verbose: bool = False):
    """結果を表示."""
    print(f"\n📄 {result['handoff']} ↔ {result['chat']}")
    print(f"   R = {result['R']:.1%} ({result['retained']}/{result['total_chat']} entities retained)")
    print(f"   Handoff entities: {result['total_handoff']} | Handoff-only: {result['handoff_only']}")

    if verbose and 'lost' in result:
        if result['lost']:
            print(f"   🔴 失われた要素 (上位10): {result['lost'][:5]}")
        if result.get('gained'):
            print(f"   🟢 追加された要素 (上位10): {result['gained'][:5]}")


if __name__ == '__main__':
    main()
