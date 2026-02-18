#!/bin/bash
# PURPOSE: Kill ghost IDE terminal processes (bash via shellIntegration) older than 4 hours
# PROOF: [L2/インフラ] <- scripts/ A0→安定した環境が必要→ゴースト掃除が担う
#
# Usage:
#   bash scripts/cleanup_ghost_terminals.sh          # dry-run (default)
#   bash scripts/cleanup_ghost_terminals.sh --kill   # actually kill
#
# Cron (recommended):
#   0 * * * * /home/makaron8426/oikos/hegemonikon/scripts/cleanup_ghost_terminals.sh --kill >> /tmp/ghost_cleanup.log 2>&1

set -euo pipefail

MAX_AGE_HOURS=4
KILL_MODE=false

if [[ "${1:-}" == "--kill" ]]; then
    KILL_MODE=true
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Ghost terminal cleanup (kill=$KILL_MODE)"

# Find bash processes started by shellIntegration-bash.sh
ghost_count=0
while IFS= read -r line; do
    pid=$(echo "$line" | awk '{print $1}')
    etime=$(echo "$line" | awk '{print $2}')

    # Parse elapsed time (format: [[DD-]HH:]MM:SS)
    hours=0
    if [[ "$etime" =~ ^([0-9]+)-([0-9]+): ]]; then
        days="${BASH_REMATCH[1]}"
        hours=$(( 10#$days * 24 + 10#${BASH_REMATCH[2]} ))
    elif [[ "$etime" =~ ^([0-9]+):([0-9]+):([0-9]+)$ ]]; then
        hours=$((10#${BASH_REMATCH[1]}))
    fi

    if (( hours >= MAX_AGE_HOURS )); then
        ghost_count=$((ghost_count + 1))
        echo "  Ghost: PID=$pid, elapsed=$etime"
        if $KILL_MODE; then
            kill -9 "$pid" 2>/dev/null && echo "    → killed (SIGKILL)" || echo "    → already dead"
        fi
    fi
done < <(ps -eo pid,etime,cmd | grep 'shellIntegration-bash.sh' | grep -v grep | awk '{print $1, $2}')

echo "  Total ghosts found: $ghost_count (age > ${MAX_AGE_HOURS}h)"
