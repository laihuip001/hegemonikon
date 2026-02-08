#!/bin/bash
# PROOF: [L2/インフラ] <- mekhane/anamnesis/mk-boot-notify.sh
#
# /boot 起動時の Slack 通知
# boot_integration.py の後に呼ぶ
#
# Usage:
#   ./mk-boot-notify.sh [モード(fast/standard/detailed)]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HEGEMONIKON_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
ENV_FILE="$HEGEMONIKON_DIR/mekhane/ergasterion/n8n/.env"

# Slack Webhook URL
SLACK_WEBHOOK_URL=""
if [ -f "$ENV_FILE" ]; then
    SLACK_WEBHOOK_URL=$(grep -s '^SLACK_WEBHOOK_URL=' "$ENV_FILE" | cut -d= -f2-)
fi

MODE="${1:-standard}"

if [ -n "$SLACK_WEBHOOK_URL" ]; then
    curl -s --connect-timeout 5 --max-time 10 \
        -X POST -H 'Content-Type: application/json' \
        -d "{\"blocks\":[{\"type\":\"header\",\"text\":{\"type\":\"plain_text\",\"text\":\"🧠 Session Started\",\"emoji\":true}},{\"type\":\"section\",\"fields\":[{\"type\":\"mrkdwn\",\"text\":\"*Mode:*\n${MODE}\"},{\"type\":\"mrkdwn\",\"text\":\"*Time:*\n$(date '+%H:%M %Y-%m-%d')\"}]}]}" \
        "$SLACK_WEBHOOK_URL" >/dev/null 2>&1 &
    echo "Slack: notified (background)"
else
    echo "Slack: skipped (no SLACK_WEBHOOK_URL)"
fi
