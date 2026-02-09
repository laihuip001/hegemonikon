# Sprint 1: Three.js 3D グラフ — Jules タスク設計書

> **dispatch**: Jules に投入するためのタスク仕様書
> **repo**: `laihuip001/hegemonikon`
> **作業ディレクトリ**: `hgk-desktop/src/`

---

## 目標

`hgk-desktop/src/views/graph3d.ts` を新規作成し、Hegemonikón の 24 定理 + 72 X-series エッジを
Three.js で 3D 力学シミュレーション付きインタラクティブグラフとして描画する。

> **注**: API は 96 エッジ (72 X-series + 24 identity) を返すが、identity エッジは非表示にする。

## 既存コード構造（参照必須）

```
hgk-desktop/
├── src/
│   ├── main.ts          # ルーター + 5 ビュー (492行)
│   ├── styles.css        # デザインシステム (285行)
│   ├── api/client.ts     # API クライアント (60行)
│   └── views/            # ← ここに graph3d.ts を追加
├── index.html            # <div id="app"> + nav + main
└── package.json          # Vite + TypeScript
```

## API エンドポイント（バックエンド実装済み）

```
GET /api/graph/nodes → GraphNode[]
GET /api/graph/edges → GraphEdge[]
GET /api/graph/full  → { nodes, edges, meta }
```

### GraphNode 型

```typescript
interface GraphNode {
  id: string;        // "O1", "S2", "H3", etc.
  series: string;    // "O", "S", "H", "P", "K", "A"
  name: string;      // "Noēsis", "Mekhanē", etc.
  greek: string;     // "νόησις"
  meaning: string;   // "深い認識"
  workflow: string;  // "/noēsis" (フルギリシャ名、CLI略称ではない)
  type: string;      // "Pure" or "Mixed"
  color: string;     // "#00d4ff" (neon colors)
  position: { x: number; y: number; z: number };
}
```

### GraphEdge 型

```typescript
interface GraphEdge {
  id: string;              // "X-OS1"
  pair: string;            // "X-OS"
  source: string;          // "O1"
  target: string;          // "S1"
  shared_coordinate: string; // "Flow", "Scale", "Valence", "identity"
  naturality: string;      // "experiential" | "reflective" | "structural" | "identity"
  meaning: string;         // "本質→様態"
  type: string;            // "anchor" | "bridge" | "identity"
}
```

### Series カラーパレット（ネオンサイバーパンク）

```typescript
const SERIES_COLORS: Record<string, string> = {
  O: "#00d4ff",  // シアンブルー — Ousia (本質)
  S: "#10b981",  // エメラルド — Schema (様態)
  H: "#ef4444",  // レッド — Hormē (傾向)
  P: "#a855f7",  // パープル — Perigraphē (境界)
  K: "#f59e0b",  // アンバー — Kairos (文脈)
  A: "#f97316",  // オレンジ — Akribeia (精密)
};
```

## 実装要件

### 1. パッケージ追加

```bash
cd hgk-desktop && npm install three @types/three
```

> `three-forcegraph` が npm 上に存在しない場合は、Three.js の `Object3D` + `d3-force-3d` で同等の力学シミュレーションを実装すること。
> その場合: `npm install d3-force-3d`

### 2. `src/views/graph3d.ts` 新規作成

```typescript
// 必須 export
export async function renderGraph3D(): Promise<void>
```

- `api.graphFull()` でデータ取得
- Three.js + 力学シミュレーション (d3-force-3d or 独自実装) でレンダリング
- `#view-content` 内に Three.js canvas を挿入
- **ビュー切替時のクリーンアップ**: `renderGraph3D` が返す前に、前回の canvas/renderer を `dispose()` する cleanup 関数を登録すること

```typescript
// cleanup パターン例
let cleanup: (() => void) | null = null;

export async function renderGraph3D(): Promise<void> {
  if (cleanup) cleanup();  // 前回の Three.js リソースを解放
  // ... Three.js 初期化
  cleanup = () => { renderer.dispose(); /* ... */ };
}
```

### 3. ビジュアル要件（サイバーパンク）

| 要素 | 仕様 |
|:---|:---|
| **背景** | 漆黒 `#0a0a0f`、微小パーティクルフィールド |
| **ノード** | 光り輝く球体 (MeshPhongMaterial + emissive)、Series カラーに準拠 |
| **ノードラベル** | 白テキスト (CSS2DRenderer)、ホバー時に greek 名と meaning を表示 |
| **エッジ** | 半透明のグロー付き線 (naturality で色分け: experiential=cyan, reflective=gold, structural=silver) |
| **Identity エッジ** | 非表示 (type === "identity" はスキップ) |
| **Pure ノード** | やや大きい (radius=8)、三角形の頂点位置 |
| **Mixed ノード** | 小さめ (radius=5)、辺の中点 |
| **Series グループ** | 同じ Series の 4 ノードは近くに配置 (初期位置は API の position を使用) |
| **アニメーション** | ノードに微小な pulse アニメーション (emissive intensity の sin 変動) |
| **カメラ** | OrbitControls でマウスドラッグ回転/ズーム、初期位置は斜め上から |

### 4. インタラクション

| 操作 | 動作 |
|:---|:---|
| **マウスホバー** | ノード拡大 + tooltip (name, greek, meaning, workflow) |
| **クリック** | 選択状態 → サイドパネルに詳細表示 (接続エッジ一覧) |
| **右クリック** | なし (将来用) |
| **ズーム** | マウスホイール |
| **回転** | 左ドラッグ |
| **パン** | 右ドラッグ |

### 5. `main.ts` への統合

```typescript
// routes に追加
import { renderGraph3D } from './views/graph3d';

const routes: Record<string, ViewRenderer> = {
  'graph': renderGraph3D,  // ← 追加
  'dashboard': renderDashboard,
  // ...
};
```

### 6. `index.html` に nav ボタン追加

```html
<button data-route="graph">🔮 Graph</button>
```

### 7. `api/client.ts` に graph API 追加

```typescript
// 型定義
interface GraphFullResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  meta: {
    total_nodes: number;
    total_edges: number;
    series: Record<string, { name: string; color: string; theorems: number }>;
    trigonon: { vertices: string[]; description: string };
    naturality: Record<string, string>;
  };
}

// Graph
graphNodes: () => apiFetch<GraphNode[]>('/api/graph/nodes'),
graphEdges: () => apiFetch<GraphEdge[]>('/api/graph/edges'),
graphFull: () => apiFetch<GraphFullResponse>('/api/graph/full'),
```

### 8. CSS 追加 (`styles.css`)

```css
/* Three.js container */
#graph-container {
  width: 100%;
  height: calc(100vh - 4rem);
  position: relative;
}

/* Node tooltip */
.node-tooltip {
  position: absolute;
  background: rgba(13, 17, 23, 0.95);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 0.75rem;
  color: var(--text-color);
  font-size: 0.85rem;
  pointer-events: none;
  backdrop-filter: blur(8px);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.15);
}
```

## 禁止事項

- ❌ `styles.css` のルート変数 (`:root`) を変更しない
- ❌ 既存の 5 ビュー (dashboard/fep/gnosis/quality/postcheck) を変更しない
- ❌ `api/client.ts` の既存エクスポートを変更しない（追加のみ）

## テスト

```bash
cd hgk-desktop && npm run build  # TypeScript コンパイルが通ること
```

---

*この仕様書で Jules に dispatch する*
