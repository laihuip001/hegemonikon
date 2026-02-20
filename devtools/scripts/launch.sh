#!/usr/bin/env bash
# HGK DevTools — Launcher Script
# Starts Vite dev server + opens in default browser

set -euo pipefail

DEVTOOLS_DIR="$(cd "$(dirname "$0")/.." && pwd)"
GATEWAY_PORT=9696
DEVTOOLS_PORT=3000
LOG_DIR="$DEVTOOLS_DIR/logs"
PID_FILE="$LOG_DIR/devtools.pid"

mkdir -p "$LOG_DIR"

# ─── Functions ─────────────────────────────────────────────────

cleanup() {
    echo "[HGK DevTools] Shutting down..."
    if [ -f "$PID_FILE" ]; then
        local pid
        pid=$(cat "$PID_FILE")
        kill "$pid" 2>/dev/null || true
        rm -f "$PID_FILE"
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

check_port() {
    local port=$1
    if command -v ss &>/dev/null; then
        ss -tlnp 2>/dev/null | grep -q ":${port} " && return 0
    elif command -v netstat &>/dev/null; then
        netstat -tlnp 2>/dev/null | grep -q ":${port} " && return 0
    fi
    return 1
}

wait_for_port() {
    local port=$1
    local max_wait=${2:-15}
    local waited=0
    while ! check_port "$port"; do
        sleep 1
        waited=$((waited + 1))
        if [ "$waited" -ge "$max_wait" ]; then
            echo "[HGK DevTools] ⚠️  Port $port did not start within ${max_wait}s"
            return 1
        fi
    done
    return 0
}

# ─── Pre-flight ────────────────────────────────────────────────

cd "$DEVTOOLS_DIR"

# Check node_modules
if [ ! -d "node_modules" ]; then
    echo "[HGK DevTools] Installing dependencies..."
    npm install
fi

# ─── Gateway Check ─────────────────────────────────────────────

if ! check_port "$GATEWAY_PORT"; then
    echo "[HGK DevTools] ⚠️  Gateway (port $GATEWAY_PORT) is not running."
    echo "[HGK DevTools] File explorer and terminal will be offline."
    echo "[HGK DevTools] Start Gateway: cd ~/oikos/hegemonikon && .venv/bin/python -m mekhane.api.server --port $GATEWAY_PORT"
fi

# ─── Vite Dev Server ──────────────────────────────────────────

if check_port "$DEVTOOLS_PORT"; then
    echo "[HGK DevTools] Dev server already running on port $DEVTOOLS_PORT"
else
    echo "[HGK DevTools] Starting Vite dev server on port $DEVTOOLS_PORT..."
    npx vite --port "$DEVTOOLS_PORT" --host > "$LOG_DIR/vite.log" 2>&1 &
    echo $! > "$PID_FILE"
    
    if ! wait_for_port "$DEVTOOLS_PORT" 15; then
        echo "[HGK DevTools] ❌ Failed to start dev server"
        cat "$LOG_DIR/vite.log"
        exit 1
    fi
    echo "[HGK DevTools] ✅ Dev server started"
fi

# ─── Open Browser ──────────────────────────────────────────────

URL="http://localhost:${DEVTOOLS_PORT}"
echo "[HGK DevTools] Opening $URL"

if command -v xdg-open &>/dev/null; then
    xdg-open "$URL" 2>/dev/null &
elif command -v sensible-browser &>/dev/null; then
    sensible-browser "$URL" 2>/dev/null &
elif command -v google-chrome &>/dev/null; then
    google-chrome "$URL" 2>/dev/null &
elif command -v firefox &>/dev/null; then
    firefox "$URL" 2>/dev/null &
fi

echo "[HGK DevTools] ⚡ HGK DevTools is running"
echo "[HGK DevTools] Press Ctrl+C to stop"

# Keep alive
wait
