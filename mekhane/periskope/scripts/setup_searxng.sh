#!/usr/bin/env bash
# Periskopē SearXNG systemd setup
# Usage: sudo bash setup_searxng.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$(dirname "$SCRIPT_DIR")/docker"
SERVICE_FILE="$DOCKER_DIR/searxng.service"

echo "=== Periskopē SearXNG Setup ==="

# 1. Check Docker
if ! command -v docker &> /dev/null; then
    echo "ERROR: docker not found. Install Docker first."
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "ERROR: docker compose not found."
    exit 1
fi

# 2. Start SearXNG to verify it works
echo "[1/4] Testing SearXNG..."
cd "$DOCKER_DIR"
docker compose up -d
sleep 3

if curl -sf http://localhost:8888/healthz > /dev/null 2>&1; then
    echo "  ✅ SearXNG is healthy"
else
    echo "  ⚠️ SearXNG may need a moment to start (port 8888)"
fi

# 3. Install systemd service
echo "[2/4] Installing systemd service..."
sudo cp "$SERVICE_FILE" /etc/systemd/system/searxng.service
sudo systemctl daemon-reload

# 4. Enable auto-start
echo "[3/4] Enabling auto-start..."
sudo systemctl enable searxng.service

# 5. Verify
echo "[4/4] Verifying..."
sudo systemctl status searxng.service --no-pager || true

echo ""
echo "=== Setup Complete ==="
echo "Commands:"
echo "  systemctl status searxng   # Check status"
echo "  systemctl restart searxng  # Restart"
echo "  systemctl stop searxng     # Stop"
echo "  systemctl disable searxng  # Disable auto-start"
