#!/usr/bin/env python3
"""adjunction_status.py — 12随伴ペアの実装状態をWFファイルからスキャン

Context Rot 対策スクリプト。V-007 (stale_handoff) の教訓から生まれた。
「Handoff に書いてあること」ではなく「ファイルの中の真実」を見る。

Usage:
    cd ~/oikos/hegemonikon
    python scripts/adjunction_status.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# 12随伴ペア候補 (adjunction_analysis.md より)
ADJUNCTION_PAIRS = [
    # (左随伴WF, 右随伴WF, Series, 説明)
    ("boot", "bye", "τ", "セッション展開⊣圧縮"),
    ("ene", "bou", "O", "行為⊣意志 (O4⊣O2)"),
    ("noe", "zet", "O", "認識⊣探求 (O1⊣O3)"),
    ("mek", "pra", "S", "方法⊣実践 (S2⊣S4)"),
    ("met", "sta", "S", "尺度⊣基準 (S1⊣S3)"),
    ("pro", "dox", "H", "直感⊣信念 (H1⊣H4)"),
    ("pis", "ore", "H", "確信⊣欲求 (H2⊣H3)"),
    ("kho", "tro", "P", "場⊣軌道 (P1⊣P3)"),
    ("hod", "tek", "P", "道⊣技法 (P2⊣P4)"),
    ("euk", "tel", "K", "好機⊣目的 (K1⊣K3)"),
    ("chr", "sop", "K", "時間⊣知恵 (K2⊣K4)"),
    ("pat", "gno", "A", "情念⊣格言 (A1⊣A3)"),
    # dia⊣epi は pat⊣gno の代わりに A2⊣A4
    # ("dia", "epi", "A", "判定⊣知識 (A2⊣A4)"),
]

WF_DIR = Path(__file__).parent.parent / ".agent" / "workflows"


def check_wf_adjunction(wf_name: str) -> dict:
    """WFファイルの category_theory セクションを検査"""
    wf_path = WF_DIR / f"{wf_name}.md"
    
    if not wf_path.exists():
        return {"exists": False, "has_adjunction": False, "details": "WFファイルなし"}
    
    content = wf_path.read_text(encoding="utf-8")
    
    # YAML frontmatter を抽出
    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        return {"exists": True, "has_adjunction": False, "details": "frontmatter なし"}
    
    frontmatter = fm_match.group(1)
    
    # category_theory セクションの存在確認
    if "category_theory:" not in frontmatter:
        return {"exists": True, "has_adjunction": False, "details": "category_theory なし"}
    
    # adjunction フィールドの抽出
    adj_match = re.search(r'adjunction:\s*"(.+?)"', frontmatter)
    adjunction = adj_match.group(1) if adj_match else "不明"
    
    # core フィールド
    core_match = re.search(r'core:\s*"(.+?)"', frontmatter)
    core = core_match.group(1) if core_match else "不明"
    
    # drift/epsilon 情報
    has_drift = "drift:" in frontmatter
    has_eta = "unit:" in frontmatter or "eta:" in frontmatter
    has_epsilon = "counit:" in frontmatter or "epsilon:" in frontmatter
    
    completeness = sum([has_drift, has_eta, has_epsilon])
    
    return {
        "exists": True,
        "has_adjunction": True,
        "adjunction": adjunction,
        "core": core,
        "has_drift": has_drift,
        "has_eta": has_eta,
        "has_epsilon": has_epsilon,
        "completeness": completeness,
        "details": f"完備度 {completeness}/3",
    }


def main():
    print("═" * 60)
    print("  随伴ペア実装状態スキャン")
    print("  真実はファイルの中にある (V-007 教訓)")
    print("═" * 60)
    print()
    
    implemented = 0
    partial = 0
    missing = 0
    
    for left, right, series, desc in ADJUNCTION_PAIRS:
        left_result = check_wf_adjunction(left)
        right_result = check_wf_adjunction(right)
        
        both_have = left_result["has_adjunction"] and right_result["has_adjunction"]
        either_has = left_result["has_adjunction"] or right_result["has_adjunction"]
        
        if both_have:
            status = "✅"
            implemented += 1
            detail = f"L: {left_result['details']} / R: {right_result['details']}"
        elif either_has:
            status = "🟡"
            partial += 1
            which = left if left_result["has_adjunction"] else right
            detail = f"片方のみ ({which})"
        else:
            status = "⬜"
            missing += 1
            detail = "未実装"
        
        print(f"  {status} {left:>4} ⊣ {right:<4} [{series}] {desc}")
        if both_have:
            # completeness 詳細
            lc = left_result.get("completeness", 0)
            rc = right_result.get("completeness", 0)
            print(f"       完備度: {left}={lc}/3, {right}={rc}/3")
    
    print()
    print("─" * 60)
    print(f"  ✅ 実装済: {implemented} / 🟡 部分: {partial} / ⬜ 未実装: {missing}")
    print(f"  合計: {len(ADJUNCTION_PAIRS)} ペア")
    print("─" * 60)
    
    if missing + partial > 0:
        print()
        print("  次に実装すべきペア:")
        for left, right, series, desc in ADJUNCTION_PAIRS:
            left_r = check_wf_adjunction(left)
            right_r = check_wf_adjunction(right)
            if not (left_r["has_adjunction"] and right_r["has_adjunction"]):
                print(f"    → {left} ⊣ {right} [{series}]")


if __name__ == "__main__":
    main()
