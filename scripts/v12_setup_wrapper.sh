#!/bin/bash
# V12: GODEBUG HTTP/2 Frame Dump — LS Binary Wrapper
#
# LS バイナリのパスに wrapper を配置し、GODEBUG=http2debug=2 付きで
# 元のバイナリを exec する。stderr を /tmp/ls_http2_debug.log に tee。
#
# 使い方:
#   1. sudo ./v12_setup_wrapper.sh install    # wrapper を設置
#   2. Antigravity IDE で Claude を呼ぶ
#   3. cat /tmp/ls_http2_debug.log            # HTTP/2 フレーム確認
#   4. sudo ./v12_setup_wrapper.sh uninstall  # 元に戻す
#
# WARNING: IDE の LS を変更する破壊的操作。自己責任。

set -euo pipefail

LS_DIR="/usr/share/antigravity/resources/app/extensions/antigravity/bin"
LS_BIN="$LS_DIR/language_server_linux_x64"
LS_ORIG="$LS_DIR/language_server_linux_x64.orig"
LS_LOG="/tmp/ls_http2_debug.log"

case "${1:-}" in
  install)
    if [ -f "$LS_ORIG" ]; then
      echo "⚠️  Already installed (orig file exists)"
      exit 1
    fi

    echo "📦 Backing up original LS binary..."
    cp "$LS_BIN" "$LS_ORIG"

    echo "📝 Creating wrapper..."
    cat > "$LS_BIN" << 'WRAPPER'
#!/bin/bash
# V12 GODEBUG wrapper — HTTP/2 debug output を stderr と log に tee
export GODEBUG=http2debug=2

SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
ORIG="$SELF_DIR/language_server_linux_x64.orig"
LOG="/tmp/ls_http2_debug.log"

echo "=== V12 GODEBUG Wrapper Started: $(date -Iseconds) ===" >> "$LOG"
echo "Args: $@" >> "$LOG"
echo "GODEBUG=$GODEBUG" >> "$LOG"
echo "---" >> "$LOG"

# exec で元の LS を実行、stderr を log にもコピー
exec "$ORIG" "$@" 2> >(tee -a "$LOG" >&2)
WRAPPER

    chmod +x "$LS_BIN"

    echo "✅ Wrapper installed."
    echo "   Next: IDE を再起動して Claude を呼ぶ → $LS_LOG を確認"
    ;;

  uninstall)
    if [ ! -f "$LS_ORIG" ]; then
      echo "⚠️  Not installed (no orig file)"
      exit 1
    fi

    echo "🔄 Restoring original LS binary..."
    mv "$LS_ORIG" "$LS_BIN"
    chmod +x "$LS_BIN"

    echo "✅ Original restored."
    ;;

  status)
    if [ -f "$LS_ORIG" ]; then
      echo "📦 Wrapper INSTALLED"
      file "$LS_BIN" | head -1
      echo "Log: $LS_LOG ($(wc -l < "$LS_LOG" 2>/dev/null || echo 0) lines)"
    else
      echo "📦 Wrapper NOT installed"
    fi
    ;;

  *)
    echo "Usage: $0 {install|uninstall|status}"
    exit 1
    ;;
esac
