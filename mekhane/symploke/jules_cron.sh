#!/bin/bash
# PROOF: [L1/インフラ] <- mekhane/symploke/ O4→cron 統合→ローテーション
# PURPOSE: Jules Daily Pipeline の cron wrapper — basanos/specialist の曜日ローテーション
#
# Crontab 設定例:
#   0 6  * * * /home/makaron8426/oikos/hegemonikon/mekhane/symploke/jules_cron.sh morning
#   0 12 * * * /home/makaron8426/oikos/hegemonikon/mekhane/symploke/jules_cron.sh afternoon
#   0 18 * * * /home/makaron8426/oikos/hegemonikon/mekhane/symploke/jules_cron.sh evening
#
# Mode rotation:
#   月水金 = basanos (structured review)
#   火木   = hybrid  (60% basanos + 40% specialist)
#   土日   = specialist (random exploration)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VENV="$PROJECT_ROOT/.venv/bin/python"
SCHEDULER="$SCRIPT_DIR/jules_daily_scheduler.py"
LOG_DIR="$PROJECT_ROOT/logs/specialist_daily"

# Slot argument (morning/afternoon/evening)
SLOT="${1:-morning}"

# Determine day of week (1=Mon ... 7=Sun)
DOW=$(date +%u)

# F16: Try adaptive mode selection, fallback to static
ADAPTIVE_MODE=$(cd "$PROJECT_ROOT" && PYTHONPATH="$SCRIPT_DIR:." "$VENV" -c \
    "from adaptive_rotation import recommend_mode; print(recommend_mode($DOW))" 2>/dev/null || echo "")

if [ -n "$ADAPTIVE_MODE" ]; then
    MODE="$ADAPTIVE_MODE"
    echo "[$(date)] F16: Adaptive mode selected: $MODE (day=$DOW)"
    # adaptive モードでも pre-audit は basanos/hybrid で有効化
    case $MODE in
        basanos)  EXTRA_ARGS="--pre-audit" ;;
        hybrid)   EXTRA_ARGS="--basanos-ratio 0.6 --pre-audit" ;;
        *)        EXTRA_ARGS="" ;;
    esac
else
    # Static fallback
    case $DOW in
        1|3|5)  # Mon, Wed, Fri → basanos
            MODE="basanos"
            EXTRA_ARGS="--pre-audit"
            ;;
        2|4)    # Tue, Thu → hybrid
            MODE="hybrid"
            EXTRA_ARGS="--basanos-ratio 0.6 --pre-audit"
            ;;
        6|7)    # Sat, Sun → specialist
            MODE="specialist"
            EXTRA_ARGS=""
            ;;
    esac
fi

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Clean up old logs (30+ days)
find "$LOG_DIR" -name "scheduler_*.json" -mtime +30 -delete 2>/dev/null || true
find "$LOG_DIR" -name "cron_*.log" -mtime +30 -delete 2>/dev/null || true

# Log file for this run
LOGFILE="$LOG_DIR/cron_$(date +%Y%m%d_%H%M)_${SLOT}.log"

echo "[$(date)] Starting Jules $SLOT slot (mode=$MODE, day=$DOW)" | tee "$LOGFILE"

# Execute scheduler
cd "$PROJECT_ROOT"
PYTHONPATH=. "$VENV" "$SCHEDULER" \
    --slot "$SLOT" \
    --mode "$MODE" \
    $EXTRA_ARGS \
    2>&1 | tee -a "$LOGFILE"

EXIT_CODE=${PIPESTATUS[0]}

echo "[$(date)] Completed with exit code $EXIT_CODE" | tee -a "$LOGFILE"

# F13: 失敗時に Sympatheia 通知を送信
if [ $EXIT_CODE -ne 0 ]; then
    echo "[$(date)] ERROR: Scheduler failed, sending notification" | tee -a "$LOGFILE"
    curl -s -X POST "http://127.0.0.1:9696/api/sympatheia/ingest" \
        -H "Content-Type: application/json" \
        -d "{\"source\":\"jules_cron\",\"level\":\"CRITICAL\",\"title\":\"Scheduler 失敗\",\"body\":\"slot=$SLOT mode=$MODE exit=$EXIT_CODE day=$DOW\"}" \
        2>/dev/null || echo "[$(date)] WARNING: Sympatheia notification failed" | tee -a "$LOGFILE"
fi

exit $EXIT_CODE
