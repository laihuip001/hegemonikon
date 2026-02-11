#!/usr/bin/env bash
# sync_claude_context.sh — HGK コンテキストを claude.ai 用 Sync フォルダに同期
#
# 同期対象:
#   ✅ .agent/workflows/  (全量)
#   ✅ .agent/rules/      (全量)
#   ✅ .agent/skills/     (全量)
#   ✅ kernel/            (全量、.md + .png)
#   ✅ KI (Knowledge Items)
#   ✅ hermeneus/docs/    (CCL ドキュメント)
#   ✅ README.md, AGENTS.md, projects.yaml
#
# 除外:
#   ❌ Python コード (.py)
#   ❌ 論文データ (mekhane/anamnesis/data/)
#   ❌ node_modules, __pycache__, .venv, .git
#   ❌ hgk-desktop/ (ビルド成果物)
#   ❌ synergeia/ (Jules 連携コード)
#
# Usage: bash scripts/sync_claude_context.sh [--dry-run]

set -euo pipefail

SRC="/home/makaron8426/oikos/hegemonikon"
DEST="/home/makaron8426/Sync/15_🏛️_ヘゲモニコン｜Hegemonikon"
KI_SRC="/home/makaron8426/.gemini/antigravity/knowledge"

DRY_RUN=""
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN="--dry-run"
    echo "🔍 DRY RUN mode"
fi

echo "═══════════════════════════════════════════"
echo "  HGK → Claude Sync"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "═══════════════════════════════════════════"

# --- 1. .agent/workflows/ (全量) ---
echo ""
echo "📋 [1/7] Workflows..."
rsync -av --delete $DRY_RUN \
    "$SRC/.agent/workflows/" \
    "$DEST/.agent/workflows/"

# --- 2. .agent/rules/ (全量) ---
echo ""
echo "📋 [2/7] Rules..."
rsync -av --delete $DRY_RUN \
    "$SRC/.agent/rules/" \
    "$DEST/.agent/rules/"

# --- 3. .agent/skills/ (全量) ---
echo ""
echo "📋 [3/7] Skills..."
rsync -av --delete $DRY_RUN \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    "$SRC/.agent/skills/" \
    "$DEST/.agent/skills/"

# --- 4. kernel/ (全量、コード除外) ---
echo ""
echo "📋 [4/7] Kernel..."
rsync -av --delete $DRY_RUN \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    "$SRC/kernel/" \
    "$DEST/kernel/"

# --- 5. KI (Knowledge Items) ---
echo ""
echo "📋 [5/7] Knowledge Items..."
if [[ -d "$KI_SRC" ]]; then
    mkdir -p "$DEST/knowledge_items"
    rsync -av --delete $DRY_RUN \
        --exclude='*.lock' \
        "$KI_SRC/" \
        "$DEST/knowledge_items/"
else
    echo "  ⚠️ KI directory not found: $KI_SRC"
fi

# --- 6. Hermēneus docs (CCL ドキュメント) ---
echo ""
echo "📋 [6/7] Hermēneus docs..."
if [[ -d "$SRC/hermeneus/docs" ]]; then
    mkdir -p "$DEST/hermeneus_docs"
    rsync -av --delete $DRY_RUN \
        "$SRC/hermeneus/docs/" \
        "$DEST/hermeneus_docs/"
fi

# --- 7. トップレベルファイル ---
echo ""
echo "📋 [7/7] Top-level files..."
for f in README.md AGENTS.md projects.yaml; do
    if [[ -f "$SRC/$f" ]]; then
        rsync -av $DRY_RUN "$SRC/$f" "$DEST/$f"
    fi
done

# --- Summary ---
echo ""
echo "═══════════════════════════════════════════"
if [[ -n "$DRY_RUN" ]]; then
    echo "  ✅ DRY RUN complete"
else
    echo "  ✅ Sync complete"
    # ファイル数
    WF_COUNT=$(find "$DEST/.agent/workflows" -name '*.md' 2>/dev/null | wc -l)
    RULES_COUNT=$(find "$DEST/.agent/rules" -name '*.md' 2>/dev/null | wc -l)
    SKILLS_COUNT=$(find "$DEST/.agent/skills" -name 'SKILL.md' 2>/dev/null | wc -l)
    KI_COUNT=$(find "$DEST/knowledge_items" -maxdepth 1 -type d 2>/dev/null | tail -n +2 | wc -l)
    TOTAL_SIZE=$(du -sh "$DEST" 2>/dev/null | cut -f1)
    
    echo "  Workflows: $WF_COUNT"
    echo "  Rules:     $RULES_COUNT"
    echo "  Skills:    $SKILLS_COUNT"
    echo "  KIs:       $KI_COUNT"
    echo "  Total:     $TOTAL_SIZE"
fi
echo "═══════════════════════════════════════════"
