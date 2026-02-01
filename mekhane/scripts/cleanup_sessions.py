# PROOF: [L3/ユーティリティ] <- mekhane/scripts/ O4→運用スクリプトが必要→cleanup_sessions が担う
#!/usr/bin/env python3
"""
cleanup_sessions.py
現在のセッション以外の全ての .pb ファイルを backup ディレクトリに退避し、
環境をクリーンにする。

Target Session to KEEP: 2cf58e28-160a-4d1c-9078-1671acc546d2
"""

import shutil
import os
from pathlib import Path
from datetime import datetime

CURRENT_SESSION_ID = "2cf58e28-160a-4d1c-9078-1671acc546d2"
CONV_DIR = Path(r"M:\.gemini\antigravity\conversations")
BACKUP_DIR = Path(
    r"M:\.gemini\antigravity\conversations_backup_"
    + datetime.now().strftime("%Y%m%d_%H%M%S")
)


def cleanup():
    if not CONV_DIR.exists():
        print(f"Directory not found: {CONV_DIR}")
        return

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Created backup directory: {BACKUP_DIR}")

    moved_count = 0
    kept_count = 0

    threshold_size = 20 * 1024 * 1024  # 20MB

    for pb_file in CONV_DIR.glob("*.pb"):
        if pb_file.stem == CURRENT_SESSION_ID:
            print(f"[*] Keeping current session: {pb_file.name}")
            kept_count += 1
            continue

        size = pb_file.stat().st_size
        if size > threshold_size or size == 0:
            print(
                f"⚠️  Moving problematic file ({size/1024/1024:.1f} MB): {pb_file.name}"
            )
            try:
                shutil.move(str(pb_file), str(BACKUP_DIR / pb_file.name))
                moved_count += 1
            except Exception as e:
                print(f"[!] Failed to move {pb_file.name}: {e}")
        else:
            # 正常ファイル
            kept_count += 1

    print("-" * 30)
    print(f"Moved {moved_count} problematic sessions to backup.")
    print(f"Kept {kept_count} healthy sessions.")

    # Clean indices (必須: 壊れたセッションの情報を消すため)
    index_dir = Path(r"M:\.gemini\antigravity\_index")
    if index_dir.exists():
        print("Removing LanceDB index...")
        try:
            shutil.rmtree(index_dir)
            print("[OK] Index removed.")
        except Exception as e:
            print(f"[!] Failed to remove index: {e}")

    brain_index_dir = Path(r"M:\.gemini\antigravity\brain\_index")
    if brain_index_dir.exists():
        print("Removing brain index...")
        try:
            shutil.rmtree(brain_index_dir)
            print("[OK] Brain index removed.")
        except Exception as e:
            print(f"[!] Failed to remove brain index: {e}")


if __name__ == "__main__":
    cleanup()
