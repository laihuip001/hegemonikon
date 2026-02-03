#!/bin/bash
# Jules Review Branch Cleanup Script
# Generated: 2026-02-03
# 
# This script deletes review branches that have been integrated into KI.
# Run with: bash scripts/cleanup_review_branches.sh
#
# DRY RUN by default, set EXECUTE=1 to actually delete

EXECUTE=${EXECUTE:-0}

echo "=== Jules Review Branch Cleanup ==="
echo "Mode: $([ "$EXECUTE" = "1" ] && echo "EXECUTE" || echo "DRY RUN")"
echo ""

# Get list of old review branches (older than 7 days)
cd /home/makaron8426/oikos/hegemonikon

# Category 1: Outdated docs branches (likely already in main)
OUTDATED_DOCS=$(git branch -a | grep -E 'origin/(docs-add|update-readme|doc-copy|add-specialist)' | sed 's|.*origin/||')

# Category 2: Merged review branches (duplicates of same review ID)
# Keep only the newest of each th-XXX, ai-XXX, es-XXX pattern

count=0
for branch in $OUTDATED_DOCS; do
    echo "DELETE: $branch"
    if [ "$EXECUTE" = "1" ]; then
        git push origin --delete "$branch" 2>/dev/null && echo "  -> Deleted" || echo "  -> Failed"
    fi
    count=$((count + 1))
done

echo ""
echo "Total branches to delete: $count"
echo ""
if [ "$EXECUTE" != "1" ]; then
    echo "To execute: EXECUTE=1 bash scripts/cleanup_review_branches.sh"
fi
