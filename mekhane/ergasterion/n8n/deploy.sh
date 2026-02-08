#!/bin/bash
# PROOF: [L2/インフラ] <- mekhane/ergasterion/n8n/ A0→自動化ツール群の管理が必要→deploy.shが担う
#
# n8n Workflow Deploy Helper
# Usage:
#   ./deploy.sh                     # 全 WF をインポート + publish + restart
#   ./deploy.sh wf05_health_alert   # 特定 WF のみ
#   ./deploy.sh --status            # ステータス確認
#   ./deploy.sh --test              # 全 webhook テスト

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTAINER="hegemonikon-n8n"
N8N_DIR="/oikos/hegemonikon/mekhane/ergasterion/n8n"
DB_PATH="$SCRIPT_DIR/data/database.sqlite"

# カラー
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✅ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
err()  { echo -e "${RED}❌ $1${NC}"; }

status() {
    echo "=== n8n Container ==="
    sudo docker ps --filter "name=$CONTAINER" --format "{{.Names}} {{.Status}}" 2>/dev/null || err "Docker unavailable"
    echo ""
    echo "=== Workflows ==="
    sudo docker exec "$CONTAINER" n8n list:workflow 2>&1 || err "n8n CLI failed"
}

test_webhooks() {
    echo "=== Testing Webhooks ==="
    local pass=0 fail=0

    echo -n "WF-02 bye-handoff: "
    R=$(curl -s -X POST http://localhost:5678/webhook/bye-handoff -H 'Content-Type: application/json' -d '{"subject":"deploy-test"}' 2>&1)
    if echo "$R" | grep -q "slack\|skipped"; then ok "OK"; ((pass++)) || true; else err "FAIL: $R"; ((fail++)) || true; fi

    echo -n "WF-05 health (HIGH): "
    R=$(curl -s -X POST http://localhost:5678/webhook/health-alert -H 'Content-Type: application/json' -d '{"items":[{"name":"X","status":"error"}],"score":0.4}' 2>&1)
    if echo "$R" | grep -q "HIGH"; then ok "severity=HIGH"; ((pass++)) || true; else err "FAIL: $R"; ((fail++)) || true; fi

    echo -n "WF-05 health (LOW): "
    R=$(curl -s -X POST http://localhost:5678/webhook/health-alert -H 'Content-Type: application/json' -d '{"items":[{"name":"X","status":"ok"}],"score":1.0}' 2>&1)
    if echo "$R" | grep -q "LOW"; then ok "severity=LOW"; ((pass++)) || true; else err "FAIL: $R"; ((fail++)) || true; fi

    echo -n "WF-06 session-start: "
    R=$(curl -s -X POST http://localhost:5678/webhook/session-start -H 'Content-Type: application/json' -d '{"mode":"test","agent":"deploy.sh"}' 2>&1)
    if echo "$R" | grep -q "active"; then ok "session active"; ((pass++)) || true; else err "FAIL: $R"; ((fail++)) || true; fi

    echo -n "WF-06 session-end: "
    R=$(curl -s -X POST http://localhost:5678/webhook/session-end -H 'Content-Type: application/json' -d '{"subject":"deploy-test"}' 2>&1)
    if echo "$R" | grep -q "ended"; then ok "session ended"; ((pass++)) || true; else err "FAIL: $R"; ((fail++)) || true; fi

    echo ""
    echo "Results: ${pass} passed, ${fail} failed"
    return "${fail}"
}

# 重複WF削除: 同名のWFが複数存在する場合、最新以外を削除
deduplicate_workflows() {
    echo "=== Checking for duplicates ==="
    # n8n list:workflow → ID|Name の一覧を取得
    local wf_list
    wf_list=$(sudo docker exec "$CONTAINER" n8n list:workflow 2>&1) || return

    # 名前でグループ化し、重複があれば古い方を DB から削除
    local names
    names=$(echo "$wf_list" | cut -d'|' -f2 | sort | uniq -d)

    if [ -z "$names" ]; then
        ok "No duplicates found"
        return
    fi

    echo "$names" | while IFS= read -r name; do
        [ -z "$name" ] && continue
        # 同名WFのIDを全て取得（最新=最後を残す）
        local ids
        ids=$(echo "$wf_list" | grep "$name" | cut -d'|' -f1)
        local keep_id
        keep_id=$(echo "$ids" | tail -1)
        echo "  Duplicate: $name (keeping $keep_id)"
        echo "$ids" | head -n -1 | while read -r old_id; do
            [ -z "$old_id" ] && continue
            python3 -c "
import sqlite3
conn = sqlite3.connect('$DB_PATH')
cur = conn.cursor()
cur.execute('DELETE FROM workflow_entity WHERE id = ?', ('$old_id',))
try:
    cur.execute('DELETE FROM webhook_entity WHERE \"workflowId\" = ?', ('$old_id',))
except: pass
conn.commit()
conn.close()
print('    Removed: $old_id')
"
        done
    done
}

deploy_workflow() {
    local json_file="$1"
    local basename=$(basename "$json_file" .json)

    echo "Deploying: $basename"

    # Import
    sudo docker exec "$CONTAINER" n8n import:workflow --input="${N8N_DIR}/${basename}.json" 2>&1 | grep -v "^$"

    # Get new ID (最新のもの)
    local new_id
    new_id=$(sudo docker exec "$CONTAINER" n8n list:workflow 2>&1 | grep -i "WF-" | grep "$(echo "$basename" | grep -oP 'wf\d+' | sed 's/wf/WF-/')" | tail -1 | cut -d'|' -f1)

    if [ -n "$new_id" ]; then
        sudo docker exec "$CONTAINER" n8n publish:workflow --id="$new_id" 2>&1 | grep -v "^$"
        ok "Published: $new_id"
    else
        warn "Could not find workflow ID for $basename"
    fi
}

deploy_all() {
    echo "=== Stopping n8n ==="
    cd "$SCRIPT_DIR" && sudo docker compose stop
    sleep 2

    echo "=== Deduplicating ==="
    deduplicate_workflows

    echo "=== Starting n8n ==="
    cd "$SCRIPT_DIR" && sudo docker compose up -d
    sleep 8

    echo "=== Deploying all workflows ==="
    for json in "$SCRIPT_DIR"/*.json; do
        [ -f "$json" ] || continue
        [[ "$json" == *docker-compose* ]] && continue
        deploy_workflow "$(basename "$json" .json)"
    done

    echo ""
    echo "=== Deduplicating after import ==="
    deduplicate_workflows

    echo ""
    echo "=== Restarting n8n ==="
    cd "$SCRIPT_DIR" && sudo docker compose restart
    sleep 8
    ok "n8n restarted"
}

# Main
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
    all)
        deploy_all
        ;;
    *)
        deploy_workflow "$1"
        echo "Restarting n8n..."
        cd "$SCRIPT_DIR" && sudo docker compose restart
        sleep 8
        ok "Done"
        ;;
esac
