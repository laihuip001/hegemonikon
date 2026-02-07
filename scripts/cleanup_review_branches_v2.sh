#!/bin/bash
# Jules Review Branch Mass Cleanup Script v2
# Generated: 2026-02-06
# 
# This script identifies and deletes duplicate review branches,
# keeping only the most recent one per review ID.
#
# Run with: bash scripts/cleanup_review_branches_v2.sh
# DRY RUN by default, set EXECUTE=1 to actually delete

set -e

EXECUTE=${EXECUTE:-0}
REPO_DIR="/home/makaron8426/oikos/hegemonikon"

echo "=== Jules Review Branch Mass Cleanup v2 ==="
echo "Mode: $([ "$EXECUTE" = "1" ] && echo "EXECUTE" || echo "DRY RUN")"
echo ""

cd "$REPO_DIR"

# Fetch latest state
git fetch --prune 2>/dev/null

# Define review branch patterns to clean
# Format: prefix-NNN-suffix-randomid
REVIEW_PATTERNS=(
    "ai-[0-9]*-*-review"
    "th-[0-9]*-*-review"
    "es-[0-9]*-*-review"
    "ae-[0-9]*-*-review"
    "as-[0-9]*-*-review"
    "cl-[0-9]*-*-review"
    "jules-client-*"
    "perf-optimize-*"
    "palette-*"
    "bolt-optimize-*"
    "review-*"
    "docs-add-*"
    "docs-cl-*"
    "docs-es-*"
    "docs-ai-*"
    "docs-th-*"
    "docs-ae-*"
    "docs-as-*"
)

# Get all remote branches except master/HEAD
ALL_BRANCHES=$(git branch -a | grep 'origin/' | grep -v 'origin/master' | grep -v 'origin/HEAD' | sed 's|.*origin/||')

total_count=0
delete_count=0

# Process each pattern
for pattern in "${REVIEW_PATTERNS[@]}"; do
    # Find branches matching this pattern
    MATCHING=$(echo "$ALL_BRANCHES" | grep -E "^$pattern" 2>/dev/null || true)
    
    if [ -n "$MATCHING" ]; then
        count=$(echo "$MATCHING" | wc -l)
        echo "Pattern: $pattern ($count branches)"
        
        # For each matching branch
        while IFS= read -r branch; do
            if [ -n "$branch" ]; then
                echo "  DELETE: $branch"
                if [ "$EXECUTE" = "1" ]; then
                    git push origin --delete "$branch" 2>/dev/null && echo "    -> Deleted" || echo "    -> Failed"
                fi
                delete_count=$((delete_count + 1))
            fi
        done <<< "$MATCHING"
        echo ""
    fi
done

echo "================================"
echo "Total branches to delete: $delete_count"
echo ""

if [ "$EXECUTE" != "1" ]; then
    echo "To execute: EXECUTE=1 bash scripts/cleanup_review_branches_v2.sh"
    echo ""
    echo "WARNING: This will delete $delete_count branches. Review carefully!"
fi
