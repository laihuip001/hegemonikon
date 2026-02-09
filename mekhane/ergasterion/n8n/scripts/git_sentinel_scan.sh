#!/bin/bash
# git_sentinel_scan.sh — ホスト側でgit statusを取得してJSONに書き出す
# WF-13 (n8n) がこのJSONを読んで処理する
# Usage: crontab で 30分毎に実行: */30 * * * * /path/to/git_sentinel_scan.sh

REPO_DIR="$HOME/oikos/hegemonikon"
OUTPUT="$HOME/oikos/mneme/.hegemonikon/git_status_raw.json"

cd "$REPO_DIR" || exit 1

# git情報収集
STATUS=$(git status --porcelain 2>&1)
BRANCH=$(git branch --show-current 2>&1)
LOG=$(git log --oneline -3 2>&1)
STASH_COUNT=$(git stash list 2>&1 | wc -l)
DIFF_STAT=$(git diff --stat 2>&1)

# JSON生成 (jq不要)
python3 -c "
import json, sys
data = {
    'timestamp': '$(date -u +%Y-%m-%dT%H:%M:%SZ)',
    'branch': '''$BRANCH'''.strip(),
    'status_lines': [l for l in '''$STATUS'''.strip().split('\n') if l.strip()],
    'recent_commits': [l for l in '''$LOG'''.strip().split('\n') if l.strip()],
    'stash_count': int('$STASH_COUNT'),
    'diff_stat': '''$DIFF_STAT'''.strip()
}
json.dump(data, sys.stdout, indent=2, ensure_ascii=False)
" > "$OUTPUT"

echo "[git_sentinel_scan] $(date) — wrote $OUTPUT"
