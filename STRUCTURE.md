# Hegemonikon 構造図 (STRUCTURE.md)

> **目的**: Hegemonikon の全体像を把握するための地図
> **更新トリガー**: ユーザー発言「設計思想として保存して」、またはAI提案による
> **参照元**: `/now map` (`/nm`), `/now ctx` (`/nc`)
> **AI向け**: [docs/STRUCTURE.md](docs/STRUCTURE.md) (English, AI-optimized)

---

## 🏗️ 3層アーキテクチャ

```
Hegemonikon
├── Core（コア層）       # OS相当。変更頻度低、安定性重視
├── Products（プロダクト層） # アプリケーション。独立して開発・置換可能
└── Data（データ層）     # 永続化データ。外部システムと連携
```

---

## 🧬 Core（コア層）

**役割**: Hegemonikon の根幹。理論基盤とAI制御。

### Kernel（理論基盤）
- Hegemonikón 理論（FEP、変分自由エネルギー）
- 公理・選択公理
- パス: `kernel/`

### Agent（AI制御層）
- **Workflows**: `/now`, `/plan`, `/code` 等のコマンド
- **Skills**: M1-M8, P1-P4 スキル
- **Rules**: 制約・プロトコル
- パス: `.agent/`

---

## 📦 Products（プロダクト層）

**役割**: 独立したツール・アプリケーション。置換・拡張可能。

| プロダクト | 説明 | 状態 | パス |
|-----------|------|------|------|
| **Forge** | プロンプト生成ツール群 | Active | `forge/` |
| **Gnōsis** | 知識ベースシステム | Active | `forge/gnosis/` |
| **prompt-lang** | AI向けプロンプト言語 | Planning | `prompt-lang/` (予定) |
| **Chat History DB** | セッション履歴DB | Active | `forge/scripts/` |

---

## 🗄️ Data（データ層）

**役割**: 永続化データ。外部システム（Obsidian等）と連携。

| データ | 説明 | パス |
|--------|------|------|
| **Vault** | 長期記憶ストレージ | `vault/` |
| **Gnōsis Data** | 知識ベースデータ（LanceDB） | `gnosis_data/` |
| **Brain** (外部) | Obsidian Vault | `M:\Brain\` |
| **Hegemonikon Store** (外部) | 長期記憶 | `M:\Documents\mine\.hegemonikon\` |

---

## 📁 ディレクトリ構造

```
M:\Hegemonikon\
├── .agent/                    # 🧬 Core: AI制御層
│   ├── workflows/             #   ワークフロー定義
│   ├── skills/                #   M1-M8, P1-P4 スキル
│   └── rules/                 #   制約・プロトコル
│
├── kernel/                    # 🧬 Core: 理論基盤
│
├── forge/                     # 📦 Product: ツール群
│   ├── gnosis/                #   知識ベース CLI
│   ├── prompts/               #   AIプロファイル設定
│   └── scripts/               #   ユーティリティ
│
├── vault/                     # 🗄️ Data: 長期記憶
├── gnosis_data/               # 🗄️ Data: 知識ベースDB
├── docs/                      # ドキュメント
├── archive/                   # アーカイブ
└── runtime/                   # ランタイム
```

---

## 🔧 ワークフロー一覧

| コマンド | 説明 | Module |
|----------|------|--------|
| `/boot` | セッション開始 | M1+M8 |
| `/now` | 現在地確認 | M1+M8 |
| `/nm` | 全体構造（この文書） | M8 |
| `/nh` | セッション履歴 | M8 |
| `/nc [project]` | プロジェクト文脈 | M8 |
| `/nt` | 未解決タスク | M8 |
| `/ask` | 調査依頼生成 | M5 |
| `/src` | Web検索 | M5 |
| `/plan` | 設計プロトコル | M4+M3 |
| `/think` | 熟考・大域最適 | M4-S+M3-S |
| `/pri` | 優先順位判定 | M2 |
| `/code` | 実装プロトコル | M6+M2 |
| `/chk` | 検証・批評 | M7 |
| `/rev` | 日次レビュー | M7+M8 |
| `/hist` | 履歴同期 | M8 |
| `/rec` | 記憶リフレッシュ | M8 |
| `/u` | 主体的見解 | M7+M4 |
| `/p` | 純粋定理 | P1-P4 |

---

## 🧠 スキル一覧

### 拡張定理（M1-M8）

| スキル | 名称 | 役割 | Tempo |
|--------|------|------|-------|
| M1 | Aisthēsis | 知覚・入力処理 | Fast |
| M2 | Krisis | 判断・優先順位 | Fast |
| M3 | Theōria | 理論・因果モデル | Slow |
| M4 | Phronēsis | 実践知・戦略 | Slow |
| M5 | Peira | 探求・情報収集 | Fast |
| M6 | Praxis | 実行・行動 | Fast |
| M7 | Dokimē | 検証・批評 | Slow |
| M8 | Anamnēsis | 記憶・長期保存 | Slow |

### 純粋定理（P1-P4）

| スキル | 名称 | 本質的問い |
|--------|------|-----------|
| P1 | Noēsis | 何を知っているか（認識） |
| P2 | Boulēsis | 何を望むか（意志） |
| P3 | Zētēsis | 何を問うか（探求） |
| P4 | Energeia | 何をするか（行為） |

---

## `/nc` プロジェクトリスト

`/nc [project]` で使用可能なプロジェクト名:

| プロジェクト | 説明 |
|-------------|------|
| `hegemonikon` | 全体システム |
| `agent` | AI制御層（ワークフロー、スキル） |
| `forge` | ツール群 |
| `gnosis` | 知識ベースシステム |
| `prompt-lang` | プロンプト言語 |
| `chat-history-db` | セッション履歴DB |
| `vault` | 長期記憶 |

---

*最終更新: 2026-01-21*
