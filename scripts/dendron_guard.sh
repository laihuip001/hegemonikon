#!/bin/bash
# PURPOSE: Dendron 定時スキャン — アンチウイルスの「フルスキャン」
# REASON: 手動チェックでは見落とす PROOF/PURPOSE の劣化を自動検出するため
#
# Usage:
#   ./scripts/dendron_guard.sh              # hegemonikon のみ (日次)
#   ./scripts/dendron_guard.sh --full       # oikos 全体 (週次 "雑草刈り")
#
# crontab 例:
#   # 毎日 AM3:00 — hegemonikon のみ
#   0 3 * * * /home/makaron8426/oikos/hegemonikon/scripts/dendron_guard.sh
#   # 毎週日曜 AM4:00 — oikos 全体 (雑草刈り)
#   0 4 * * 0 /home/makaron8426/oikos/hegemonikon/scripts/dendron_guard.sh --full

set -euo pipefail

OIKOS_ROOT="$HOME/oikos"
HGK_ROOT="$OIKOS_ROOT/hegemonikon"
REPORT_DIR="$OIKOS_ROOT/mneme/.hegemonikon/dendron"
DATE=$(date +%Y%m%d)
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Ensure report directory exists
mkdir -p "$REPORT_DIR"

# Activate venv
export PYTHONPATH="$HGK_ROOT"

run_check() {
    local target="$1"
    local label="$2"
    local report_file="$REPORT_DIR/${label}_${DATE}.json"

    echo "[$TIMESTAMP] 🔍 Dendron scan: $target ($label)"

    cd "$HGK_ROOT"
    .venv/bin/python -m mekhane.dendron check "$target" --ci --format json \
        > "$report_file" 2>&1 || true

    echo "[$TIMESTAMP] 📄 Report: $report_file"
}

if [ "${1:-}" = "--full" ]; then
    # 雑草刈り: oikos 全体をスキャン
    echo "=== 🌿 Dendron Weekly Full Scan (雑草刈り) ==="
    echo ""

    # oikos 配下のプロジェクトを走査
    for project_dir in "$OIKOS_ROOT"/*/; do
        project_name=$(basename "$project_dir")

        # .git がないディレクトリはスキップ
        if [ ! -d "$project_dir/.git" ] && [ ! -d "$project_dir/mekhane" ]; then
            # PROOF.md があるプロジェクトのみチェック
            if ! find "$project_dir" -name "PROOF.md" -maxdepth 3 -quit 2>/dev/null | grep -q .; then
                continue
            fi
        fi

        run_check "$project_dir" "weekly_${project_name}"
    done

    echo ""
    echo "=== 🌿 Weekly scan complete ==="
else
    # 日次: hegemonikon のみ
    echo "=== 🛡️ Dendron Daily Scan ==="
    run_check "$HGK_ROOT" "daily"
    echo "=== 🛡️ Daily scan complete ==="
fi

# Cleanup: 30日より古いレポートを削除
find "$REPORT_DIR" -name "*.json" -mtime +30 -delete 2>/dev/null || true
