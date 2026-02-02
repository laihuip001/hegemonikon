---
id: hegemonikon-ki
name: Hegemonikón Knowledge Item
version: v1.0
description: |
  Use this skill when you need to understand the Hegemonikón framework structure,
  theorem architecture (O/S/H/P/K/A series), or workflow-skill relationships.
  Triggers: /boot, フレームワーク, 定理, 24定理, τ-layer, v2.1, v2.2
triggers:
  explicit:
    - /hgk-ki
  keywords:
    - hegemonikon
    - 定理
    - スキル
    - ワークフロー
    - 24定理
    - τ-layer
    - v2.1
    - v2.2
---

# Hegemonikón Knowledge Item Skill

> **目的**: KI「Hegemonikón Integrated System」の内容をスキルとして発動可能にする

## いつ使うか

- セッション開始時（`/boot` 時）
- 定理・スキル・ワークフロー構造を問われた時
- 「Hegemonikón とは何か」を説明する必要がある時
- v2.1/v2.2 アーキテクチャの確認が必要な時

## 参照すべきアーティファクト

```
/home/laihuip001/oikos/.gemini/antigravity/knowledge/hegemonikon_system/
├── metadata.json
└── artifacts/
    ├── overview.md
    ├── core/canonical_theorems_v2_1.md
    ├── workflows/detailed_protocols.md
    └── ...
```

## クイックリファレンス

### 定理体系 (24)

| Series | Name | Theorems |
|--------|------|----------|
| Ousia (O) | 純粋定理 | O1-O4 |
| Schema (S) | 戦略定理 | S1-S4 |
| Hormē (H) | 衝動定理 | H1-H4 |
| Perigraphē (P) | 環境定理 | P1-P4 |
| Kairos (K) | 文脈定理 | K1-K4 |
| Akribeia (A) | 精度定理 | A1-A4 |

### ワークフロー階層

| 層 | 例 | 用途 |
|----|-----|------|
| **Ω (Omega)** | `/boot`, `/bye` | セッションライフサイクル |
| **Δ (Delta)** | `/vet`, `/plan` | 設計・品質保証 |
| **τ (Tau)** | `/bou`, `/k` | 微細な意志・文脈操作 |

---

*このスキルは KI「Hegemonikón Integrated System」から自動生成された*
