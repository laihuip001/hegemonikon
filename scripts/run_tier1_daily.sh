#!/bin/bash
# PROOF: [L3/ユーティリティ] <- scripts/ O4→Tier1定点実行が必要→run_tier1_daily が担う
# ============================================================
# Tier 1 Daily Review — 朝4時定点実行
# 
# 全派生 (動的計算) を前日変更された Python ファイルに対して自動実行する
#
# Usage:
#   ./scripts/run_tier1_daily.sh           # 通常実行
#   ./scripts/run_tier1_daily.sh --dry-run # ドライラン
#   ./scripts/run_tier1_daily.sh --target path/to/file.py  # 固定ターゲット
# ============================================================
set -euo pipefail

# === 設定 ===
PROJECT_DIR="${PROJECT_DIR:-$HOME/oikos/hegemonikon}"
LOG_DIR="$PROJECT_DIR/logs/specialist_daily"
VENV="$PROJECT_DIR/.venv/bin/python"
RUNNER="$PROJECT_DIR/mekhane/symploke/run_specialists.py"
DATE=$(date +%Y%m%d)
TIMESTAMP=$(date +%Y%m%d_%H%M)
MAX_FILES=20          # API枠飽和防止
MAX_CONCURRENT=5      # 並列数
TIMEOUT_PER_FILE=900  # 15分/ファイル (180派生に十分)
DRY_RUN=""
FIXED_TARGET=""

# === 引数解析 ===
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) DRY_RUN="--dry-run"; shift ;;
        --target)  FIXED_TARGET="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# === 環境ロード ===
cd "$PROJECT_DIR"
set -a && source "$PROJECT_DIR/.env" 2>/dev/null && set +a

# API キー数を確認
KEY_COUNT=$(env | grep -c JULIUS_API_KEY || true)
if [ "$KEY_COUNT" -eq 0 ] && [ -z "$DRY_RUN" ]; then
    echo "[$TIMESTAMP] ERROR: No API keys found. Aborting." | tee -a "$LOG_DIR/error.log"
    notify-send "⚠️ Tier 1 Daily" "API keys not found. Aborted." 2>/dev/null || true
    exit 1
fi

