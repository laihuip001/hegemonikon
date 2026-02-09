#!/usr/bin/env bash
# sync_config.sh — HGK テキスト設定ファイルを Syncthing ディレクトリへ自動同期
# 用途: cron / /bye / 手動実行
# 方向: HGK → Sync (一方向)

set -euo pipefail

# ── 定数 ──────────────────────────────────────────
HGK_ROOT="$HOME/oikos/hegemonikon"
SYNC_ROOT="$HOME/Sync/15_🏛️_ヘゲモニコン｜Hegemonikon"
GLOBAL_GEMINI="$HOME/.gemini/GEMINI.md"

DRY_RUN=false
VERBOSE=false

# ── 引数処理 ──────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run|-n) DRY_RUN=true; shift ;;
    --verbose|-v) VERBOSE=true; shift ;;
    --help|-h)
      echo "Usage: $0 [--dry-run] [--verbose]"
      echo "  HGK のテキスト設定ファイルを Sync (Syncthing) へ同期"
      exit 0
      ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# ── 同期対象ファイル (HGK_ROOT からの相対パス) ─────
CONFIG_FILES=(
  ".gemini/GEMINI.md"
  ".claude.json"
  ".markdownlint.json"
  ".pre-commit-config.yaml"
  "projects.yaml"
  "pyproject.toml"
  "requirements.txt"
  "AGENTS.md"
  "README.md"
)

# ── 同期対象ディレクトリ (rsync で再帰的同期) ─────
CONFIG_DIRS=(
  ".agent/"
  "docs/"
  "kernel/"
  "ccl/"
)

# ── 除外パターン ──────────────────────────────────
EXCLUDES=(
  ".env"
  ".env.*"
  "__pycache__"
  "*.pyc"
  ".git/"
)

# ── ユーティリティ ────────────────────────────────
log() { echo "[sync] $*"; }
vlog() { $VERBOSE && echo "[sync:v] $*" || true; }

# ── 個別ファイル同期 ──────────────────────────────
sync_file() {
  local src="$1"
  local dst="$2"
  
  if [[ ! -f "$src" ]]; then
    vlog "SKIP (not found): $src"
    return
  fi
  
  # 変更があるか確認
  if [[ -f "$dst" ]] && cmp -s "$src" "$dst"; then
    vlog "UNCHANGED: $(basename "$src")"
    return
  fi
  
  # ディレクトリ作成
  local dst_dir
  dst_dir=$(dirname "$dst")
  
  if $DRY_RUN; then
    log "WOULD COPY: $src → $dst"
  else
    mkdir -p "$dst_dir"
    cp -p "$src" "$dst"
    log "COPIED: $(basename "$src")"
  fi
}

# ── ディレクトリ同期 ──────────────────────────────
sync_dir() {
  local src="$1"
  local dst="$2"
  
  if [[ ! -d "$src" ]]; then
    vlog "SKIP (not found): $src"
    return
  fi
  
  local rsync_opts="-a --delete"
  for excl in "${EXCLUDES[@]}"; do
    rsync_opts+=" --exclude=$excl"
  done
  
  if $DRY_RUN; then
    rsync_opts+=" --dry-run"
  fi
  
  local changes
  changes=$(rsync $rsync_opts "$src" "$dst" 2>&1 | grep -v "^$" | head -20 || true)
  
  if [[ -n "$changes" ]]; then
    log "DIR $(basename "$src"): $changes"
  else
    vlog "DIR UNCHANGED: $(basename "$src")"
  fi
}

# ── メイン ────────────────────────────────────────
main() {
  log "=== HGK → Sync 同期開始 ==="
  $DRY_RUN && log "(DRY RUN モード)"
  
  # 1. 個別ファイル同期
  for file in "${CONFIG_FILES[@]}"; do
    sync_file "$HGK_ROOT/$file" "$SYNC_ROOT/$file"
  done
  
  # 2. グローバル GEMINI.md
  sync_file "$GLOBAL_GEMINI" "$SYNC_ROOT/.global/GEMINI.md"
  
  # 3. ディレクトリ同期
  for dir in "${CONFIG_DIRS[@]}"; do
    sync_dir "$HGK_ROOT/$dir" "$SYNC_ROOT/$dir"
  done
  
  log "=== 同期完了 ==="
}

main
