#!/bin/bash
# Digestor Scheduler セットアップスクリプト
# 自宅 PC に移行後に実行

set -e

USER=$(whoami)
SERVICE_NAME="digestor-scheduler@${USER}.service"
SERVICE_FILE="/home/${USER}/oikos/hegemonikon/mekhane/ergasterion/digestor/digestor-scheduler@.service"
SYSTEMD_DIR="/etc/systemd/system"

echo "=== Digestor Scheduler Setup ==="
echo "User: ${USER}"
echo "Service: ${SERVICE_NAME}"
echo ""

# 1. サービスファイルをコピー
echo "[1/4] Copying service file..."
sudo cp "${SERVICE_FILE}" "${SYSTEMD_DIR}/"

# 2. systemd リロード
echo "[2/4] Reloading systemd..."
sudo systemctl daemon-reload

# 3. サービス有効化
echo "[3/4] Enabling service..."
sudo systemctl enable "${SERVICE_NAME}"

# 4. サービス開始
echo "[4/4] Starting service..."
sudo systemctl start "${SERVICE_NAME}"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Status check:"
sudo systemctl status "${SERVICE_NAME}" --no-pager

echo ""
echo "Commands:"
echo "  Start:   sudo systemctl start ${SERVICE_NAME}"
echo "  Stop:    sudo systemctl stop ${SERVICE_NAME}"
echo "  Restart: sudo systemctl restart ${SERVICE_NAME}"
echo "  Status:  sudo systemctl status ${SERVICE_NAME}"
echo "  Logs:    cat ~/.hegemonikon/digestor/scheduler.log"
