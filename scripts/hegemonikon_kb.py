#!/usr/bin/env python3
# PROOF: [L3/Utility] <- scripts/ A0→Implementation→hegemonikon_kb
"""hegemonikon-kb: HGK 知識基盤への統合検索 CLI。

Jules/Gemini が HGK の概念・定理・用語を直接引くためのインターフェース。

Usage:
    python scripts/hegemonikon_kb.py query "FEP"           # 統合検索
    python scripts/hegemonikon_kb.py theorem O1             # 定理詳細
    python scripts/hegemonikon_kb.py vocab "Mekhanē"        # 用語検索
    python scripts/hegemonikon_kb.py context                # context/ 一覧
"""

import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONTEXT_DIR = PROJECT_ROOT / "mekhane" / "symploke" / "context"
KERNEL_DIR = PROJECT_ROOT / "kernel"

# 24 定理の定義
THEOREMS = {
    "O1": ("Noēsis", "深い認識・直観", "ousia.md"),
    "O2": ("Boulēsis", "意志・目的", "ousia.md"),
    "O3": ("Zētēsis", "探求・問い", "ousia.md"),
    "O4": ("Energeia", "行為・実現", "ousia.md"),
    "S1": ("Metis", "知略・戦略的思考", "schema.md"),
    "S2": ("Mekhanē", "方法・手段配置", "schema.md"),
    "S3": ("Stasis", "変更追跡・状態管理", "schema.md"),
    "S4": ("Praxis", "実践・価値実現", "schema.md"),
    "H1": ("Propatheia", "前感情・初期傾向", "horme.md"),
    "H2": ("Pistis", "確信・信頼", "horme.md"),
    "H3": ("Orexis", "欲求・価値傾向", "horme.md"),
    "H4": ("Doxa", "信念・持続的確信", "horme.md"),
    "P1": ("Khōra", "場・Git位置", "perigraphe.md"),
    "P2": ("Chronos", "時間・期限", "perigraphe.md"),
    "P3": ("Telos", "完了条件", "perigraphe.md"),
    "P4": ("Eukairia", "適時判断", "perigraphe.md"),
    "K1": ("Prohairesis", "文脈選択", "kairos.md"),
    "K2": ("Taksis", "優先順位", "kairos.md"),
    "K3": ("Synesis", "文脈理解", "kairos.md"),
    "K4": ("Sophia", "知恵・調査", "kairos.md"),
    "A1": ("Hexis", "認知態勢", "akribeia.md"),
    "A2": ("Krisis", "判定・評価", "akribeia.md"),
    "A3": ("Epimeleia", "配慮・保守", "akribeia.md"),
    "A4": ("Epistēmē", "知識・確立", "akribeia.md"),
}


def cmd_query(args: argparse.Namespace) -> None:
    """統合検索: context/ + THEOREMS を検索。"""
    query = args.query.lower()
    results = []

    # 1. 定理検索
    for tid, (name, desc, _) in THEOREMS.items():
        if query in tid.lower() or query in name.lower() or query in desc:
            results.append(f"  [{tid}] {name} — {desc}")

    # 2. context/ 検索
    for f in sorted(CONTEXT_DIR.glob("*.md")):
        content = f.read_text(errors="replace")
        lines = content.split("\n")
        matches = [
            (i + 1, line.strip())
            for i, line in enumerate(lines)
            if query in line.lower()
        ]
        if matches:
            for ln, text in matches[:3]:
                results.append(f"  [{f.stem}:{ln}] {text[:80]}")

    if results:
        print(f"=== '{args.query}' の検索結果 ({len(results)}件) ===")
        for r in results:
            print(r)
    else:
        print(f"'{args.query}' に一致する結果なし。")


def cmd_theorem(args: argparse.Namespace) -> None:
    """定理詳細: ID で定理情報を表示。"""
    tid = args.theorem_id.upper()
    if tid in THEOREMS:
        name, desc, source_file = THEOREMS[tid]
        print(f"=== {tid}: {name} ===")
        print(f"  説明: {desc}")
        print(f"  定義: kernel/{source_file}")
        series = tid[0]
        series_map = {
            "O": "Ousia (本質)", "S": "Schema (様態)", "H": "Hormē (傾向)",
            "P": "Perigraphē (条件)", "K": "Kairos (文脈)", "A": "Akribeia (精密)",
        }
        print(f"  Series: {series_map.get(series, series)}")
        # 同 Series の他の定理
        siblings = [
            f"{k}: {v[0]}" for k, v in THEOREMS.items()
            if k[0] == series and k != tid
        ]
        print(f"  同 Series: {', '.join(siblings)}")
    else:
        # 部分一致で候補を表示
        candidates = [
            f"{k}: {v[0]}" for k, v in THEOREMS.items()
            if tid.lower() in k.lower() or tid.lower() in v[0].lower()
        ]
        if candidates:
            print(f"'{tid}' に完全一致なし。候補:")
            for c in candidates:
                print(f"  {c}")
        else:
            print(f"'{tid}' に一致する定理なし。")
            print("利用可能な ID: " + ", ".join(sorted(THEOREMS.keys())))


def cmd_vocab(args: argparse.Namespace) -> None:
    """用語検索: hgk_vocabulary.md から用語を検索。"""
    vocab_file = CONTEXT_DIR / "hgk_vocabulary.md"
    if not vocab_file.exists():
        print("hgk_vocabulary.md が見つかりません。")
        return

    query = args.term.lower()
    content = vocab_file.read_text(errors="replace")
    lines = content.split("\n")

    found = False
    for i, line in enumerate(lines):
        if query in line.lower():
            # 前後の文脈を表示
            start = max(0, i - 1)
            end = min(len(lines), i + 3)
            if not found:
                print(f"=== '{args.term}' の用語情報 ===")
            found = True
            for j in range(start, end):
                marker = ">>>" if j == i else "   "
                print(f"  {marker} {lines[j]}")
            print()

    if not found:
        print(f"'{args.term}' に一致する用語なし。")


def cmd_context(args: argparse.Namespace) -> None:
    """context/ ファイル一覧。"""
    files = sorted(CONTEXT_DIR.glob("*.md"))
    print(f"=== context/ ({len(files)} ファイル) ===")
    total = 0
    for f in files:
        lines = len(f.read_text(errors="replace").split("\n"))
        total += lines
        print(f"  {f.name:30s} {lines:4d} 行")
    print(f"  {'合計':30s} {total:4d} 行")


def main():
    parser = argparse.ArgumentParser(
        description="hegemonikon-kb: HGK 知識基盤への統合検索",
        prog="hegemonikon-kb",
    )
    sub = parser.add_subparsers(dest="command")

    p_query = sub.add_parser("query", help="統合検索")
    p_query.add_argument("query", help="検索クエリ")

    p_thm = sub.add_parser("theorem", help="定理詳細")
    p_thm.add_argument("theorem_id", help="定理 ID (例: O1, S2, K4)")

    p_vocab = sub.add_parser("vocab", help="用語検索")
    p_vocab.add_argument("term", help="用語 (例: Mekhanē)")

    sub.add_parser("context", help="context/ 一覧")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    commands = {
        "query": cmd_query,
        "theorem": cmd_theorem,
        "vocab": cmd_vocab,
        "context": cmd_context,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
