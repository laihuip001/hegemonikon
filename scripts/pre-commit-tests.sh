#!/usr/bin/env bash
# PROOF: [L2/CI] <- mekhane/ A0→テスト自動化→pre-commit hookが担う
# PURPOSE: Git commit 前に統合テスト + Kalon テストを実行
# USAGE: .git/hooks/pre-commit から呼び出される / 手動: bash scripts/pre-commit-tests.sh
#         --no-verify で commit 時にスキップ可能 (Git 標準)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_DIR}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔬 Hegemonikón Pre-commit Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Integration tests + Kalon tests + Peira tests
PYTHONPATH=. .venv/bin/python -m pytest \
    mekhane/tests/ \
    mekhane/peira/tests/ \
    --ignore=mekhane/tests/test_guardian_integration.py \
    -x -q --timeout=60 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ All tests passed. Committing."
else
    echo ""
    echo "❌ Tests failed. Commit blocked."
    echo "   Use 'git commit --no-verify' to skip."
fi

exit $EXIT_CODE
