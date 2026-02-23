# HGK OS APP — UI 要件定義 v1.0

> **目的**: 他セッションでも参照できる永続的な要件ドキュメント
> **作成日**: 2026-02-19
> **MVP 定義**: AMBITION.md F4 (AI 指揮台) を MVP とする

---

## 1. 設計方針

| 項目 | 内容 |
|:-----|:-----|
| **デザイン参照** | claude.ai 70% (温かみ、丸み、余白) + manus.im 30% (ステータス、プログレス) |
| **適用範囲** | 色味と空気感。レイアウト構造の模倣はしない |
| **既存活用** | 既存の `hgk/` アプリを拡張。新規プロジェクトではない |

---

## 2. レイアウト構成

### 2.1 全体レイアウト (Creator 指定)

```
┌──────┬─────────┬──────────────────────────┬────────────────────┐
│ アイ  │ 縦タブ   │                          │ スライドアウト      │
│ コン  │ (アイ   │    メインコンテンツ        │ パネル(右端)       │
│ バー  │ コン+   │    (選択されたView)       │ ・ターミナル        │
│ (左端)│ タイトル)│                          │ ・アーティファクト   │
│      │         │                          │                    │
└──────┴─────────┴──────────────────────────┴────────────────────┘
```

### 2.2 左端: アイコンバー (Creator 要件)

- 各機能アイコンを縦に並べる (ダッシュボード、チャット等)
- クリックで対応する機能画面を表示
- **参照**: claude.ai のサイドバーと同じ構造

### 2.3 左ペイン: 縦タブ (Creator 要件)

- アイコンバーの右隣に配置
- **アイコン＋タイトル**でタブを表示
- クリックで中央コンテンツを切り替え

### 2.4 右端: スライドアウトパネル (Creator 要件)

- **OPPO PAD のOS機能に類似**
- 通常は非表示 (端に薄い線のみ)
- マウスホバーで線の透明度が低下 (視覚フィードバック)
- クリックでパネルがスライドイン
- コンテンツ: ターミナル出力、アーティファクトの内容
- 再クリックでスライドアウト (閉じる)

---

## 3. Orchestrator View (F4 MVP) — 実装済み

### 3.1 3ペイン構成

- **左**: ファイルツリー (読み取り専用、クリックで内容表示)
- **中央**: AI チャット (Ochema ask_with_tools、モデルセレクタ4種)
- **右**: Changes (git status/diff) + Terminal ログ

### 3.2 機能一覧

| 機能 | API | 状態 |
|:-----|:----|:-----|
| ファイルツリー表示 | `GET /api/files/list` | ✅ 実装済み |
| ファイル内容表示 | `GET /api/files/read` | ✅ 実装済み |
| AI チャット | `POST /api/ochema/ask_with_tools` | ✅ 実装済み |
| Git 変更一覧 | `GET /api/git/status` | ✅ 実装済み |
| Git Diff 表示 | `GET /api/git/diff` | ✅ 実装済み |
| ターミナル実行 | `POST /api/terminal/execute` | ✅ 実装済み |
| モデル選択 | フロントエンドのみ | ✅ 実装済み |
| ウェルカムスクリーン | — | ✅ 実装済み |
| ステータスバー | — | ✅ 実装済み |
| SSE ストリーミング | `/api/chat/send` | ✅ 実装済み (Phase 4) |

---

## 4. 未実装 (Phase 2)

| # | 機能 | 詳細 |
|:--|:-----|:-----|
| U1 | 左端アイコンバー | 全機能のアイコンナビ (§2.2) |
| U2 | 縦タブ | アイコン+タイトルの縦タブ (§2.3) |
| U3 | 右端スライドアウト | OPPO PAD 風、ホバーで透明度変化 (§2.4) |
| U4 | タブシステム | Ctrl+T/W でタブ管理 |
| U6 | Diff 承認/却下 | 変更の approve/reject ボタン |

---

## 5. 技術スタック

| 項目 | 技術 |
|:-----|:-----|
| Desktop Shell | Tauri v2 (Rust) |
| Frontend | Vite + TypeScript (Vanilla) |
| Backend API | FastAPI (port 9696, UDS /tmp/hgk.sock) |
| 3D | Three.js + d3-force-3d |
| IPC | Tauri invoke → Rust → UDS HTTP → FastAPI |

---

## 6. ファイル構成

| ファイル | 役割 |
|:---------|:-----|
| `hgk/src/views/orchestrator.ts` | Orchestrator View 本体 |
| `hgk/src/views/orchestrator.css` | Orchestrator スタイル |
| `hgk/src/route-config.ts` | ルート定義 (Orchestrator 追加済み) |
| `hgk/src/api/client.ts` | API クライアント (Orchestrator 用型+メソッド追加) |
| `mekhane/api/routes/devtools.py` | バックエンド API (files, git, terminal, ochema) |

---

*Created: 2026-02-19 — HGK OS APP MVP v1.0*

Last synced: 2026-02-23
