#!/usr/bin/env bash
# PURPOSE: Cortex API (cloudcode-pa v1internal) 直叩きスクリプト
# 参照: kernel/doxa/DX-010_ide_hack_cortex_direct_access.md
# 
# 使い方:
#   cortex.sh "Hello"                          # 基本 (gemini-2.0-flash)
#   cortex.sh -m gemini-2.5-pro "Hello"        # モデル指定
#   cortex.sh -s "You are a poet" "Write haiku" # system instruction
#   cortex.sh --stream "Hello"                 # ストリーミング
#   cortex.sh --think 1024 "Hard problem"      # thinking budget
#   cortex.sh --raw '{"contents":[...]}'       # raw JSON (requestフィールド)
#   cortex.sh --info                           # loadCodeAssist 情報表示
#   cortex.sh --quota                          # クォータ確認
#
# 環境変数:
#   CORTEX_MODEL        デフォルトモデル (default: gemini-2.0-flash)
#   CORTEX_PROJECT      プロジェクトID (default: 自動取得)
#   CORTEX_MAX_TOKENS   最大出力トークン (default: 8192)
#   CORTEX_TEMPERATURE  温度 (default: 0.7)

set -euo pipefail

# Google API へは直接接続 (mitmproxy 残骸回避)
unset HTTPS_PROXY HTTP_PROXY https_proxy http_proxy 2>/dev/null || true

# ─── Constants ───
readonly CLIENT_ID="REDACTED_CLIENT_ID"
readonly CLIENT_SECRET="REDACTED_CLIENT_SECRET"
readonly CREDS_FILE="$HOME/.gemini/oauth_creds.json"
readonly BASE_URL="https://cloudcode-pa.googleapis.com/v1internal"
readonly TOKEN_CACHE="/tmp/.cortex_token_cache"

# ─── Defaults ───
MODEL="${CORTEX_MODEL:-gemini-2.0-flash}"
PROJECT="${CORTEX_PROJECT:-}"
MAX_TOKENS="${CORTEX_MAX_TOKENS:-8192}"
TEMPERATURE="${CORTEX_TEMPERATURE:-0.7}"
SYSTEM_INSTRUCTION=""
STREAM=false
THINK_BUDGET=""
RAW_REQUEST=""
SHOW_INFO=false
SHOW_QUOTA=false
SHOW_USAGE=false
VERBOSE=false

# ─── Functions ───

die() { echo "❌ $*" >&2; exit 1; }

usage() {
    sed -n '3,16p' "$0" | sed 's/^# *//'
    exit 0
}

# Token refresh (キャッシュ付き — 有効期限内なら再利用)
get_token() {
    # キャッシュが55分以内なら再利用
    if [[ -f "$TOKEN_CACHE" ]]; then
        local age=$(( $(date +%s) - $(stat -c %Y "$TOKEN_CACHE" 2>/dev/null || echo 0) ))
        if (( age < 3300 )); then
            cat "$TOKEN_CACHE"
            return
        fi
    fi

    [[ -f "$CREDS_FILE" ]] || die "OAuth 認証が必要です。先に: npx @google/gemini-cli --prompt 'hello'"

    local refresh_token
    refresh_token=$(python3 -c "import json; print(json.load(open('$CREDS_FILE'))['refresh_token'])" 2>/dev/null) \
        || die "refresh_token の読み取りに失敗"

    local response
    response=$(curl -s -X POST "https://oauth2.googleapis.com/token" \
        -d "client_id=$CLIENT_ID" \
        -d "client_secret=$CLIENT_SECRET" \
        -d "refresh_token=$refresh_token" \
        -d "grant_type=refresh_token") || die "Token refresh 失敗"

    local token
    token=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null) \
        || die "access_token の解析に失敗: $response"

    echo "$token" > "$TOKEN_CACHE"
    chmod 600 "$TOKEN_CACHE"
    echo "$token"
}

# プロジェクト ID 取得 (loadCodeAssist)
get_project() {
    local token="$1"

    if [[ -n "$PROJECT" ]]; then
        echo "$PROJECT"
        return
    fi

    local response
    response=$(curl -s -X POST \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        "$BASE_URL:loadCodeAssist" \
        -d '{"metadata":{"ideType":"IDE_UNSPECIFIED","platform":"PLATFORM_UNSPECIFIED","pluginType":"GEMINI"}}') \
        || die "loadCodeAssist 失敗"

    local project
    project=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin)['cloudaicompanionProject'])" 2>/dev/null) \
        || die "プロジェクト ID の解析に失敗: $response"

    echo "$project"
}

