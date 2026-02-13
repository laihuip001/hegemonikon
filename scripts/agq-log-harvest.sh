#!/usr/bin/env bash
# agq-log-harvest — Antigravity Log Harvester v1.0
# Language Server のログからセッションメトリクスを収穫する
#
# 使い方:
#   ./agq-log-harvest.sh --env        # 環境スナップショット (/boot 時)
#   ./agq-log-harvest.sh --metrics    # セッションメトリクス (/bye 時)
#   ./agq-log-harvest.sh --summary    # 人間向けサマリー表示
#
# 依存: grep, jq, ps, awk
#
# 起源: 2026-02-12 QuotaWatcher/LSP 調査から着想
# agq-check.sh と対: check=API, harvest=ログ

set -euo pipefail

# --- 定数 ---
LOG_BASE="$HOME/.config/Antigravity/logs"
ENV_FILE="/tmp/agq_env.json"
METRICS_FILE="/tmp/agq_metrics.json"
WS_FILTER="${AGQ_WORKSPACE:-hegemonikon}"

# --- 引数解析 ---
MODE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --env) MODE="env"; shift ;;
    --metrics) MODE="metrics"; shift ;;
    --summary) MODE="summary"; shift ;;
    --help|-h)
      echo "Usage: agq-log-harvest.sh [--env|--metrics|--summary]"
      exit 0 ;;
    *) shift ;;
  esac
done

if [[ -z "$MODE" ]]; then
  echo "❌ モードを指定してください: --env, --metrics, --summary" >&2
  exit 1
fi

# --- ヘルパー関数 ---

# 最新のログセッションディレクトリを取得
find_latest_log_session() {
  local d latest=""
  # Antigravity.log が存在するセッションに絞り込む（空セッションをスキップ）
  for d in $(ls -1d "$LOG_BASE"/20* 2>/dev/null | sort); do
    if find "$d" -name "Antigravity.log" -size +0c 2>/dev/null | grep -q .; then
      latest="$d"
    fi
  done
  if [[ -z "$latest" ]]; then
    # フォールバック — Antigravity.log がなくても最新セッションを返す
    latest=$(ls -1d "$LOG_BASE"/20* 2>/dev/null | sort | tail -1)
  fi
  if [[ -z "$latest" ]]; then
    echo "❌ ログセッションが見つかりません" >&2
    return 1
  fi
  echo "$latest"
}

# Antigravity.log のパスを検出 (window1/exthost/google.antigravity/ 配下)
find_antigravity_log() {
  local session_dir="$1"
  local log_path
  # 現 PID に対応する window のログを優先 (PID がプロセス引数に一致)
  local pid
  pid=$(ps aux | grep "language_server_linux" | grep -v grep | grep "$WS_FILTER" | awk '{print $2}' | head -1 || echo "")
  if [[ -n "$pid" ]]; then
    log_path=$(find "$session_dir" -path "*/google.antigravity/Antigravity.log" -size +0c 2>/dev/null | while read -r f; do
      if grep -q "$pid" "$f" 2>/dev/null; then echo "$f"; break; fi
    done)
  fi
  # フォールバック — 最大サイズのログを使用
  if [[ -z "$log_path" ]]; then
    log_path=$(find "$session_dir" -path "*/google.antigravity/Antigravity.log" -size +0c 2>/dev/null | \
      xargs ls -S 2>/dev/null | head -1)
  fi
  if [[ -z "$log_path" ]]; then
    return 1
  fi
  echo "$log_path"
}

# Gemini Code Assist.log のパスを検出
find_gca_log() {
  local session_dir="$1"
  local log_path
  log_path=$(find "$session_dir" -name "*Gemini Code Assist.log" -not -name "*Agent*" 2>/dev/null | tail -1)
  if [[ -z "$log_path" || ! -s "$log_path" ]]; then
    return 1
  fi
  echo "$log_path"
}

