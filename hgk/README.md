# Hegemonikón Desktop

認知ハイパーバイザーフレームワーク **Hegemonikón** の GUI フロントエンド。

## 技術スタック

| レイヤー | 技術 |
|:---------|:-----|
| Desktop Shell | Tauri v2 (Rust) |
| Frontend | Vite + TypeScript (Vanilla) |
| 3D Visualization | Three.js + d3-force-3d |
| Accessibility | AT-SPI2 (Rust, Linux) |
| Backend API | FastAPI (UDS: `/tmp/hgk.sock`) |

## 起動

```bash
# API バックエンド (別ターミナル)
cd ~/oikos/hegemonikon
PYTHONPATH=. .venv/bin/python -m mekhane.api.server --uds /tmp/hgk.sock

# Desktop アプリ
cd hgk
npm run tauri dev
```

## Views (17)

| View | ファイル | 概要 |
|:-----|:---------|:-----|
| Dashboard | `dashboard.ts` | メインダッシュボード (Quota, Digest, Status) |
| Chat | `chat.ts` | LLM チャット (Claude, Gemini, Cortex) |
| Graph 3D | `graph3d.ts` | Three.js 公理体系 3D ビジュアライゼーション |
| Search | `search.ts` | Gnōsis ベクトル検索 |
| Sophia | `sophia.ts` | Knowledge Item 管理 |
| Gnosis | `gnosis.ts` | 論文検索・管理 |
| FEP | `fep.ts` | FEP 状態空間ビジュアライゼーション |
| Timeline | `timeline.ts` | セッション履歴タイムライン |
| Notifications | `notifications.ts` | 通知パネル |
| Synteleia | `synteleia.ts` | 認知アンサンブル監査 |
| Synedrion | `synedrion.ts` | 偉人評議会 UI |
| PKS | `pks.ts` | Proactive Knowledge Surface |
| Desktop DOM | `desktop-dom.ts` | AT-SPI アクセシビリティツリー |
| Agent Manager | `agent-manager.ts` | エージェント管理 |
| Digestor | `digestor.ts` | 論文消化パイプライン |
| Quality | `quality.ts` | 品質ダッシュボード |
| Postcheck | `postcheck.ts` | ポストチェック |

## ディレクトリ構造

```
hgk/
├── src/                 # Frontend (TypeScript)
│   ├── main.ts          # ルーティング・ナビゲーション
│   ├── styles.css       # グローバルスタイル
│   ├── utils.ts         # 共有ユーティリティ
│   ├── api-types.ts     # API 型定義 (自動生成)
│   ├── command_palette.ts # コマンドパレット (Ctrl+K)
│   ├── telemetry.ts     # テレメトリ
│   └── views/           # 17 views
├── src-tauri/           # Backend (Rust)
│   ├── src/
│   │   ├── lib.rs       # Tauri コマンド定義
│   │   ├── main.rs      # エントリポイント
│   │   └── a11y/        # AT-SPI アクセシビリティ
│   └── tauri.conf.json
├── docs/                # 設計文書
└── index.html           # エントリ HTML
```

## 依存関係

- **mekhane/api/**: FastAPI バックエンド (UDS 経由)
- **mekhane/synteleia/**: Synteleia 監査エンジン
- **mekhane/anamnesis/**: Gnōsis ベクトル検索
