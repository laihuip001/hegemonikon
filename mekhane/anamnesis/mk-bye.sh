#!/bin/bash
# PROOF: [L2/インフラ] <- mekhane/anamnesis/mk-bye.sh
#
# /bye ワークフローのオーケストレーター
# 1. チャット履歴エクスポート (export_chats.py)
# 2. n8n Webhook 通知 (Handoff 生成 + Slack 通知)
# 3. デスクトップ通知 (notify-send)
#
# Usage:
#   ./mk-bye.sh [主題(オプション)]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HEGEMONIKON_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
VENV_PYTHON="$HEGEMONIKON_DIR/.venv/bin/python"
EXPORT_SCRIPT="$SCRIPT_DIR/export_chats.py"
N8N_WEBHOOK_URL="http://localhost:5678/webhook/bye-handoff"

# コンテキスト（主題）
SUBJECT="$1"
if [ -z "$SUBJECT" ]; then
    SUBJECT="Auto-generated Handoff"
fi

echo "=== /bye Sequence Initiated ==="
echo "Subject: $SUBJECT"

# 1. Export Chat History
echo "[1/3] Exporting chat history..."
if "$VENV_PYTHON" "$EXPORT_SCRIPT" --single "$SUBJECT" --format md; then
    echo "Chat export successful."
else
    echo "Chat export failed. Continuing..."
fi

# 2. Trigger n8n Webhook (Slack 通知含む)
echo "[2/3] Triggering n8n Handoff generation..."
RESPONSE=$(curl -s -X POST "$N8N_WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -d "{\"subject\": \"$SUBJECT\", \"timestamp\": \"$(date -Iseconds)\"}" \
    --connect-timeout 5 || echo "n8n unreachable")

echo "n8n Response: $RESPONSE"

# 3. Desktop Notification (即座にローカル通知)
echo "[3/3] Desktop notification..."
if command -v notify-send &>/dev/null; then
    notify-send -u critical -i dialog-information \
        "👋 /bye Sequence Complete" \
        "Subject: $SUBJECT\nHandoff saved to mneme."
    echo "Desktop notification sent."
else
    echo "notify-send not available, skipping."
fi

echo "=== /bye Sequence Completed ==="