# Language Server プロセス情報を取得
get_ls_process_info() {
  local proc_line
  proc_line=$(ps aux | grep "language_server_linux" | grep -v grep | grep "$WS_FILTER" | head -1 || true)
  if [[ -z "$proc_line" ]]; then
    return 1
  fi
  echo "$proc_line"
}

# --- ENV モード: 環境スナップショット ---
mode_env() {
  local session_dir ag_log proc_line
  session_dir=$(find_latest_log_session) || exit 1
  ag_log=$(find_antigravity_log "$session_dir" || echo "")
  proc_line=$(get_ls_process_info || echo "")

  # PID
  local pid="0"
  if [[ -n "$proc_line" ]]; then
    pid=$(echo "$proc_line" | awk '{print $2}')
  fi

  # ポート情報 (ログから — 現PIDのエントリを優先)
  local https_port="0" http_port="0" ext_port="0"
  if [[ -n "$ag_log" && -n "$pid" && "$pid" != "0" ]]; then
    https_port=$(grep "$pid" "$ag_log" | grep -oP 'listening on random port at \K\d+(?= for HTTPS)' | tail -1 || echo "0")
    http_port=$(grep "$pid" "$ag_log" | grep -oP 'listening on random port at \K\d+(?= for HTTP)' | tail -1 || echo "0")
    ext_port=$(grep -oP 'extension server client at port \K\d+' "$ag_log" | tail -1 || echo "0")
  elif [[ -n "$ag_log" ]]; then
    https_port=$(grep -oP 'listening on random port at \K\d+(?= for HTTPS)' "$ag_log" | tail -1 || echo "0")
    http_port=$(grep -oP 'listening on random port at \K\d+(?= for HTTP)' "$ag_log" | tail -1 || echo "0")
    ext_port=$(grep -oP 'extension server client at port \K\d+' "$ag_log" | tail -1 || echo "0")
  fi

  # Cloud endpoint (プロセス引数から)
  local cloud_ep=""
  if [[ -n "$proc_line" ]]; then
    cloud_ep=$(echo "$proc_line" | grep -oP 'cloud_code_endpoint \K\S+' || echo "")
  fi

  # Workspace ID
  local ws_id=""
  if [[ -n "$proc_line" ]]; then
    ws_id=$(echo "$proc_line" | grep -oP 'workspace_id \K\S+' || echo "")
  fi

  # セッションディレクトリ名
  local session_name
  session_name=$(basename "$session_dir")

  jq -n \
    --arg ts "$(date -Iseconds)" \
    --argjson pid "$pid" \
    --argjson https_port "${https_port:-0}" \
    --argjson http_port "${http_port:-0}" \
    --argjson ext_port "${ext_port:-0}" \
    --arg cloud_ep "$cloud_ep" \
    --arg ws_id "$ws_id" \
    --arg session_dir "$session_name" \
    '{
      timestamp: $ts,
      ls_pid: $pid,
      ports: {https: $https_port, http: $http_port, extension: $ext_port},
      cloud_endpoint: $cloud_ep,
      workspace: $ws_id,
      session_log_dir: $session_dir
    }' > "$ENV_FILE"

  echo "📸 Env snapshot saved: $ENV_FILE"
  jq '.' "$ENV_FILE"
}

