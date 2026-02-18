#!/usr/bin/env bash
# PROOF: [L2/運用] <- scripts/ O4→cron→jules_basanos_cron が担う
# PURPOSE: Jules Daily Pipeline — basanos ローテーション cron 設定
# =================================================================
#
# Cron 設置方法:
#   crontab -e
#   # 以下を追加:
#   0 6  * * * /home/makaron8426/oikos/hegemonikon/scripts/jules_basanos_cron.sh morning
#   0 12 * * * /home/makaron8426/oikos/hegemonikon/scripts/jules_basanos_cron.sh midday
#   0 18 * * * /home/makaron8426/oikos/hegemonikon/scripts/jules_basanos_cron.sh evening
#
# スケジュール:
#   月水金 = basanos (構造化レビュー) + pre-audit
#   火木   = specialist (探索的ランダムレビュー)
#   土日   = 休み
# =================================================================

set -euo pipefail

SLOT="${1:?Usage: $0 <morning|midday|evening>}"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="${PROJECT_ROOT}/logs/specialist_daily"
VENV="${PROJECT_ROOT}/.venv/bin/python"

# ログディレクトリ確保
mkdir -p "${LOG_DIR}"

cd "${PROJECT_ROOT}"

# 曜日取得 (1=月曜 ... 7=日曜)
DOW=$(date +%u)

case "${DOW}" in
    1|3|5)
        # 月水金: basanos mode + pre-audit
        MODE="basanos"
        EXTRA_ARGS="--pre-audit --domains 5"
        ;;
    2|4)
        # 火木: specialist mode
        MODE="specialist"
        EXTRA_ARGS=""
        ;;
    6|7)
        # 土日: 休み
        echo "[$(date '+%Y-%m-%d %H:%M')] Weekend — skipping ${SLOT}" >> "${LOG_DIR}/cron.log"
        exit 0
        ;;
esac

echo "[$(date '+%Y-%m-%d %H:%M')] Starting ${SLOT} slot [${MODE}]" >> "${LOG_DIR}/cron.log"

PYTHONPATH="${PROJECT_ROOT}" "${VENV}" \
    mekhane/symploke/jules_daily_scheduler.py \
    --slot "${SLOT}" \
    --mode "${MODE}" \
    ${EXTRA_ARGS} \
    >> "${LOG_DIR}/cron.log" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M')] Completed ${SLOT} slot [${MODE}]" >> "${LOG_DIR}/cron.log"
