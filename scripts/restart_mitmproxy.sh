#!/bin/bash
# mitmproxy Cortex API 傍受の再起動スクリプト
# 使い方: source scripts/restart_mitmproxy.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. venv がなければ作成
if [ ! -d /tmp/mitmproxy-env ]; then
    python3 -m venv /tmp/mitmproxy-env
    /tmp/mitmproxy-env/bin/pip install mitmproxy
fi

# 2. mitmdump 起動
/tmp/mitmproxy-env/bin/mitmdump -p 8765 \
    -s "$SCRIPT_DIR/capture_cortex_token.py" \
    --set ssl_insecure=true &

# 3. 環境変数設定
export HTTP_PROXY=http://127.0.0.1:8765
export HTTPS_PROXY=http://127.0.0.1:8765
export NO_PROXY=localhost,127.0.0.1,::1
export SSL_CERT_FILE=$HOME/.mitmproxy/mitmproxy-ca-cert.pem
export REQUESTS_CA_BUNDLE=$HOME/.mitmproxy/mitmproxy-ca-cert.pem

echo "✅ mitmproxy started on :8765"
echo "   To stop: kill %1 && unset HTTP_PROXY HTTPS_PROXY SSL_CERT_FILE REQUESTS_CA_BUNDLE"
