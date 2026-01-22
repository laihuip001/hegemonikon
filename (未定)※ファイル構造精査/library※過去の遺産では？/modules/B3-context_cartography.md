---
id: B-3
trigger: manual
---

# B-3: Context Cartography (文脈地図)

## Objective

スレッド開始から現在までの全議論を俯瞰し、構造・決定事項・未解決課題をマッピングする。

## Processing

1. **Segmentation:** 議論を論理的フェーズに分割 (発散→収束→修正)
2. **Extraction:** 各フェーズの決定事項と保留事項を抽出
3. **Vector Analysis:** 当初目的と現在地を比較し、ドリフトを検出

## Output Template

```markdown
## 📑 エグゼクティブ・サマリー
(議論の要点と現在地を3行で要約)

---

## 🗺️ 議論の地図

### 🚩 Origin & Vector
- **当初の目的:** [スレッド開始時のゴール]
- **現在の焦点:** [今のテーマ]
- **Drift Check:** [整合 / 乖離（要修正）]

### 📍 Phase History
- **Phase 1:** [フェーズ名]
  - Key Decision: ...
  - Pivot: ...

### 📦 The Backlog
- Pending Question: [未回答の問い]
- Technical Debt: [後回しにした課題]

---

## 🔗 構造的可視化
(Mermaid graph TD または mindmap で図解)
```
