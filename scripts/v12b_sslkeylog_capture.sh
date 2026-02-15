#!/bin/bash
# V12b: SSLKEYLOGFILE + tcpdump Cortex gRPC Capture
#
# Go の crypto/tls.writeKeyLog が SSLKEYLOGFILE をサポートしている前提で、
# TLS session keys をダンプしつつ tcpdump でパケットを取る。
# Wireshark/tshark で後から復号可能。
#
# 使い方: sudo bash scripts/v12b_sslkeylog_capture.sh
#
set -euo pipefail

LS_DIR="/usr/share/antigravity/resources/app/extensions/antigravity/bin"
LS_BIN="$LS_DIR/language_server_linux_x64"
LS_ORIG="$LS_DIR/language_server_linux_x64.orig"
KEYLOG="/tmp/ls_sslkeylog.txt"
PCAP="/tmp/ls_cortex_capture.pcap"
HGK_DIR="/home/makaron8426/oikos/hegemonikon"
TARGET_USER="makaron8426"

echo "🔧 V12b: SSLKEYLOGFILE + tcpdump Capture"
echo "=========================================="

# Cloudcode IPs
echo ""
echo "[0/8] Resolving cloudcode-pa IPs..."
CORTEX_IPS=$(host daily-cloudcode-pa.googleapis.com 2>/dev/null | grep 'has address' | awk '{print $NF}' | tr '\n' ' ')
echo "  Cortex IPs: $CORTEX_IPS"

# Step 1: Backup
echo ""
echo "[1/8] Backing up LS binary..."
if [ -f "$LS_ORIG" ]; then
  echo "  ⚠️  .orig exists, skipping"
else
  cp "$LS_BIN" "$LS_ORIG"
  echo "  ✅ Backup done"
fi

# Step 2: Install wrapper (SSLKEYLOGFILE + GODEBUG)
echo ""
echo "[2/8] Installing SSLKEYLOGFILE wrapper..."
rm -f "$LS_BIN"
cat > "$LS_BIN" << 'WRAPPER'
#!/bin/bash
# SSLKEYLOGFILE = Go crypto/tls が TLS master secrets を書き出す
export SSLKEYLOGFILE="/tmp/ls_sslkeylog.txt"
# GODEBUG も併用 (net/http2 部分)
export GODEBUG=http2debug=2

SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
ORIG="$SELF_DIR/language_server_linux_x64.orig"
DEBUGLOG="/tmp/ls_http2_cortex_v12b.log"

echo "=== V12b Wrapper: $(date -Iseconds) ===" >> "$DEBUGLOG" 2>/dev/null || true
echo "SSLKEYLOGFILE=$SSLKEYLOGFILE" >> "$DEBUGLOG" 2>/dev/null || true
exec "$ORIG" "$@" 2>> "$DEBUGLOG"
WRAPPER
chmod +x "$LS_BIN"
echo "  ✅ Wrapper installed"

# Step 3: Prepare log files
echo ""
echo "[3/8] Preparing log files..."
for f in "$KEYLOG" "/tmp/ls_http2_cortex_v12b.log"; do
  rm -f "$f"
  sudo -u "$TARGET_USER" touch "$f"
  chmod 666 "$f"
done
echo "  ✅ $KEYLOG"
echo "  ✅ /tmp/ls_http2_cortex_v12b.log"

# Step 4: Kill LS
echo ""
echo "[4/8] Killing LS processes..."
pkill -f 'language_server_linux.*server_port' || echo "  No LS"
echo "  ✅ Killed"

# Step 5: Wait + start tcpdump
echo ""
echo "[5/8] Starting tcpdump for cloudcode-pa traffic..."
# Capture traffic to known Cortex IPs + any HTTPS (443)
tcpdump -i any -w "$PCAP" 'port 443' &
TCPDUMP_PID=$!
echo "  ✅ tcpdump started (PID: $TCPDUMP_PID)"
chmod 666 "$PCAP"

# Step 6: Wait for LS restart
echo ""
echo "[6/8] Waiting 25s for LS restart..."
sleep 25
if pgrep -f 'language_server_linux.*server_port' > /dev/null 2>&1; then
  echo "  ✅ LS restarted"
else
  echo "  Waiting 15s more..."
  sleep 15
  if pgrep -f 'language_server_linux.*server_port' > /dev/null 2>&1; then
    echo "  ✅ LS restarted (delayed)"
  else
    echo "  ❌ LS failed. Restoring..."
    kill $TCPDUMP_PID 2>/dev/null
    mv "$LS_ORIG" "$LS_BIN" && chmod +x "$LS_BIN"
    exit 1
  fi
fi

# Step 7: Call Claude
echo ""
echo "[7/8] Calling Claude..."
sudo -u "$TARGET_USER" -H bash -c "cd $HGK_DIR && python3 mekhane/ochema/claude_cli.py -m 'Say hello' --raw --timeout 90" 2>&1 || echo "  ⚠️  Call may have failed"
sleep 5

# Step 8: Stop tcpdump & restore
echo ""
echo "[8/8] Cleaning up..."
kill $TCPDUMP_PID 2>/dev/null
sleep 2

rm -f "$LS_BIN"
mv "$LS_ORIG" "$LS_BIN"
chmod +x "$LS_BIN"
echo "  ✅ Original restored"

# Summary
echo ""
echo "=========================================="
echo "📊 V12b Results"
echo "=========================================="

echo ""
echo "=== SSLKEYLOGFILE ==="
if [ -s "$KEYLOG" ]; then
  echo "  ✅ TLS keys captured!"
  wc -l "$KEYLOG"
  head -3 "$KEYLOG"
else
  echo "  ❌ Empty — Go runtime may not honor SSLKEYLOGFILE without explicit KeyLogWriter config"
fi

echo ""
echo "=== tcpdump PCAP ==="
ls -la "$PCAP"
echo "  Packets to cloudcode-pa IPs:"
for ip in $CORTEX_IPS; do
  COUNT=$(tcpdump -r "$PCAP" "host $ip" 2>/dev/null | wc -l)
  echo "    $ip: $COUNT packets"
done

echo ""
echo "=== HTTP/2 debug log ==="
wc -l /tmp/ls_http2_cortex_v12b.log

echo ""
echo "=== External authorities ==="
grep 'encoding header ":authority"' /tmp/ls_http2_cortex_v12b.log 2>/dev/null | sed 's/.*= "//' | tr -d '"' | sort -u

echo ""
echo "=== TLS SNI (from pcap) ==="
tcpdump -r "$PCAP" -nn 2>/dev/null | grep -oP '(?<=SNI: )[^\s]+' | sort -u 2>/dev/null || \
  echo "  (SNI extraction requires tshark for full analysis)"

echo ""
echo "FILES:"
echo "  PCAP: $PCAP"
echo "  SSLKEYLOG: $KEYLOG"
echo "  HTTP/2 LOG: /tmp/ls_http2_cortex_v12b.log"
echo ""
echo "復号: tshark -r $PCAP -o tls.keylog_file:$KEYLOG -Y 'http2' -V"
