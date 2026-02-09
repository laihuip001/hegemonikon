#!/bin/bash
# PROOF: [L2/インフラ] <- mekhane/ergasterion/n8n/ A0→自動化ツール群の管理が必要→deploy.shが担う
#
# n8n Workflow Deploy Helper (Local Process Edition)
#
# n8n がローカルプロセスとして稼働する環境に対応。
# JSON → SQLite 直接インポート + プロセス再起動。
#
# Usage:
#   ./deploy.sh                     # 全 WF をインポート + restart
#   ./deploy.sh wf05_health_alert   # 特定 WF のみ
#   ./deploy.sh --status            # ステータス確認
#   ./deploy.sh --test              # 全 webhook テスト
#   ./deploy.sh --no-restart        # インポートのみ (再起動しない)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_PATH="$SCRIPT_DIR/data/database.sqlite"
N8N_PORT="${N8N_PORT:-5678}"
N8N_HOST="${N8N_HOST:-localhost}"
N8N_URL="http://${N8N_HOST}:${N8N_PORT}"

# カラー
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✅ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
err()  { echo -e "${RED}❌ $1${NC}"; }
info() { echo -e "${CYAN}ℹ️  $1${NC}"; }

# ── n8n プロセス管理 ──────────────────────────────────

find_n8n_pid() {
    pgrep -f "node.*n8n" | head -1
}

