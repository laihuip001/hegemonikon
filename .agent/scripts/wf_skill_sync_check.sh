#!/bin/bash
# wf_skill_sync_check.sh
# WF derivatives と実装の同期を検証するスクリプト

cd /home/laihuip001/oikos/.agent/workflows

echo "=== WF Derivatives vs Implementation ==="
echo "| WF | frontmatter | 実装 | 状態 |"
echo "|:---|:-----------:|:----:|:----:|"

total_front=0
total_impl=0
desync_count=0

for wf in *.md; do
  base=$(basename "$wf" .md)
  
  # frontmatter の derivatives 数を取得
  front=$(head -40 "$wf" | grep "^derivatives:" | sed 's/derivatives: \[//' | sed 's/\]//' | tr ',' '\n' | sed 's/^ *//' | grep -v '^$' | wc -l)
  
  # ## --mode= セクション数を取得
  impl=$(grep -c "^## --mode=" "$wf" 2>/dev/null)
  impl=${impl:-0}
  
  if [ "$front" -gt 0 ]; then
    total_front=$((total_front + front))
    total_impl=$((total_impl + impl))
    
    if [ "$front" -eq "$impl" ]; then
      echo "| $base | $front | $impl | ✅ |"
    else
      diff=$((front - impl))
      echo "| $base | $front | $impl | ⚠️ ($diff) |"
      desync_count=$((desync_count + 1))
    fi
  fi
done

echo ""
echo "=== Summary ==="
echo "Total frontmatter: $total_front"
echo "Total implemented: $total_impl"
echo "Desync files: $desync_count"

if [ "$desync_count" -eq 0 ]; then
  echo "✅ All WFs are in sync!"
  exit 0
else
  echo "⚠️ $desync_count WFs have desync"
  exit 1
fi
