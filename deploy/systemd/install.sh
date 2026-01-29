#!/bin/bash
# Swarm Scheduler systemd Installation Script
# 
# Run with: sudo ./install.sh
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYSTEMD_DIR="/etc/systemd/system"

echo "═══════════════════════════════════════════════════════"
echo "  Swarm Scheduler systemd Installation"
echo "═══════════════════════════════════════════════════════"

# Copy files
echo "→ Copying service files..."
cp "$SCRIPT_DIR/swarm-scheduler.timer" "$SYSTEMD_DIR/"
cp "$SCRIPT_DIR/swarm-scheduler.service" "$SYSTEMD_DIR/"

# Reload systemd
echo "→ Reloading systemd daemon..."
systemctl daemon-reload

# Enable timer
echo "→ Enabling swarm-scheduler.timer..."
systemctl enable swarm-scheduler.timer

# Start timer
echo "→ Starting swarm-scheduler.timer..."
systemctl start swarm-scheduler.timer

# Show status
echo ""
echo "═══════════════════════════════════════════════════════"
echo "  Installation Complete!"
echo "═══════════════════════════════════════════════════════"
echo ""
systemctl status swarm-scheduler.timer --no-pager
echo ""
echo "Next scheduled run:"
systemctl list-timers swarm-scheduler.timer --no-pager
echo ""
echo "Commands:"
echo "  • View logs:    journalctl -u swarm-scheduler.service -f"
echo "  • Manual run:   systemctl start swarm-scheduler.service"
echo "  • Disable:      systemctl disable swarm-scheduler.timer"