# generateContent 実行
generate() {
    local token="$1" project="$2" prompt="$3"
    local endpoint="$BASE_URL:generateContent"
    local curl_opts=(-s)

    if $STREAM; then
        endpoint="$BASE_URL:streamGenerateContent?alt=sse"
        curl_opts=(-sN)  # -N: no buffer for streaming
    fi

    # リクエスト構築 (環境変数でPythonに安全に渡す)
    local request_json
    request_json=$(CORTEX_PROMPT="$prompt" \
        CORTEX_SI="$SYSTEM_INSTRUCTION" \
        CORTEX_TB="$THINK_BUDGET" \
        CORTEX_RAW="$RAW_REQUEST" \
        CORTEX_M="$MODEL" \
        CORTEX_P="$project" \
        CORTEX_T="$TEMPERATURE" \
        CORTEX_N="$MAX_TOKENS" \
        python3 << 'PYEOF'
import json, os

prompt = os.environ.get("CORTEX_PROMPT", "")
si = os.environ.get("CORTEX_SI", "")
tb = os.environ.get("CORTEX_TB", "")
raw = os.environ.get("CORTEX_RAW", "")
model = os.environ.get("CORTEX_M", "gemini-2.0-flash")
project = os.environ.get("CORTEX_P", "")
temp = float(os.environ.get("CORTEX_T", "0.7"))
max_tok = int(os.environ.get("CORTEX_N", "8192"))

if raw:
    req = json.loads(raw)
else:
    req = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temp,
            "maxOutputTokens": max_tok
        }
    }
    if si:
        req["systemInstruction"] = {
            "role": "user",
            "parts": [{"text": si}]
        }
    if tb:
        req["generationConfig"]["thinkingConfig"] = {
            "thinkingBudget": int(tb)
        }

payload = {"model": model, "project": project, "request": req}
print(json.dumps(payload, ensure_ascii=False))
PYEOF
    ) || die "リクエスト構築失敗"

    $VERBOSE && echo "📡 $endpoint" >&2
    $VERBOSE && echo "📦 $(echo "$request_json" | python3 -m json.tool 2>/dev/null || echo "$request_json")" >&2

    local response
    response=$(curl "${curl_opts[@]}" -X POST \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        "$endpoint" \
        -d "$request_json") || die "API 呼び出し失敗"

    # 出力
    if $STREAM; then
        # SSE: data: 行からテキストを抽出
        echo "$response" | python3 -c "
import sys, json
for line in sys.stdin:
    line = line.strip()
    if line.startswith('data: '):
        try:
            d = json.loads(line[6:])
            parts = d.get('response',{}).get('candidates',[{}])[0].get('content',{}).get('parts',[])
            for p in parts:
                if 'text' in p:
                    print(p['text'], end='')
        except: pass
print()
" 2>/dev/null
    else
        echo "$response" | CORTEX_SHOW_USAGE="$SHOW_USAGE" python3 -c "
import sys, json, os
show_usage = os.environ.get('CORTEX_SHOW_USAGE', 'false') == 'true'
try:
    d = json.load(sys.stdin)
except json.JSONDecodeError:
    print(sys.stdin.read(), file=sys.stderr)
    sys.exit(1)
r = d.get('response', d)
# error check
if 'error' in d:
    print(f\"❌ API Error: {json.dumps(d['error'], indent=2)}\", file=sys.stderr)
    sys.exit(1)
# text output
for c in r.get('candidates', []):
    for p in c.get('content', {}).get('parts', []):
        if 'text' in p:
            print(p['text'])
# usage
if show_usage:
    u = r.get('usageMetadata', {})
    if u:
        print(f'---')
        print(f\"📊 tokens: {u.get('promptTokenCount','?')} in → {u.get('candidatesTokenCount','?')} out = {u.get('totalTokenCount','?')} total\")
        print(f\"📍 model: {r.get('modelVersion','?')}\")
" 2>/dev/null || echo "$response"
    fi
}

# ─── Parse Arguments ───
while [[ $# -gt 0 ]]; do
    case "$1" in
        -m|--model)     MODEL="$2"; shift 2 ;;
        -s|--system)    SYSTEM_INSTRUCTION="$2"; shift 2 ;;
        -t|--temp)      TEMPERATURE="$2"; shift 2 ;;
        -n|--max-tokens) MAX_TOKENS="$2"; shift 2 ;;
        --stream)       STREAM=true; shift ;;
        --think)        THINK_BUDGET="$2"; shift 2 ;;
        --raw)          RAW_REQUEST="$2"; shift 2 ;;
        --info)         SHOW_INFO=true; shift ;;
        --quota)        SHOW_QUOTA=true; shift ;;
        --usage)        SHOW_USAGE=true; shift ;;
        --verbose|-v)   VERBOSE=true; shift ;;
        -h|--help)      usage ;;
        --)             shift; break ;;
        -*)             die "Unknown option: $1" ;;
        *)              break ;;
    esac
done

PROMPT="${*:-}"

# ─── Main ───

# Token 取得
TOKEN=$(get_token)

# --info モード
if $SHOW_INFO; then
    echo "📡 loadCodeAssist..."
    curl -s -X POST \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        "$BASE_URL:loadCodeAssist" \
        -d '{"metadata":{"ideType":"IDE_UNSPECIFIED","platform":"PLATFORM_UNSPECIFIED","pluginType":"GEMINI"}}' \
        | python3 -m json.tool
    exit 0
fi

# --quota モード
if $SHOW_QUOTA; then
    PROJ=$(get_project "$TOKEN")
    echo "📡 retrieveUserQuota (project: $PROJ)..."
    curl -s -X POST \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        "$BASE_URL:retrieveUserQuota" \
        -d "{\"project\":\"$PROJ\"}" \
        | python3 -m json.tool
    exit 0
fi

# プロンプト必須チェック
[[ -z "$PROMPT" && -z "$RAW_REQUEST" ]] && die "プロンプトを指定してください。例: cortex.sh \"Hello\""

# プロジェクト取得
PROJ=$(get_project "$TOKEN")
$VERBOSE && echo "🏗️  project: $PROJ" >&2
$VERBOSE && echo "🤖 model: $MODEL" >&2

# 生成
generate "$TOKEN" "$PROJ" "$PROMPT"
