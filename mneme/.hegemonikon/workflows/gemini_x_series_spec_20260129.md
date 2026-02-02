# X-series 可視化 追加実装指示書

> **対象エージェント**: Gemini (Antigravity IDE)
> **前提**: Hegemonikón Interactive Guide が完成している状態
> **目的**: X-series 36関係の可視化機能を追加

---

## 1. 概要

現在の Interactive Guide に **X-series 可視化ページ**を追加する。

ユーザーが Hub をクリックすると、その Hub から他の Hub への接続関係が視覚的に表示される。

---

## 2. 機能要件

### 2.1 X-series ページ

| 要件 | 詳細 |
|:-----|:-----|
| **ナビゲーション** | ホーム画面に「X-series」カードを追加 |
| **可視化** | 6 Hub を六角形または円形に配置 |
| **インタラクション** | Hub をクリックすると、そこからの接続線がハイライト |
| **推奨表示** | 選択した Hub から推奨される次の Hub を表示 |

### 2.2 データ構造

`data/x-series.json` を作成:

```json
{
  "relations": [
    {
      "id": "X-OS",
      "from": "O",
      "to": "S",
      "meaning": "認識 → 設計",
      "path": "O1 → S1",
      "priority": 1
    },
    {
      "id": "X-OA",
      "from": "O",
      "to": "A",
      "meaning": "認識 → 検証",
      "path": "O1 → A2",
      "priority": 2
    }
    // ... 36 relations total
  ]
}
```

---

## 3. UI デザイン

### 3.1 レイアウト

```
┌─────────────────────────────────────────────────────────────┐
│  ← Back              X-SERIES: 36 RELATIONS                 │
│                                                             │
│              ┌─────────────────────────┐                   │
│              │          [O]            │                   │
│              │       ↗     ↘           │                   │
│              │    [A]         [S]      │                   │
│              │     ↑    ✕    ↓         │                   │
│              │    [K]         [H]      │                   │
│              │       ↖     ↙           │                   │
│              │          [P]            │                   │
│              └─────────────────────────┘                   │
│                                                             │
│   現在地: [O]  →  推奨: S (設計), A (検証), K (時機)       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 CSS クラス

```css
.x-series-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.hub-node {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.hub-node:hover {
  transform: scale(1.1);
  box-shadow: var(--shadow-glow);
}

.hub-node.active {
  border: 2px solid var(--border-accent);
}

.connection-line {
  stroke: var(--text-secondary);
  stroke-width: 1;
  transition: stroke 0.3s ease, stroke-width 0.3s ease;
}

.connection-line.highlighted {
  stroke: var(--border-accent);
  stroke-width: 2;
}
```

### 3.3 SVG または Canvas

**推奨**: SVG を使用（DOM 操作が容易）

---

## 4. 実装手順

### Step 1: データ作成

`data/x-series.json` に 36 関係を定義。

既存データ参照: `/home/makaron8426/oikos/mneme/.hegemonikon/workflows/x_series_36_relations_guide_20260129.md`

### Step 2: X-series ページ作成

`views/x-series.js` または既存の `main.js` に追加:

```javascript
function renderXSeries() {
  // SVG で 6 Hub を円形に配置
  // 接続線を描画
  // クリックイベントでハイライト
}
```

### Step 3: ナビゲーション追加

ホーム画面に「X-series」カードを追加:

```javascript
{
  id: 'x-series',
  name: 'X-Series',
  description: '36 Relations',
  color: '#9333ea' // Purple
}
```

### Step 4: テスト

- Hub クリックで接続線がハイライトされるか
- 推奨 Hub が正しく表示されるか

---

## 5. 品質基準

| 基準 | 要件 |
|:-----|:-----|
| **視覚** | 既存デザインと一貫性 |
| **アニメーション** | 接続線のハイライトはスムーズ |
| **データ** | 36 関係すべてが正確 |
| **操作性** | 直感的なクリック操作 |

---

## 6. 参考資料

- [X-series 36関係ガイド](/home/makaron8426/oikos/mneme/.hegemonikon/workflows/x_series_36_relations_guide_20260129.md)
- [既存の Interactive Guide 実装](/home/makaron8426/oikos/hegemonikon-guide/)

---

*この指示書に従って X-series 可視化を追加してください。*
