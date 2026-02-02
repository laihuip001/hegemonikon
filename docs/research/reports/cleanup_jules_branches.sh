#!/bin/bash
# Jules Review Branches Cleanup Script
# Generated: 2026-01-29
# Purpose: Delete review branches after /fit verification
#
# USAGE:
#   1. Review this list and uncomment branches to delete
#   2. Run: bash cleanup_jules_branches.sh
#
# SAFETY: All branches are prefixed with 'origin/' for remote deletion

cd /home/makaron8426/oikos/hegemonikon || exit 1

echo "🧹 Jules Review Branches Cleanup"
echo "================================="
echo ""

# Count total branches
TOTAL=$(git branch -a | grep -E "(jules|review)" | wc -l)
echo "📊 Total review branches: $TOTAL"
echo ""

# DRY RUN - List what would be deleted
echo "⚠️  DRY RUN MODE - No branches will be deleted"
echo ""
echo "Branches matching pattern 'jules|review':"
git branch -a | grep -E "(jules|review)" | head -20
echo "... and $((TOTAL - 20)) more"
echo ""

# UNCOMMENT TO ACTUALLY DELETE
# =============================
# WARNING: This will permanently delete remote branches!
#
# To delete all jules/review branches:
# git branch -a | grep 'remotes/origin/' | grep -E "(jules|review)" | \
#   sed 's|remotes/origin/||' | \
#   xargs -I {} git push origin --delete {}

echo ""
echo "To proceed with deletion:"
echo "1. Review branches carefully"
echo "2. Edit this script to uncomment the deletion commands"
echo "3. Run again"
