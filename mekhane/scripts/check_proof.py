#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] A2→品質検証が必要→check_proof が担う
"""
PROOF Header Checker - CI Integration

mekhane/ 以下の全 Python ファイルに PROOF ヘッダーがあることを検証。

Usage:
    python check_proof.py              # 検証のみ
    python check_proof.py --verbose    # 詳細表示
    python check_proof.py --stats      # 統計表示

Exit codes:
    0 = All files have PROOF headers
    1 = Missing PROOF headers
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


# パス設定
SCRIPT_DIR = Path(__file__).resolve().parent
MEKHANE = SCRIPT_DIR.parent if SCRIPT_DIR.name == "scripts" else SCRIPT_DIR / "mekhane"

# 検証パターン
REQUIRED_PATTERN = re.compile(r"# PROOF:|PROOF:")
LEVEL_PATTERN = re.compile(r"\[(L[123])/([^\]]+)\]")


def check_proofs(verbose: bool = False) -> tuple[int, list[Path], Counter]:
    """Check all Python files for PROOF headers.
    
    Returns:
        (total_files, missing_files, level_counter)
    """
    total = 0
    missing = []
    levels = Counter()
    
    search_dir = MEKHANE
    if not search_dir.exists():
        # フォールバック: hegemonikon/mekhane を探す
        alt = Path(__file__).resolve().parent.parent / "mekhane"
        if alt.exists():
            search_dir = alt
        else:
            print(f"❌ Cannot find mekhane directory")
            print(f"   Tried: {MEKHANE}")
            print(f"   Tried: {alt}")
            sys.exit(2)
    
    for f in search_dir.rglob("*.py"):
        if "__pycache__" in str(f):
            continue
        
        total += 1
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            if verbose:
                print(f"  ⚠️  Cannot read {f}: {e}")
            continue
        
        if not REQUIRED_PATTERN.search(content):
            missing.append(f)
            if verbose:
                print(f"  ❌ Missing: {f.relative_to(search_dir.parent)}")
        else:
            # レベルを抽出
            match = LEVEL_PATTERN.search(content)
            if match:
                levels[match.group(1)] += 1
            else:
                levels["(no level)"] += 1
    
    return total, missing, levels


def main():
    parser = argparse.ArgumentParser(description="PROOF Header Checker")
    parser.add_argument("--verbose", "-v", action="store_true", help="詳細表示")
    parser.add_argument("--stats", "-s", action="store_true", help="統計表示")
    args = parser.parse_args()
    
    print("🔍 PROOF Header Checker")
    print()
    
    total, missing, levels = check_proofs(verbose=args.verbose)
    
    # 統計表示
    if args.stats:
        print("📊 Level Distribution:")
        for level, count in sorted(levels.items()):
            print(f"   {level}: {count}")
        print()
    
    # 結果
    if missing:
        print(f"❌ PROOF missing in {len(missing)}/{total} files:")
        display_count = 10 if not args.verbose else len(missing)
        for f in missing[:display_count]:
            rel = f.relative_to(f.parent.parent.parent) if len(f.parts) > 3 else f
            print(f"   - {rel}")
        if len(missing) > display_count:
            print(f"   ... and {len(missing) - display_count} more")
        sys.exit(1)
    
    print(f"✅ All {total} files have PROOF headers")
    if levels:
        print(f"   L1: {levels.get('L1', 0)} | L2: {levels.get('L2', 0)} | L3: {levels.get('L3', 0)}")
    sys.exit(0)


if __name__ == "__main__":
    main()
