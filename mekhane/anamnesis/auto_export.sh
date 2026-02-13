#!/bin/bash
# PROOF: [L2/インフラ] セッションエクスポート自動化
#
# Cron で定期実行し、Antigravity セッションを自動エクスポート
# 
# 設置: crontab -e で以下を追加
#   0 * * * * /home/makaron8426/oikos/hegemonikon/mekhane/anamnesis/auto_export.sh
#
# Origin: 2026-02-01 /bye エクスポート問題の解決

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HEGEMONIKON_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
VENV_PYTHON="$HEGEMONIKON_DIR/.venv/bin/python"
EXPORT_SCRIPT="$SCRIPT_DIR/export_chats.py"
LOG_FILE="/home/makaron8426/oikos/mneme/.hegemonikon/logs/auto_export.log"

# ログディレクトリ作成
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "=== Auto Export Started ==="

# Antigravity IDE (Electron) が起動しているか確認 (CDP ポート 9334)
if ! curl -s http://localhost:9334/json/version > /dev/null 2>&1; then
    log "Antigravity not running (CDP port 9334 not available). Skipping."
    exit 0
fi

log "Antigravity detected. Running export..."

# エクスポート実行
cd "$HEGEMONIKON_DIR"
if "$VENV_PYTHON" "$EXPORT_SCRIPT" --all >> "$LOG_FILE" 2>&1; then
    log "Export successful"

    # インデックス更新 (exports + steps + handoffs)
    INDEXER="$SCRIPT_DIR/session_indexer.py"
    log "Running indexers..."
    PYTHONPATH="$HEGEMONIKON_DIR" "$VENV_PYTHON" "$INDEXER" --exports >> "$LOG_FILE" 2>&1 && log "Export index OK" || log "Export index failed"
    PYTHONPATH="$HEGEMONIKON_DIR" "$VENV_PYTHON" "$INDEXER" --steps >> "$LOG_FILE" 2>&1 && log "Steps index OK" || log "Steps index failed"
    PYTHONPATH="$HEGEMONIKON_DIR" "$VENV_PYTHON" "$INDEXER" --handoffs >> "$LOG_FILE" 2>&1 && log "Handoffs index OK" || log "Handoffs index failed"
else
    log "Export failed with exit code $?"
fi

log "=== Auto Export Finished ==="
