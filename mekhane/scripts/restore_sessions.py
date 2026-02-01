# PROOF: [L3/ユーティリティ] O4→運用スクリプトが必要→restore_sessions が担う
#!/usr/bin/env python3
"""
restore_healthy_sessions.py
バックアップから健全なセッションを復元する。
ただし、archive にある巨大ファイル(2件)は戻さない。
"""

import shutil
from pathlib import Path

# 最新のバックアップディレクトリを探す
BACKUP_ROOT = Path(r"M:\.gemini\antigravity")
backups = sorted(list(BACKUP_ROOT.glob("conversations_backup_*")))

if not backups:
    print("No backups found!")
    exit(1)

LATEST_BACKUP = backups[-1]  # 一番新しいバックアップ (さっき全退避したもの)
CONV_DIR = Path(r"M:\.gemini\antigravity\conversations")
ARCHIVE_DIR = Path(r"M:\.gemini\antigravity\archive")

print(f"Restoring from: {LATEST_BACKUP}")

restored_count = 0
skipped_count = 0

CONV_DIR.mkdir(parents=True, exist_ok=True)

# archive にあるファイル名のリスト
archived_files = {f.name for f in ARCHIVE_DIR.glob("*.pb")}
print(f"Archived (ignored) files: {len(archived_files)}")

for pb_file in LATEST_BACKUP.glob("*.pb"):
    # archive にあるファイルなら戻さない（壊れているから）
    if pb_file.name in archived_files:
        print(f"Skipping archived file: {pb_file.name}")
        skipped_count += 1
        continue

    # サイズチェック（念のため）
    size = pb_file.stat().st_size
    if size > 20 * 1024 * 1024:  # 20MB
        print(
            f"Skipping HUGE file found in backup: {pb_file.name} ({size/1024/1024:.1f} MB)"
        )
        skipped_count += 1
        continue

    # 復元
    shutil.copy2(str(pb_file), str(CONV_DIR / pb_file.name))
    restored_count += 1

print("-" * 30)
print(f"Restored {restored_count} healthy sessions.")
print(f"Skipped {skipped_count} problematic sessions.")
