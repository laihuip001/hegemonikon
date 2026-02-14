# HGK Desktop App — 開発計画

> /dev プロトコル準拠、アジャイル Sprint 構成
> 更新: 2026-02-09

---

## 設計原則 (/dev)

| Protocol | 適用 |
|:---|:---|
| **TDD** (Module 04) | 各 Sprint で API テスト先行 |
| **Complexity Budget** (Module 06) | 1 Sprint = 1 機能、同時に 2 つ以上やらない |
| **Narrative Commit** (Module 14) | 意図を語るコミット |

---

## 開発サイクル

```
┌──────────────┐     ┌──────────────┐
│  Claude (BE) │←───→│  Gemini (FE) │
│  API + 3D    │     │  UI + Style  │
│  prototype   │     │  integration │
└──────┬───────┘     └──────┬───────┘
       │                    │
       └────── Review ──────┘
         (Claude /dia+)
```

**各 Sprint**: Claude が Backend + 3D プロトタイプ → Gemini が UI 統合 → Claude が `/dia+` レビュー

---

## Sprint 0: 足場 (Scaffold)

**ゴール**: グラフデータ API + Tauri UDS bridge

### Claude (Backend)

| タスク | 詳細 |
|:---|:---|
| `GET /api/graph/nodes` | 24 定理ノード (id, series, name, coordinates, type) |
| `GET /api/graph/edges` | 78 エッジ (72 X-series + 6 identity) |
| `GET /api/graph/meta` | Trígōnon メタデータ (Pure/Mixed, Anchor/Bridge) |
| テスト | 3 エンドポイント × 構造検証 |

**データソース**: `kernel/taxis.md` + `kernel/trigonon.md` をパースして JSON 化

### Gemini (Frontend)

| タスク | 詳細 |
|:---|:---|
| Tauri Rust bridge | UDS HTTP クライアント (`/tmp/hgk.sock`) |
| `invoke()` 型定義 | OpenAPI → TypeScript types |
| Tauri commands | 各 API エンドポイントに対応する Rust command |

### 完了基準

- `curl --unix-socket /tmp/hgk.sock http://localhost/api/graph/nodes` → 24 nodes
- `npm run tauri dev` → Tauri 起動、invoke で API 応答

---

## Sprint 1: 3D 定理グラフ 🌐

**ゴール**: 96 要素が 3D 空間で回せる

### Claude (3D Prototype)

| タスク | 詳細 |
|:---|:---|
| Three.js scene | カメラ、ライト、OrbitControls |
| Force-directed layout | d3-force-3d で 24 ノード配置 |
| ノード描画 | Series 別ネオンカラー球体 + ラベル |
| エッジ描画 | 方向付き矢印、Anchor/Bridge で太さ分け |
| GPU シェーダー | ネオングロー (RTX 2070 Super) |
| アニメーション | ノードホバーで発光、エッジ上の信号伝播 |

### Gemini (UI Integration)

| タスク | 詳細 |
|:---|:---|
| レイアウト | 3D canvas + サイドパネル (ノード詳細) |
| サイドパネル | クリックしたノードの定理情報、接続先一覧 |
| CSS | サイバーパンクテーマ全体適用 |
| フィルタ | Series (O/S/H/P/K/A) ON/OFF トグル |

### 完了基準

- 24 ノードが 3D 空間で回転・ズーム可能
- ノードクリックで詳細表示
- 60fps 維持 (GPU レンダリング)

---

## Sprint 2: FEP + Gnōsis 🧠📚

**ゴール**: 認知可視化 + 知識検索

### Claude (Backend)

| タスク | 詳細 |
|:---|:---|
| `GET /api/fep/beliefs/labeled` | 48 次元に名前 + 説明を付与 |
| Gnōsis search 修正 | shape mismatch 解消 or フォールバック |

### Claude (3D)

| タスク | 詳細 |
|:---|:---|
| Beliefs radar chart | 48 次元を円形 or 3D 球面 |
| FEP step アニメーション | step 実行 → 3D グラフのアクティブ定理が発光 |

### Gemini (UI)

| タスク | 詳細 |
|:---|:---|
| FEP ビュー | Beliefs 表示 + step ボタン + epsilon テーブル |
| Gnōsis ビュー | 検索バー + カード + source フィルタ |
| ナビゲーション | グラフ/FEP/Gnōsis/n8n のタブ or サイドバー |

---

## Sprint 3: n8n Heartbeat + 統合 💓

**ゴール**: Sympatheia モニタリング + 全機能統合

### Claude (Backend)

| タスク | 詳細 |
|:---|:---|
| `GET /api/n8n/heartbeat` | n8n API proxy (executions, status) |
| `GET /api/n8n/workflows` | 稼働中 WF 一覧 |

### Gemini (UI)

| タスク | 詳細 |
|:---|:---|
| Heartbeat ビュー | 脈拍アニメーション + WF リスト |
| ダッシュボード | 全機能のサマリーを 1 画面に |

---

## Sprint 4: ポリッシュ + GPU 最適化 ✨

**ゴール**: 恥ずかしくない品質

| タスク | 担当 | 詳細 |
|:---|:---|:---|
| WebGL シェーダー最適化 | Claude | GPU compute for particle effects |
| マイクロアニメーション | Gemini | ページ遷移、ホバー、ローディング |
| レスポンシブ | Gemini | ウィンドウリサイズ対応 |
| パフォーマンス | Claude | 60fps プロファイリング |
| Tauri ビルド | Gemini | `npm run tauri build` → .deb / AppImage |

---

## F5 (WF 起動) — 凍結

> Creator 判断: 「0 OR 100。クリップボードなら要らない。」
> IDE 連携が技術的に確立するまで凍結。Phase 2 以降で再検討。

---

## 分業原則

| 領域 | 担当 | なぜ |
|:---|:---|:---|
| **3D コア** (Three.js, シェーダー) | **Claude** | 難易度高、数学的構造の理解が必要 |
| **Backend API** | **Claude** | mekhane 内部構造を知っている |
| **UI/CSS** | **Gemini** | ビジュアルデザイン、大量の CSS |
| **Tauri Rust** | **Gemini** | Rust bridge は定型パターン |
| **レビュー** | **Claude /dia+** | 各 Sprint 後に品質検証 |

---

*Plan v1.0 — /dev (2026-02-09)*