# === 専門家数を動的取得 ===
SPECIALIST_INFO=$("$VENV" -c "
from mekhane.symploke.specialists_tier1 import TIER1_SPECIALISTS, get_all_derivatives
base = len(TIER1_SPECIALISTS)
deriv = len(get_all_derivatives(TIER1_SPECIALISTS[0]))
print(f'{base} {deriv + 1} {base * (deriv + 1)}')
" 2>/dev/null || echo "20 9 180")
BASE_COUNT=$(echo "$SPECIALIST_INFO" | awk '{print $1}')
COORDS_PER=$(echo "$SPECIALIST_INFO" | awk '{print $2}')
TOTAL_PER_FILE=$(echo "$SPECIALIST_INFO" | awk '{print $3}')

# === ターゲット決定 ===
if [ -n "$FIXED_TARGET" ]; then
    TARGETS="$FIXED_TARGET"
else
    # 前日変更ファイル (Python のみ)
    # フォールバック: HEAD~1 が無い場合 (初回) は全ファイルから最新20件
    TARGETS=$(git diff --name-only HEAD~1 -- '*.py' 2>/dev/null | head -$MAX_FILES)
    if [ -z "$TARGETS" ] && [ "$(git rev-list --count HEAD 2>/dev/null || echo 0)" -le 1 ]; then
        TARGETS=$(git ls-files '*.py' 2>/dev/null | head -$MAX_FILES)
    fi
fi

if [ -z "$TARGETS" ]; then
    echo "[$TIMESTAMP] No Python changes detected. Skipping."
    mkdir -p "$LOG_DIR"
    echo "$TIMESTAMP: skip (no changes)" >> "$LOG_DIR/daily_summary.log"
    exit 0
fi

TARGET_COUNT=$(echo "$TARGETS" | wc -l)
EXPECTED_TASKS=$((TARGET_COUNT * TOTAL_PER_FILE))

# === 実行開始 ===
mkdir -p "$LOG_DIR"

echo "============================================================"
echo "Tier 1 Daily Review — $TIMESTAMP"
echo "============================================================"
echo "Targets: $TARGET_COUNT files"
echo "Specialists: $BASE_COUNT base × $COORDS_PER coords = $TOTAL_PER_FILE/file"
echo "Expected tasks: $EXPECTED_TASKS"
echo "API Keys: $KEY_COUNT"
echo "Max concurrent: $MAX_CONCURRENT"
[ -n "$DRY_RUN" ] && echo "*** DRY RUN MODE ***"
echo "============================================================"
echo ""

TOTAL_STARTED=0
TOTAL_FAILED=0
ERRORS=""

for target in $TARGETS; do
    echo "--- Target: $target ---"
    OUTPUT_FILE="$LOG_DIR/${TIMESTAMP}_$(echo "$target" | tr '/' '_' | sed 's/\.py$//' ).json"
    
    if ! timeout "$TIMEOUT_PER_FILE" "$VENV" "$RUNNER" \
        --tier 1 \
        --derive \
        --target "$target" \
        --output "$OUTPUT_FILE" \
        --max-concurrent "$MAX_CONCURRENT" \
        $DRY_RUN \
        2>&1 | tee -a "$LOG_DIR/${DATE}.log"; then
        ERRORS="${ERRORS}FAIL: ${target}\n"
    fi
    
    # 結果カウント (dry-run 以外)
    if [ -z "$DRY_RUN" ] && [ -f "$OUTPUT_FILE" ]; then
        STARTED=$(python3 -c "
import json
with open('$OUTPUT_FILE') as f:
    d = json.load(f)
s = sum(1 for r in d.get('results',[]) if 'session_id' in r)
f = sum(1 for r in d.get('results',[]) if 'error' in r)
print(f'{s} {f}')
" 2>/dev/null || echo "0 0")
        FILE_STARTED=$(echo "$STARTED" | awk '{print $1}')
        FILE_FAILED=$(echo "$STARTED" | awk '{print $2}')
        TOTAL_STARTED=$((TOTAL_STARTED + FILE_STARTED))
        TOTAL_FAILED=$((TOTAL_FAILED + FILE_FAILED))
        echo "  → Started: $FILE_STARTED, Failed: $FILE_FAILED"
    fi
    echo ""
done

# === サマリー ===
echo "============================================================"
echo "Daily Summary — $TIMESTAMP"
echo "============================================================"
echo "Targets: $TARGET_COUNT files"
echo "Started: $TOTAL_STARTED"
echo "Failed:  $TOTAL_FAILED"
echo "Logs:    $LOG_DIR/${DATE}.log"
echo "============================================================"

# ログ記録
echo "$TIMESTAMP: targets=$TARGET_COUNT started=$TOTAL_STARTED failed=$TOTAL_FAILED" >> "$LOG_DIR/daily_summary.log"

# === 通知 ===
if [ "$TOTAL_FAILED" -gt 0 ] || [ -n "$ERRORS" ]; then
    MSG="⚠️ Tier 1 Daily: ${TOTAL_STARTED} started, ${TOTAL_FAILED} failed (${TARGET_COUNT} files)"
    notify-send "Tier 1 Daily Review" "$MSG" 2>/dev/null || true
    
    # Slack 通知 (SLACK_WEBHOOK_URL が設定されている場合)
    if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
        curl -s -X POST "$SLACK_WEBHOOK_URL" \
            -H 'Content-type: application/json' \
            -d "{\"text\": \"$MSG\"}" >/dev/null 2>&1 || true
    fi
else
    notify-send "✅ Tier 1 Daily Review" "All ${TOTAL_STARTED} tasks started (${TARGET_COUNT} files)" 2>/dev/null || true
fi
