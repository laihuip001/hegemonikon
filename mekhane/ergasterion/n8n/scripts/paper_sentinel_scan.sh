#!/bin/bash
# paper_sentinel_scan.sh — Gnosis から論文候補を収集してJSONに書き出す
# WF-14 (n8n) がこのJSONを読んで Cortex で要約生成する
# Usage: crontab で 6時間毎に実行: 0 */6 * * * /path/to/paper_sentinel_scan.sh

set -euo pipefail

REPO_DIR="$HOME/oikos/hegemonikon"
OUTPUT="$HOME/oikos/mneme/.hegemonikon/paper_sentinel_raw.json"
TOPICS_FILE="$REPO_DIR/mekhane/ergasterion/n8n/scripts/sentinel_topics.txt"
VENV="$REPO_DIR/.venv/bin/python"
MAX_PER_TOPIC=3

export PYTHONPATH="$REPO_DIR"
cd "$REPO_DIR" || exit 1

# Default topics if file doesn't exist
if [ ! -f "$TOPICS_FILE" ]; then
    echo "active inference" > "$TOPICS_FILE"
    echo "free energy principle" >> "$TOPICS_FILE"
    echo "cognitive architecture" >> "$TOPICS_FILE"
fi

# Collect papers using Gnosis CLI for each topic
$VENV << 'PYTHON_SCRIPT'
import json, os, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

repo = os.environ.get("REPO_DIR", os.path.expanduser("~/oikos/hegemonikon"))
topics_file = os.path.join(repo, "mekhane/ergasterion/n8n/scripts/sentinel_topics.txt")
output_path = os.environ.get("OUTPUT", os.path.expanduser("~/oikos/mneme/.hegemonikon/paper_sentinel_raw.json"))
venv_python = os.path.join(repo, ".venv/bin/python")
max_per = 3

papers = []
topics = []

with open(topics_file) as f:
    topics = [l.strip() for l in f if l.strip() and not l.startswith('#')]

for topic in topics:
    try:
        result = subprocess.run(
            [venv_python, "mekhane/anamnesis/cli.py", "search", topic, "--limit", str(max_per)],
            capture_output=True, text=True, timeout=60, cwd=repo,
            env={**os.environ, "PYTHONPATH": repo}
        )
        if result.returncode == 0:
            current = {}
            for line in result.stdout.split('\n'):
                title_m = re.match(r'\[\d+\]\s+(.*)', line)
                if title_m:
                    if current.get('title'):
                        papers.append(current)
                    current = {'title': title_m.group(1).strip(), 'topic': topic, 'score': 0.5, 'source': 'gnosis'}
                elif line.strip().startswith('Source:'):
                    current['source'] = line.split(':', 1)[1].strip().split('|')[0].strip()
                elif line.strip().startswith('Authors:'):
                    current['authors'] = [a.strip() for a in line.split(':', 1)[1].strip().split(',')]
                elif line.strip().startswith('Abstract:'):
                    current['abstract'] = line.split(':', 1)[1].strip()[:500]
            if current.get('title'):
                papers.append(current)
    except Exception as e:
        papers.append({'error': str(e), 'topic': topic})

# Deduplicate by title
seen = set()
unique = []
for p in papers:
    title = p.get('title', '')
    if title not in seen:
        seen.add(title)
        unique.append(p)

output = {
    'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'topics': topics,
    'total_papers': len(unique),
    'papers': sorted(unique, key=lambda x: x.get('score', 0), reverse=True),
}

Path(output_path).parent.mkdir(parents=True, exist_ok=True)
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f'[paper_sentinel_scan] {datetime.now()} — {len(unique)} papers, wrote {output_path}')
PYTHON_SCRIPT
