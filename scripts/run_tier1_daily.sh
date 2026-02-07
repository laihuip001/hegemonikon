#!/bin/bash
# PROOF: [L3/ユーティリティ] <- scripts/ O4→Tier1定点実行が必要→run_tier1_daily が担う
# ============================================================
# Tier 1 Daily Review — 朝4時定点実行
# 
# 全派生 (13基本 × 8派生 = 104人/ファイル) を
# 前日変更された Python ファイルに対して自動実行する
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
MAX_FILES=20          # API枠飽和防止: 20ファイル × 104派生 = 2080 (上限内)
MAX_CONCURRENT=5      # 並列数
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
    exit 1
fi

# === ターゲット決定 ===
if [ -n "$FIXED_TARGET" ]; then
    TARGETS="$FIXED_TARGET"
else
    # 前日変更ファイル (Python のみ)
    TARGETS=$(git diff --name-only HEAD~1 -- '*.py' 2>/dev/null | head -$MAX_FILES)
fi

if [ -z "$TARGETS" ]; then
    echo "[$TIMESTAMP] No Python changes detected. Skipping."
    mkdir -p "$LOG_DIR"
    echo "$TIMESTAMP: skip (no changes)" >> "$LOG_DIR/daily_summary.log"
    exit 0
fi

TARGET_COUNT=$(echo "$TARGETS" | wc -l)
EXPECTED_TASKS=$((TARGET_COUNT * 104))

# === 実行開始 ===
mkdir -p "$LOG_DIR"

echo "============================================================"
echo "Tier 1 Daily Review — $TIMESTAMP"
echo "============================================================"
echo "Targets: $TARGET_COUNT files"
echo "Derivatives: 104/file (13 base × 8 variants)"
echo "Expected tasks: $EXPECTED_TASKS"
echo "API Keys: $KEY_COUNT"
echo "Max concurrent: $MAX_CONCURRENT"
[ -n "$DRY_RUN" ] && echo "*** DRY RUN MODE ***"
echo "============================================================"
echo ""

TOTAL_STARTED=0
TOTAL_FAILED=0

for target in $TARGETS; do
    echo "--- Target: $target ---"
    OUTPUT_FILE="$LOG_DIR/${TIMESTAMP}_$(echo "$target" | tr '/' '_' | sed 's/\.py$//' ).json"
    
    timeout 600 "$VENV" "$RUNNER" \
        --tier 1 \
        --derive \
        --target "$target" \
        --output "$OUTPUT_FILE" \
        --max-concurrent "$MAX_CONCURRENT" \
        $DRY_RUN \
        2>&1 | tee -a "$LOG_DIR/${DATE}.log"
    
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
