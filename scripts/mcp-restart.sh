#!/usr/bin/env bash
# MCP サーバー一括再起動スクリプト (L2 保険)
#
# Usage:
#   ./scripts/mcp-restart.sh          # kill all MCP processes
#   ./scripts/mcp-restart.sh --status # show status only
#   ./scripts/mcp-restart.sh --dry-run # show what would be killed
#
# turbo-all
set -euo pipefail

MCP_PATTERN="mekhane/mcp/.*_server\.py|scripts/hermeneus_mcp\.py|mekhane\.mcp\.hgk_gateway"
PID_DIR="$HOME/.cache/hgk/mcp"

_color() { printf "\033[%sm%s\033[0m" "$1" "$2"; }
_green() { _color "32" "$1"; }
_red()   { _color "31" "$1"; }
_yellow(){ _color "33" "$1"; }

status() {
    echo "=== MCP プロセス状況 ==="
    local count=0
    while IFS= read -r line; do
        count=$((count + 1))
        local pid=$(echo "$line" | awk '{print $1}')
        local rss=$(echo "$line" | awk '{print $2}')
        local cmd=$(echo "$line" | cut -d' ' -f3-)
        local mb=$((rss / 1024))
        # サーバー名を抽出
        local name=$(echo "$cmd" | grep -oP '[a-z_]+_server\.py|hermeneus_mcp\.py|hgk_gateway' | head -1)
        printf "  PID %-7s | %3d MB | %s\n" "$pid" "$mb" "${name:-unknown}"
    done < <(ps -eo pid,rss,args --sort=-rss | grep -P "$MCP_PATTERN" | grep -v grep)

    if [ $count -eq 0 ]; then
        echo "  $(_green '(なし)')"
    else
        local total_mb
        total_mb=$(ps -eo rss,args | grep -P "$MCP_PATTERN" | grep -v grep | awk '{sum+=$1} END {printf "%.0f", sum/1024}')
        echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "  合計: $count プロセス, ${total_mb} MB"
    fi

    # PID ファイル状況
    if [ -d "$PID_DIR" ]; then
        echo ""
        echo "=== PID ファイル ==="
        for f in "$PID_DIR"/*.pid; do
            [ -f "$f" ] || continue
            local name=$(basename "$f" .pid)
            local pid=$(cat "$f" 2>/dev/null || echo "")
            if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
                echo "  $(_green '✅') $name (PID $pid)"
            else
                echo "  $(_red '❌') $name (PID ${pid:-?} — dead)"
            fi
        done
    fi
}

kill_all() {
    local dry_run="${1:-false}"
    local pids
    pids=$(pgrep -f "$MCP_PATTERN" 2>/dev/null || true)

    if [ -z "$pids" ]; then
        echo "$(_green 'MCP プロセスなし。')"
        return
    fi

    local count=$(echo "$pids" | wc -l)
    echo "$(_yellow "SIGTERM → $count プロセス...")"

    if [ "$dry_run" = "true" ]; then
        echo "$(_yellow '[DRY RUN] 実際には kill しません')"
        ps -eo pid,rss,args --sort=-rss | grep -P "$MCP_PATTERN" | grep -v grep
        return
    fi

    # SIGTERM
    echo "$pids" | xargs kill 2>/dev/null || true
    
    # 2秒待機
    sleep 2

    # 残存確認
    local remaining
    remaining=$(pgrep -f "$MCP_PATTERN" 2>/dev/null || true)
    if [ -n "$remaining" ]; then
        echo "$(_red "残存 $(echo "$remaining" | wc -l) プロセス → SIGKILL")"
        echo "$remaining" | xargs kill -9 2>/dev/null || true
        sleep 1
    fi

    # 最終確認
    remaining=$(pgrep -f "$MCP_PATTERN" 2>/dev/null || true)
    if [ -z "$remaining" ]; then
        echo "$(_green '✅ 全 MCP プロセスを停止')"
    else
        echo "$(_red '❌ 一部プロセスが残存')"
        echo "$remaining" | xargs ps -p 2>/dev/null
    fi

    # PID ファイル掃除
    if [ -d "$PID_DIR" ]; then
        rm -f "$PID_DIR"/*.pid 2>/dev/null
        echo "PID ファイルを削除"
    fi
}

case "${1:-kill}" in
    --status|-s) status ;;
    --dry-run|-n) kill_all true ;;
    --help|-h)
        echo "Usage: $0 [--status|--dry-run|--help]"
        echo "  (引数なし)    全 MCP プロセスを kill"
        echo "  --status      状況表示のみ"
        echo "  --dry-run     何が kill されるか表示"
        ;;
    *) kill_all false ;;
esac
