#!/bin/bash
# sync_inbox_cleanup.sh
# PURPOSE: ~/Sync/00_Inbox 内の7日以上古いファイルを削除する
#
# Usage: ./sync_inbox_cleanup.sh [--dry-run]

set -euo pipefail

INBOX="$HOME/Sync/00_📥_仮置き｜Inbox"
TTL_DAYS=7

DRY_RUN=""
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN="true"
  echo "🔍 Dry-run mode"
fi

if [ ! -d "$INBOX" ]; then
  echo "⚠️ Inbox not found: $INBOX"
  exit 1
fi

# 7日以上古いファイルを検索
OLD_FILES=$(find "$INBOX" -type f -mtime +${TTL_DAYS} 2>/dev/null)

if [ -z "$OLD_FILES" ]; then
  echo "✅ Inbox clean — no files older than ${TTL_DAYS} days"
  exit 0
fi

echo "📋 Files older than ${TTL_DAYS} days:"
echo "$OLD_FILES"

if [ -z "$DRY_RUN" ]; then
  find "$INBOX" -type f -mtime +${TTL_DAYS} -delete
  # 空ディレクトリも削除（Inbox 自体は残す）
  find "$INBOX" -mindepth 1 -type d -empty -delete 2>/dev/null
  echo "✅ Cleaned $(echo "$OLD_FILES" | wc -l) files"
else
  echo "🔍 Would clean $(echo "$OLD_FILES" | wc -l) files"
fi
