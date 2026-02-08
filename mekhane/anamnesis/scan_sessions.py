#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- mekhane/anamnesis/ P3→データ処理が必要→scan_sessions が担う
"""
破損 .pb ファイルのスキャンとバックアップ
Usage: python scan_sessions.py
"""

import shutil
from pathlib import Path
from datetime import datetime

CONV_DIR = Path(r"M:\.gemini\antigravity\conversations")
BACKUP_DIR = Path(r"M:\.gemini\backup") / datetime.now().strftime("%Y%m%d_%H%M%S")


# PURPOSE: 破損 .pb ファイルを特定
def scan_pb_files():
    """破損 .pb ファイルを特定"""
    print("=== Scanning .pb files ===\n")

    problematic = []

    for pb_file in CONV_DIR.glob("*.pb"):
        size = pb_file.stat().st_size

        if size == 0:
            print(f"❌ {pb_file.name}: EMPTY (0 bytes)")
            problematic.append(pb_file)
        elif size > 20_971_520:  # 20MB
            print(f"⚠️  {pb_file.name}: HUGE ({size:,} bytes)")
            problematic.append(pb_file)
        elif 10 < size < 100:
            print(f"⚠️  {pb_file.name}: INCOMPLETE ({size} bytes)")
            problematic.append(pb_file)
        else:
            print(f"✓ {pb_file.name}: OK ({size:,} bytes)")

    return problematic


# PURPOSE: 問題ファイルをバックアップして削除
def backup_problematic(files):
    """問題ファイルをバックアップして削除"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    for pb_file in files:
        dest = BACKUP_DIR / pb_file.name
        shutil.copy2(pb_file, dest)
        pb_file.unlink()
        print(f"✓ Backed up and removed: {pb_file.name}")

    print(f"\nBackup location: {BACKUP_DIR}")


if __name__ == "__main__":
    problems = scan_pb_files()
    print(f"\nFound {len(problems)} problematic files\n")

    if problems:
        response = input("Backup and remove these files? (y/n): ")
        if response.lower() == "y":
            backup_problematic(problems)
            print("\n✓ Cleanup complete. Restart Antigravity to reindex.")
