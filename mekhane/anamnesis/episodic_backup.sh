#!/bin/bash
# PROOF: [L2/インフラ]
# 
# P3 → エピソード記憶のバックアップが必要
#    → Antigravity brain/knowledge を mneme にコピー
#    → このスクリプトが担う
# Q.E.D.
#
# episodic_backup.sh - Antigravity データを mneme にバックアップ
# 使用方法: ./episodic_backup.sh
# cron: 0 * * * * /home/laihuip001/oikos/hegemonikon/mekhane/anamnesis/episodic_backup.sh

set -euo pipefail

# 設定
# NOTE: Antigravity 環境では HOME=/home/laihuip001/oikos
OIKOS_ROOT="/home/laihuip001/oikos"
GEMINI_DIR="${OIKOS_ROOT}/.gemini/antigravity"
MNEME_DIR="${OIKOS_ROOT}/mneme/.antigravity"
LOG_FILE="${OIKOS_ROOT}/mneme/.hegemonikon/logs/episodic_backup.log"

# ログ関数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 初期化
mkdir -p "$MNEME_DIR/brain" "$MNEME_DIR/knowledge" "$(dirname "$LOG_FILE")"

log "=== Episodic Backup Start ==="

# Brain (task.md, walkthrough.md, implementation_plan.md)
if [[ -d "${GEMINI_DIR}/brain" ]]; then
    BRAIN_COUNT=$(find "${GEMINI_DIR}/brain" -name "*.md" 2>/dev/null | wc -l)
    rsync -a --delete \
        --include='*/' \
        --include='*.md' \
        --include='*.json' \
        --exclude='*' \
        "${GEMINI_DIR}/brain/" "${MNEME_DIR}/brain/"
    log "Brain: ${BRAIN_COUNT} markdown files synced"
else
    log "WARNING: Brain directory not found"
fi

# Knowledge (KI artifacts)
if [[ -d "${GEMINI_DIR}/knowledge" ]]; then
    KNOWLEDGE_COUNT=$(find "${GEMINI_DIR}/knowledge" -name "*.md" 2>/dev/null | wc -l)
    rsync -a --delete \
        --include='*/' \
        --include='*.md' \
        --include='*.json' \
        --exclude='*' \
        "${GEMINI_DIR}/knowledge/" "${MNEME_DIR}/knowledge/"
    log "Knowledge: ${KNOWLEDGE_COUNT} artifact files synced"
else
    log "WARNING: Knowledge directory not found"
fi

# 統計
TOTAL_SIZE=$(du -sh "$MNEME_DIR" 2>/dev/null | cut -f1)
log "Total backup size: ${TOTAL_SIZE}"
log "=== Episodic Backup Complete ==="
