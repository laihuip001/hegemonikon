# ワークフロー劣化再発防止ルール

> **作成日**: 2026-01-29
> **目的**: 1:1統一などのリファクタリング時に機能喪失を防ぐ

---

## 📊 劣化パターン分析

### 発見された劣化パターン

| パターン | 原因 | 例 |
|:---------|:-----|:---|
| **骨格化 (Skeletonization)** | 1:1分解時に機能を移植せず骨格のみ残す | `/sop` KI未反映 |
| **機能散逸 (Function Dispersion)** | 複数WFに分解時に一部機能が消失 | `/pri` → Eisenhower喪失 |
| **統合時圧縮 (Merge Compression)** | 統合時に詳細が簡略化される | `/plan` → `/s` Y-1/D-1喪失 |

### 根本原因

1. **「後で移植」の先送り** — 骨格を先に作り、中身を後で埋める予定が忘れられる
2. **分解時の棚卸し不足** — 旧WFの全機能をリストアップせずに分解
3. **lineage の形骸化** — lineage に「吸収元」を記録しても内容が移植されない

---

## 🛡️ 再発防止ルール

### ルール 1: 削除前棚卸し (Pre-Delete Inventory)

WF を削除または分解する前に、**全機能の棚卸し表**を作成。

```markdown
## 削除対象: /pri.md

| 機能 | 移植先 | 移植状況 |
|:-----|:-------|:---------|
| Eisenhower Matrix | /k.md | ❌ 未移植 |
| Q2 保護 | /k.md | ❌ 未移植 |
| Priority Score | /k.md | ❌ 未移植 |
| Urgency マッピング | /chr.md | ✅ 移植済 |

→ 全て ✅ になるまで削除禁止
```

### ルール 2: absorbed タグ必須 (Absorption Tracking)

機能を吸収した WF は frontmatter に `absorbed` タグを追加。

```yaml
absorbed:
  - "Eisenhower Matrix (from /pri.md)"
  - "Q2 保護 (from /pri.md)"
```

**検証**: absorbed に記載された機能が本文に存在するか確認。

### ルール 3: 品質指標チェック (Quality Gate)

新規・修正 WF は以下の品質指標を満たすこと:

| 指標 | 必須 | 推奨 |
|:-----|:----:|:----:|
| `skill_ref` | ✅ | — |
| `version` | ✅ | — |
| `lineage` | ✅ | — |
| `triggers` | — | ✅ |
| `anti_skip` | — | ✅ |
| `出力形式` セクション | — | ✅ |
| `Hegemonikon Status` テーブル | — | ✅ |

### ルール 4: Git pre-commit フック

`.git/hooks/pre-commit` に以下を追加:

```bash
#!/bin/bash
# Workflow Quality Check

for f in $(git diff --cached --name-only | grep "^.agent/workflows/.*\.md$"); do
    if ! grep -q "skill_ref:" "$f" && [[ "$f" != *"/u.md" ]]; then
        echo "❌ $f: skill_ref がありません"
        exit 1
    fi
    if ! grep -q "version:" "$f"; then
        echo "❌ $f: version がありません"
        exit 1
    fi
    if ! grep -q "lineage:" "$f"; then
        echo "❌ $f: lineage がありません"
        exit 1
    fi
done

echo "✅ ワークフロー品質チェック PASS"
```

---

## 📋 チェックリスト

### リファクタリング時

- [ ] 削除前棚卸し表を作成したか？
- [ ] 全機能の移植先を明記したか？
- [ ] 移植先に機能が実装されたことを確認したか？
- [ ] absorbed タグを追加したか？
- [ ] lineage に変更履歴を記録したか？

### 新規作成時

- [ ] skill_ref があるか？（/u 以外）
- [ ] version があるか？
- [ ] lineage があるか？
- [ ] 出力形式セクションがあるか？
- [ ] Hegemonikon Status テーブルがあるか？

---

## 📚 参照

- [ワークフロー劣化監査報告書](file:///home/makaron8426/oikos/.gemini/antigravity/brain/1291d231-b66b-45f4-9d3c-599a9b400955/implementation_plan.md)
- [深層監査報告書](file:///home/makaron8426/oikos/.gemini/antigravity/brain/1291d231-b66b-45f4-9d3c-599a9b400955/deep_workflow_audit.md)

---

*Workflow Degradation Prevention Rules v1.0*
*Generated: 2026-01-29*
