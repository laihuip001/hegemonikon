#!/bin/bash
# sync_hegemonikon_texts.sh
# PURPOSE: Hegemonikón の自然言語ドキュメントのみを ~/Sync にミラーする
# 
# 対象: .agent/, kernel/, docs/, ccl/ の .md, .yaml, .yml ファイル
# 除外: Python コード, DBs, テスト, node_modules, .venv
#
# Usage: ./sync_hegemonikon_texts.sh [--dry-run]

set -euo pipefail

SRC="$HOME/oikos/hegemonikon"
DST="$HOME/Sync/15_🏛️_ヘゲモニコン｜Hegemonikon"

DRY_RUN=""
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN="--dry-run"
  echo "🔍 Dry-run mode"
fi

INCLUDE_DIRS=(".agent" "kernel" "docs" "ccl")

for dir in "${INCLUDE_DIRS[@]}"; do
  if [ -d "$SRC/$dir" ]; then
    echo "📂 Syncing $dir..."
    rsync -av --delete $DRY_RUN \
      --include='*/' \
      --include='*.md' \
      --include='*.yaml' \
      --include='*.yml' \
      --exclude='*' \
      "$SRC/$dir/" "$DST/$dir/"
  else
    echo "⚠️  $dir not found, skipping"
  fi
done

# ルートの重要ファイルもコピー
for f in README.md AGENTS.md; do
  if [ -f "$SRC/$f" ]; then
    rsync -av $DRY_RUN "$SRC/$f" "$DST/"
  fi
done

echo ""
echo "✅ Hegemonikón テキストミラー同期完了"
echo "📊 ファイル数: $(find "$DST" -name '*.md' -type f | wc -l) .md files"
echo "📦 総容量: $(du -sh "$DST" | cut -f1)"
