#!/usr/bin/env bash
# agq-sessions — Antigravity Session History Sync v1
# Language Server の GetAllCascadeTrajectories API から全セッション履歴を取得
#
# 使い方:
#   ./agq-sessions.sh --summary              # セッション統計 (/boot 用)
#   ./agq-sessions.sh --dump                 # 全セッションを JSON に保存
#   ./agq-sessions.sh --export-current       # 現在セッションを Markdown にエクスポート (/bye 用)
#   ./agq-sessions.sh --index                # セッション履歴を LanceDB にインデックス
#   ./agq-sessions.sh --list                 # セッション一覧
#
# 依存: curl, python3, ps, grep, ss
# 内部: agq-sessions-parser.py (protobuf テキスト抽出)
#
# 起源: 2026-02-13 gRPC セッション履歴自動同期
# API: /exa.language_server_pb.LanguageServerService/GetAllCascadeTrajectories

set -euo pipefail

# --- 定数 ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARSER="$SCRIPT_DIR/agq-sessions-parser.py"
PYTHON="${PYTHON:-python3}"
EXPORT_DIR="${HOME}/oikos/mneme/.hegemonikon/sessions"
DUMP_DIR="/tmp/agq_sessions"

# --- 引数解析 ---
MODE="summary"
WS_FILTER="hegemonikon"
OUTPUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --summary)        MODE="summary"; shift ;;
    --dump)           MODE="dump"; shift ;;
    --export-current) MODE="export"; shift ;;
    --index)          MODE="index"; shift ;;
    --list)           MODE="summary"; shift ;;  # alias
    --output)         OUTPUT="$2"; shift 2 ;;
    --workspace)      WS_FILTER="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: agq-sessions.sh [--summary|--dump|--export-current] [--output PATH] [--workspace NAME]"
      echo ""
      echo "Modes:"
      echo "  --summary         Session statistics (for /boot)"
      echo "  --dump            Save all sessions to JSON (for analysis)"
      echo "  --export-current  Export current session as Markdown (for /bye Step 3.5)"
      echo "  --index           Index sessions into LanceDB (vector search)"
      echo ""
      echo "Options:"
      echo "  --output PATH     Override output path"
      echo "  --workspace NAME  Workspace filter (default: hegemonikon)"
      exit 0 ;;
    *) WS_FILTER="$1"; shift ;;
  esac
done

# --- Step 1: プロセス検出 (agq-check.sh と同じパターン) ---
PROC_LINE=$(ps aux | grep "language_server_linux" | grep -v grep | grep "$WS_FILTER" | head -1 || true)

if [[ -z "$PROC_LINE" ]]; then
  echo "❌ Language Server プロセスが見つかりません (workspace: $WS_FILTER)" >&2
  exit 1
fi

CSRF=$(echo "$PROC_LINE" | grep -oP 'csrf_token \K[^ ]+')
PID=$(echo "$PROC_LINE" | awk '{print $2}')

if [[ -z "$CSRF" ]]; then
  echo "❌ CSRF トークンの取得に失敗しました" >&2
  exit 1
fi

# --- Step 2: リスニングポート取得 ---
mapfile -t PORTS < <(ss -tlnp 2>/dev/null | grep "pid=$PID" | grep -oP '127\.0\.0\.1:\K\d+' | sort -u)

if [[ ${#PORTS[@]} -eq 0 ]]; then
  echo "❌ リスニングポートが見つかりません (PID: $PID)" >&2
  exit 1
fi

# --- Step 3: GetAllCascadeTrajectories API 呼出し ---
# Connect Protocol は JSON だが、このエンドポイントは protobuf バイナリを返す。
# --output で直接ファイルに書き出す。

TMPFILE=$(mktemp /tmp/agq_trajectories_XXXXXX.bin)
trap "rm -f $TMPFILE" EXIT

API_OK=false
for port in "${PORTS[@]}"; do
  HTTP_CODE=$(curl -sk --max-time 30 -X POST \
    -H "Content-Type: application/json" \
    -H "X-Codeium-Csrf-Token: $CSRF" \
    -H "Connect-Protocol-Version: 1" \
    -d '{"metadata":{"ideName":"antigravity","extensionName":"antigravity","locale":"en"}}' \
    -o "$TMPFILE" \
    -w "%{http_code}" \
    "https://127.0.0.1:$port/exa.language_server_pb.LanguageServerService/GetAllCascadeTrajectories" 2>/dev/null || echo "000")

  if [[ "$HTTP_CODE" == "200" ]] && [[ -s "$TMPFILE" ]]; then
    API_OK=true
    break
  fi
done

if ! $API_OK; then
  echo "❌ 全ポート (${PORTS[*]}) で GetAllCascadeTrajectories 取得に失敗しました" >&2
  exit 1
fi

FILE_SIZE=$(stat --printf="%s" "$TMPFILE" 2>/dev/null || stat -f%z "$TMPFILE" 2>/dev/null || echo "0")

# --- Step 4: Python パーサーで処理 ---
if [[ ! -f "$PARSER" ]]; then
  echo "❌ パーサーが見つかりません: $PARSER" >&2
  exit 1
fi

# venv の Python を優先、なければシステム Python
if [[ -x "$SCRIPT_DIR/../.venv/bin/python" ]]; then
  PYTHON="$SCRIPT_DIR/../.venv/bin/python"
fi

case "$MODE" in
  summary)
    cat "$TMPFILE" | "$PYTHON" "$PARSER" --mode summary
    echo "📦 Raw data: ${FILE_SIZE} bytes"
    ;;
  dump)
    DUMP_TARGET="${OUTPUT:-$DUMP_DIR}"
    cat "$TMPFILE" | "$PYTHON" "$PARSER" --mode dump --output "$DUMP_TARGET"
    ;;
  export)
    if [[ -n "$OUTPUT" ]]; then
      EXPORT_PATH="$OUTPUT"
    else
      DATE_STR=$(date +%Y-%m-%d)
      EXPORT_PATH="${EXPORT_DIR}/chat_export_${DATE_STR}.md"
      # 同日に既に存在する場合はサフィックスを追加
      if [[ -f "$EXPORT_PATH" ]]; then
        N=2
        while [[ -f "${EXPORT_DIR}/chat_export_${DATE_STR}_${N}.md" ]]; do
          N=$((N + 1))
        done
        EXPORT_PATH="${EXPORT_DIR}/chat_export_${DATE_STR}_${N}.md"
      fi
    fi
    cat "$TMPFILE" | "$PYTHON" "$PARSER" --mode export --output "$EXPORT_PATH"
    ;;
  index)
    # dump to temp dir, then index via session_indexer.py
    INDEX_TMP=$(mktemp -d /tmp/agq_index_XXXXXX)
    cat "$TMPFILE" | "$PYTHON" "$PARSER" --mode dump --output "$INDEX_TMP"
    INDEXER="$SCRIPT_DIR/../mekhane/anamnesis/session_indexer.py"
    if [[ ! -f "$INDEXER" ]]; then
      echo "❌ session_indexer.py が見つかりません: $INDEXER" >&2
      rm -rf "$INDEX_TMP"
      exit 1
    fi
    cd "$SCRIPT_DIR/.."
    PYTHONPATH="." "$PYTHON" "$INDEXER" "$INDEX_TMP/trajectories_raw.json"
    rm -rf "$INDEX_TMP"
    ;;
esac