is_n8n_running() {
    local pid
    pid=$(find_n8n_pid)
    [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null
}

restart_n8n() {
    local pid
    pid=$(find_n8n_pid)

    if [ -n "$pid" ]; then
        info "Stopping n8n (PID: $pid)..."
        kill "$pid" 2>/dev/null
        sleep 3

        # 確実に停止を確認
        if kill -0 "$pid" 2>/dev/null; then
            warn "Force killing n8n..."
            kill -9 "$pid" 2>/dev/null
            sleep 2
        fi
    fi

    info "Starting n8n..."
    N8N_HOST="$N8N_HOST" N8N_PORT="$N8N_PORT" N8N_PROTOCOL=http \
        nohup node /usr/local/bin/n8n start > /tmp/n8n_deploy_restart.log 2>&1 &

    # 起動待ち
    local retries=0
    while [ $retries -lt 15 ]; do
        if curl -s "${N8N_URL}/healthz" >/dev/null 2>&1 || \
           curl -s "${N8N_URL}/signin" >/dev/null 2>&1; then
            ok "n8n started (PID: $(find_n8n_pid))"
            return 0
        fi
        sleep 1
        ((retries++))
    done

    err "n8n failed to start within 15s"
    return 1
}

# ── SQLite ワークフロー操作 ──────────────────────────

deploy_workflow() {
    local json_file="$1"
    local basename=$(basename "$json_file" .json)
    local filepath="$SCRIPT_DIR/${basename}.json"

    if [ ! -f "$filepath" ]; then
        err "File not found: $filepath"
        return 1
    fi

    info "Deploying: $basename"

    python3 -c "
import sqlite3, json, sys

DB = '$DB_PATH'
WF_FILE = '$filepath'

with open(WF_FILE) as f:
    wf = json.load(f)

name = wf.get('name', '$basename')
nodes = json.dumps(wf['nodes'])
connections = json.dumps(wf['connections'])
settings = json.dumps(wf.get('settings', {}))
import uuid
# versionId は必ず UUID を生成 (JSON の値は無視)
version_id = str(uuid.uuid4())
active = 1 if wf.get('active', True) else 0
tags = json.dumps(wf.get('tags', []))

conn = sqlite3.connect(DB)
cur = conn.cursor()

# 既存 WF を名前で検索
cur.execute('SELECT id FROM workflow_entity WHERE name = ?', (name,))
existing = cur.fetchone()

if existing:
    wf_id = existing[0]
    cur.execute('''
        UPDATE workflow_entity
        SET nodes = ?, connections = ?, settings = ?, \"versionId\" = ?,
            active = ?, \"updatedAt\" = datetime('now')
        WHERE id = ?
    ''', (nodes, connections, settings, version_id, active, wf_id))
    print(f'  Updated: {name} (ID: {wf_id})')
else:
    # 新規作成 — ID は n8n 形式のランダム文字列
    import string, random
    wf_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    cur.execute('''
        INSERT INTO workflow_entity (id, name, nodes, connections, settings, \"versionId\", active, \"createdAt\", \"updatedAt\")
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    ''', (wf_id, name, nodes, connections, settings, version_id, active))
    print(f'  Created: {name} (ID: {wf_id})')

# workflow_history にも登録 (publish と同等)
cur.execute('''
    INSERT OR REPLACE INTO workflow_history (workflowId, versionId, nodes, connections, name, authors, \"createdAt\", \"updatedAt\")
    VALUES (?, ?, ?, ?, ?, 'deploy.sh', datetime('now'), datetime('now'))
''', (wf_id, version_id, nodes, connections, name))

# webhook_entity にも登録 (webhook ノードを自動検出)
for node in wf['nodes']:
    if node.get('type', '') in ('n8n-nodes-base.webhook',):
        wh_path = node.get('parameters', {}).get('path', '')
        wh_method = node.get('parameters', {}).get('httpMethod', 'POST')
        wh_id = node.get('webhookId', '')
        node_name = node.get('name', '')
        if wh_path:
            # 既存 webhook を削除して再登録
            cur.execute('DELETE FROM webhook_entity WHERE "workflowId" = ? AND "webhookPath" = ?', (wf_id, wh_path))
            cur.execute('''
                INSERT INTO webhook_entity ("workflowId", "webhookPath", method, node, "webhookId", "pathLength")
                VALUES (?, ?, ?, ?, ?, 1)
            ''', (wf_id, wh_path, wh_method, node_name, wh_id or wh_path))
            print(f'  Webhook: {wh_method} /{wh_path}')

# shared_workflow が無ければ追加 (プロジェクト関連付け)
cur.execute('SELECT COUNT(*) FROM shared_workflow WHERE \"workflowId\" = ?', (wf_id,))
if cur.fetchone()[0] == 0:
    cur.execute('SELECT role, \"projectId\" FROM shared_workflow LIMIT 1')
    ref = cur.fetchone()
    if ref:
        cur.execute('''
            INSERT INTO shared_workflow (role, \"workflowId\", \"projectId\", \"createdAt\", \"updatedAt\")
            VALUES (?, ?, ?, datetime('now'), datetime('now'))
        ''', (ref[0], wf_id, ref[1]))

conn.commit()
conn.close()
" 2>&1

    if [ $? -eq 0 ]; then
        ok "$basename deployed"
    else
        err "$basename failed"
        return 1
    fi
}

# ── ステータス確認 ────────────────────────────────────

status() {
    echo "=== n8n Process ==="
    local pid
    pid=$(find_n8n_pid)
    if [ -n "$pid" ]; then
        ok "Running (PID: $pid)"
        ps -o pid,etime,rss,%cpu -p "$pid" 2>/dev/null | tail -1 | awk '{printf "  Uptime: %s | RSS: %s KB | CPU: %s%%\n", $2, $3, $4}'
    else
        err "Not running"
    fi

    echo ""
    echo "=== Workflows in DB ==="
    python3 -c "
import sqlite3
conn = sqlite3.connect('$DB_PATH')
cur = conn.cursor()
cur.execute('SELECT id, name, active FROM workflow_entity ORDER BY name')
for row in cur.fetchall():
    status = '🟢' if row[2] else '⚪'
    print(f'  {status} {row[1]} (ID: {row[0]})')
conn.close()
" 2>&1

    echo ""
    echo "=== Health Check ==="
    if curl -s "${N8N_URL}/healthz" >/dev/null 2>&1; then
        ok "HTTP OK"
    elif curl -s "${N8N_URL}/signin" >/dev/null 2>&1; then
        ok "HTTP OK (signin redirect)"
    else
        err "HTTP unreachable"
    fi
}

# ── Webhook テスト ────────────────────────────────────

test_webhooks() {
    echo "=== Testing Webhooks ==="
    local pass=0 fail=0

    echo -n "WF-02 bye-handoff: "
    R=$(curl -s -X POST "${N8N_URL}/webhook/bye-handoff" -H 'Content-Type: application/json' -d '{"subject":"deploy-test"}' 2>&1)
    if echo "$R" | grep -q "slack\|skipped\|success"; then ok "OK"; ((pass++)) || true; else err "FAIL: $R"; ((fail++)) || true; fi

    echo -n "WF-05 health (HIGH): "
    R=$(curl -s -X POST "${N8N_URL}/webhook/health-alert" -H 'Content-Type: application/json' -d '{"items":[{"name":"X","status":"error"}],"score":0.4}' 2>&1)
    if echo "$R" | grep -q "HIGH"; then ok "severity=HIGH"; ((pass++)) || true; else err "FAIL: $R"; ((fail++)) || true; fi

    echo -n "WF-05 health (LOW): "
    R=$(curl -s -X POST "${N8N_URL}/webhook/health-alert" -H 'Content-Type: application/json' -d '{"items":[{"name":"X","status":"ok"}],"score":1.0}' 2>&1)
    if echo "$R" | grep -q "LOW"; then ok "severity=LOW"; ((pass++)) || true; else err "FAIL: $R"; ((fail++)) || true; fi

    echo -n "WF-06 session-start: "
    R=$(curl -s -X POST "${N8N_URL}/webhook/session-start" -H 'Content-Type: application/json' -d '{"mode":"test","agent":"deploy.sh"}' 2>&1)
    if echo "$R" | grep -q "active"; then ok "session active"; ((pass++)) || true; else err "FAIL: $R"; ((fail++)) || true; fi

    echo -n "WF-06 session-end: "
    R=$(curl -s -X POST "${N8N_URL}/webhook/session-end" -H 'Content-Type: application/json' -d '{"subject":"deploy-test"}' 2>&1)
    if echo "$R" | grep -q "ended"; then ok "session ended"; ((pass++)) || true; else err "FAIL: $R"; ((fail++)) || true; fi

    echo -n "WF-03 heartbeat: "
    R=$(curl -s -X POST "${N8N_URL}/webhook/heartbeat" -H 'Content-Type: application/json' -d '{}' 2>&1)
    if echo "$R" | grep -q "heartbeat\|timestamp\|ok"; then ok "OK"; ((pass++)) || true; else warn "SKIP: $R"; fi

    echo ""
    echo "Results: ${pass} passed, ${fail} failed"
    return "${fail}"
}

# ── 重複削除 ──────────────────────────────────────────

deduplicate_workflows() {
    echo "=== Checking for duplicates ==="
    python3 -c "
import sqlite3
conn = sqlite3.connect('$DB_PATH')
cur = conn.cursor()

# 同名WFをグループ化
cur.execute('''
    SELECT name, GROUP_CONCAT(id), COUNT(*)
    FROM workflow_entity
    GROUP BY name
    HAVING COUNT(*) > 1
''')

dups = cur.fetchall()
if not dups:
    print('  No duplicates found ✅')
    conn.close()
    exit(0)

for name, ids_str, count in dups:
    ids = ids_str.split(',')
    keep = ids[-1]  # 最新を保持
    remove = ids[:-1]
    print(f'  Duplicate: {name} ({count} copies, keeping {keep})')
    for old_id in remove:
        cur.execute('DELETE FROM workflow_entity WHERE id = ?', (old_id,))
        try:
            cur.execute('DELETE FROM webhook_entity WHERE \"workflowId\" = ?', (old_id,))
        except: pass
        print(f'    Removed: {old_id}')

conn.commit()
conn.close()
" 2>&1
}

# ── デプロイ全体 ──────────────────────────────────────

deploy_all() {
    local should_restart=true
    [ "${1:-}" = "--no-restart" ] && should_restart=false

    echo "=== Deploying all workflows ==="

    local count=0
    for json in "$SCRIPT_DIR"/*.json; do
        [ -f "$json" ] || continue
        [[ "$json" == *docker-compose* ]] && continue
        deploy_workflow "$(basename "$json" .json)"
        ((count++))
    done

    echo ""
    ok "Deployed $count workflows"

    echo ""
    deduplicate_workflows

    if $should_restart; then
        echo ""
        restart_n8n
    else
        info "Skipping restart (--no-restart)"
    fi
}

# ── Main ──────────────────────────────────────────────

case "${1:-all}" in
    --status)
        status
        ;;
    --test)
        test_webhooks
        ;;
    --dedup)
        deduplicate_workflows
        ;;
    --no-restart)
        deploy_all --no-restart
        ;;
    all)
        deploy_all
        ;;
    *)
        deploy_workflow "$1"
        echo ""
        restart_n8n
        ;;
esac
