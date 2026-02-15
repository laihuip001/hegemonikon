#!/bin/bash
# V12 Phase 3: Cortex HTTP/2 Capture — Permission Fix
#
# 前回の問題:
#   1. root で作ったログファイルに makaron8426 の tee が書けない
#   2. su - が DISPLAY を要求
#
set -euo pipefail

LS_DIR="/usr/share/antigravity/resources/app/extensions/antigravity/bin"
LS_BIN="$LS_DIR/language_server_linux_x64"
LS_ORIG="$LS_DIR/language_server_linux_x64.orig"
LOG="/tmp/ls_http2_cortex_v12.log"
HGK_DIR="/home/makaron8426/oikos/hegemonikon"
TARGET_USER="makaron8426"

echo "🔧 V12 Phase 3: Cortex HTTP/2 Frame Capture (Fixed)"
echo "===================================================="

# Step 1: Backup
echo "[1/7] Backing up LS binary..."
if [ -f "$LS_ORIG" ]; then
  echo "  ⚠️  .orig exists, skipping backup"
else
  cp "$LS_BIN" "$LS_ORIG"
  echo "  ✅ Backup done"
fi

# Step 2: Install wrapper
echo "[2/7] Installing GODEBUG wrapper..."
rm -f "$LS_BIN"
cat > "$LS_BIN" << 'WRAPPER'
#!/bin/bash
export GODEBUG=http2debug=2
SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
ORIG="$SELF_DIR/language_server_linux_x64.orig"
LOG="/tmp/ls_http2_cortex_v12.log"
echo "=== V12 Wrapper: $(date -Iseconds) ===" >> "$LOG"
echo "Args: $@" >> "$LOG"
echo "PID: $$, USER: $(whoami)" >> "$LOG"
echo "---" >> "$LOG"
exec "$ORIG" "$@" 2> >(tee -a "$LOG" >&2)
WRAPPER
chmod +x "$LS_BIN"
echo "  ✅ Wrapper installed"

# Step 3: Create log with CORRECT permissions
echo "[3/7] Creating log file (owned by $TARGET_USER)..."
touch "$LOG"
chown "$TARGET_USER:$TARGET_USER" "$LOG"
chmod 666 "$LOG"
> "$LOG"
echo "  ✅ Log ready: $LOG (owner: $TARGET_USER)"

# Step 4: Kill LS
echo "[4/7] Killing LS processes..."
pkill -f 'language_server_linux.*server_port' || echo "  No LS running"
echo "  ✅ LS killed"

# Step 5: Wait
echo "[5/7] Waiting 25s for IDE restart..."
sleep 25
if pgrep -f 'language_server_linux.*server_port' > /dev/null 2>&1; then
  echo "  ✅ LS restarted"
else
  echo "  Waiting 15s more..."
  sleep 15
  if pgrep -f 'language_server_linux.*server_port' > /dev/null 2>&1; then
    echo "  ✅ LS restarted (delayed)"
  else
    echo "  ❌ LS not running. Restoring..."
    mv "$LS_ORIG" "$LS_BIN" && chmod +x "$LS_BIN"
    exit 1
  fi
fi

# Step 6: Call Claude (as user, without su -)
echo "[6/7] Calling Claude..."
sudo -u "$TARGET_USER" -H bash -c "cd $HGK_DIR && python3 mekhane/ochema/claude_cli.py -m 'Say hello in one word' --raw --timeout 90" 2>&1 || echo "  ⚠️  Call may have failed"
sleep 5

# Step 7: Restore
echo "[7/7] Restoring original..."
rm -f "$LS_BIN"
mv "$LS_ORIG" "$LS_BIN"
chmod +x "$LS_BIN"
echo "  ✅ Restored"

# Summary
echo ""
echo "===================================================="
echo "📊 Results"
echo "===================================================="
echo "Log: $LOG"
LINES=$(wc -l < "$LOG")
echo "Lines: $LINES"
if [ "$LINES" -gt 0 ]; then
  echo ""
  echo "=== External hosts ==="
  grep 'encoding header ":authority"' "$LOG" 2>/dev/null | sed 's/.*= "//' | tr -d '"' | sort -u
  echo ""
  echo "=== Cortex connections ==="
  grep -i 'cloudcode\|cortex\|216.58.220\|142.250' "$LOG" 2>/dev/null | head -5 || echo "  None"
  echo ""
  echo "=== Bearer tokens ==="
  grep 'Bearer' "$LOG" 2>/dev/null | head -3 || echo "  None"
  echo ""
  echo "=== Cascade/LLM paths ==="
  grep -i ':path.*cascade\|:path.*generate\|:path.*planner\|:path.*StreamGenerate\|requestedModel\|requested_model' "$LOG" 2>/dev/null | head -10 || echo "  None"
else
  echo "  ❌ Log is empty — wrapper stderr redirect may have failed"
  echo ""
  echo "  Debug: checking if wrapper ran..."
  pgrep -a -f 'language_server_linux' | head -2
fi
