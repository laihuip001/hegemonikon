#!/usr/bin/env bash
# PROOF: [L2/インフラ] <- scripts/ A0→n8n スケジュール実行が必要
# PURPOSE: n8n Execute Command ノードから PKS push を実行するラッパー
#
# Usage (n8n Execute Command node):
#   /home/makaron8426/oikos/hegemonikon/scripts/pks_push.sh
#
# Environment:
#   PKS_MODE: auto|topics (default: auto)
#   PKS_TOPICS: トピック (カンマ区切り、PKS_MODE=topics 時)
#   PKS_MAX: 最大プッシュ件数 (default: 5)
#   PKS_COOLDOWN_HOURS: クールダウン時間 (default: 24)
#   PKS_OUTPUT: テキスト出力先 (default: stdout)

set -euo pipefail

# Project root
PROJECT_ROOT="/home/makaron8426/oikos/hegemonikon"
PYTHON="${PROJECT_ROOT}/.venv/bin/python"

# Proxy avoidance + offline model
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy 2>/dev/null || true

# PKS parameters
MODE="${PKS_MODE:-auto}"
MAX="${PKS_MAX:-5}"
COOLDOWN="${PKS_COOLDOWN_HOURS:-24}"
TOPICS="${PKS_TOPICS:-}"
OUTPUT="${PKS_OUTPUT:-}"

export PKS_COOLDOWN_HOURS="${COOLDOWN}"

# Build command
CMD=("${PYTHON}" -m mekhane.pks.pks_cli push --max "${MAX}")

case "${MODE}" in
  auto)
    CMD+=(--auto)
    ;;
  topics)
    if [[ -z "${TOPICS}" ]]; then
      echo "❌ PKS_MODE=topics requires PKS_TOPICS" >&2
      exit 1
    fi
    CMD+=(--topics "${TOPICS}")
    ;;
  *)
    echo "❌ Unknown PKS_MODE: ${MODE}" >&2
    exit 1
    ;;
esac

# Execute
cd "${PROJECT_ROOT}"
RESULT=$("${CMD[@]}" 2>&1)

# Output
if [[ -n "${OUTPUT}" ]]; then
  echo "${RESULT}" > "${OUTPUT}"
  echo "📄 Output saved to: ${OUTPUT}"
else
  echo "${RESULT}"
fi

# Timestamp
echo ""
echo "---"
echo "⏰ $(date '+%Y-%m-%d %H:%M:%S')"
