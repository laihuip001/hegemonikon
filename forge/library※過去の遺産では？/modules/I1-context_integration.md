---
id: I-1
trigger: manual
---

# I-1: Context Integration (外部文脈統合)

## Objective

別チャットの議論やWeb記事などを「パッチ」として現在の成果物に適用しアップデートする。

## Input

```xml
<external_context>
{{ここに別チャットの内容やテキストを貼り付け}}
</external_context>
```

## Processing

1. **Extraction:** 外部コンテキストから適用可能な新視点・制約・アイデアを抽出
2. **Gap Analysis:** 現成果物と比較し、矛盾点 (Correction) / 不足点 (Expansion) / 質的向上点 (Improvement) を特定
3. **Synthesis:** 既存構造を破壊せず整合性を保ちながら統合

## Output Template

```markdown
## 🧬 統合レポート
- **修正 (Correction):** [外部文脈に基づき修正した点]
- **拡張 (Expansion):** [新たに追加した要素]
- **改善 (Improvement):** [ブラッシュアップした点]

---

## 📄 Updated Artifact
(統合後の完全な成果物)
```