# --- METRICS モード: セッションメトリクス ---
mode_metrics() {
  local session_dir ag_log
  session_dir=$(find_latest_log_session) || exit 1
  ag_log=$(find_antigravity_log "$session_dir" || echo "")

  if [[ -z "$ag_log" ]]; then
    echo "⚠️  Antigravity.log が見つかりません" >&2
    jq -n '{timestamp: now | todate, api_calls: 0, ctx_messages: [], ctx_max: 0, errors: 0, browser_ops: 0}' > "$METRICS_FILE"
    echo "📊 Empty metrics saved: $METRICS_FILE"
    return 0
  fi

  # API 呼出し回数 (grep -c は 0 件で exit 1 → || true で吸収)
  local api_calls
  api_calls=$(grep -c "planner_generator.go.*Requesting planner" "$ag_log" 2>/dev/null || true)
  api_calls="${api_calls:-0}"

  # コンテキストサイズ推移 (N chat messages の列)
  local ctx_json
  ctx_json=$(grep -oP 'with \K\d+(?= chat messages)' "$ag_log" 2>/dev/null | jq -Rs 'split("\n") | map(select(. != "") | tonumber)' 2>/dev/null || true)
  ctx_json="${ctx_json:-[]}"

  # 最大コンテキスト
  local ctx_max
  ctx_max=$(echo "$ctx_json" | jq 'max // 0' 2>/dev/null || true)
  ctx_max="${ctx_max:-0}"

  # エラー数 (Antigravity.log 内のエラー行)
  local errors
  errors=$(grep -ci '\[error\]' "$ag_log" 2>/dev/null || true)
  errors="${errors:-0}"

  # ブラウザ操作数
  local browser_ops
  browser_ops=$(grep -c 'operator.go.*cascadeId' "$ag_log" 2>/dev/null || true)
  browser_ops="${browser_ops:-0}"

  # セッションディレクトリ名
  local session_name
  session_name=$(basename "$session_dir")

  jq -n \
    --arg ts "$(date -Iseconds)" \
    --argjson api_calls "$api_calls" \
    --argjson ctx_messages "$ctx_json" \
    --argjson ctx_max "$ctx_max" \
    --argjson errors "$errors" \
    --argjson browser_ops "$browser_ops" \
    --arg session_dir "$session_name" \
    '{
      timestamp: $ts,
      api_calls: $api_calls,
      ctx_messages: $ctx_messages,
      ctx_max: $ctx_max,
      errors: $errors,
      browser_ops: $browser_ops,
      session_log_dir: $session_dir
    }' > "$METRICS_FILE"

  echo "📊 Metrics saved: $METRICS_FILE"
}

# --- SUMMARY モード: 人間向けサマリー ---
mode_summary() {
  # まず metrics を収穫
  mode_metrics > /dev/null 2>&1

  if [[ ! -f "$METRICS_FILE" ]]; then
    echo "❌ メトリクスファイルが見つかりません" >&2
    exit 1
  fi

  local api ctx_max errors browser_ops ctx_msgs
  api=$(jq -r '.api_calls' "$METRICS_FILE")
  ctx_max=$(jq -r '.ctx_max' "$METRICS_FILE")
  errors=$(jq -r '.errors' "$METRICS_FILE")
  browser_ops=$(jq -r '.browser_ops' "$METRICS_FILE")
  ctx_msgs=$(jq -r '.ctx_messages | length' "$METRICS_FILE")

  # Context Rot 判定
  local ctx_status="🟢"
  if [[ "$ctx_max" -gt 50 ]]; then
    ctx_status="🔴"
  elif [[ "$ctx_max" -gt 30 ]]; then
    ctx_status="🟡"
  fi

  echo "┌─────────────────────────────────────────────────┐"
  echo "│ 📊 Session Log Metrics"
  echo "├─────────────────────────────────────────────────┤"
  printf "│ 🔄 API Calls:        %s\n" "$api"
  printf "│ %s Context Peak:     %s msgs (from %s requests)\n" "$ctx_status" "$ctx_max" "$ctx_msgs"
  printf "│ ❌ Errors:            %s\n" "$errors"
  printf "│ 🌐 Browser Ops:      %s\n" "$browser_ops"
  echo "└─────────────────────────────────────────────────┘"

  if [[ "$ctx_max" -gt 50 ]]; then
    echo "⚠️  Context Rot 警告: N=$ctx_max > 50 — /bye を検討してください"
  fi
}

# --- メイン ---
case "$MODE" in
  env) mode_env ;;
  metrics) mode_metrics ;;
  summary) mode_summary ;;
esac
