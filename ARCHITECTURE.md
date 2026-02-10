# Hegemonikón Architecture

> **最終更新**: 2026-02-10
> **目的**: PJ 全体の技術構造を一目で理解する

---

## システム全体像

```mermaid
graph TB
    subgraph "ユーザー接点"
        IDE["Antigravity IDE<br>(Claude)"]
        DT["hgk-desktop<br>(Tauri + Three.js)"]
    end

    subgraph "認知制御層"
        HRM["hermeneus/<br>CCL コンパイラ"]
        CCL["ccl/<br>言語仕様"]
        KRN["kernel/<br>公理体系 (96要素)"]
    end

    subgraph "実行基盤 (mekhane/)"
        SYM["symploke<br>統合"]
        FEP["fep<br>自由エネルギー"]
        ANA["anamnesis<br>記憶・検索"]
        API["api<br>REST/WS"]
        DEN["dendron<br>存在証明"]
    end

    subgraph "マルチエージェント"
        SYN["synergeia/<br>Jules 連携"]
        MCP["MCP Servers<br>(5+)"]
    end

    subgraph "記憶"
        MNM["mneme/<br>Handoff・KI"]
        GNO["gnosis_data/<br>論文DB"]
    end

    IDE --> HRM
    IDE --> MCP
    IDE --> DT
    HRM --> CCL
    HRM --> KRN
    HRM --> FEP
    DT --> API
    API --> ANA
    API --> FEP
    SYM --> ANA
    SYM --> FEP
    MCP --> ANA
    MCP --> HRM
    SYN --> IDE
    ANA --> MNM
    ANA --> GNO
```

---

## ディレクトリ構造

| パス | 用途 | 詳細 |
|:-----|:-----|:-----|
| **kernel/** | 公理体系定義 | SACRED_TRUTH, ousia.md, schema.md, horme.md 等。96要素の正本 |
| **ccl/** | CCL 言語仕様 | 演算子定義、マクロ参照、使用例 |
| **hermeneus/** | CCL コンパイラ | パーサー → 展開 → LMQL 翻訳 → LLM 実行 → 検証。MCP サーバー提供 |
| **mekhane/** | 実行基盤 | 26 サブモジュール。[詳細](mekhane/ARCHITECTURE.md) |
| **hgk-desktop/** | デスクトップ UI | Tauri + Vite + Three.js。3D グラフ可視化 |
| **synergeia/** | マルチエージェント | Jules (Gemini) API クライアント、並列タスク実行 |
| **mneme/** | 長期記憶 | Handoff, セッション履歴, パターン記録 |
| **gnosis_data/** | 論文 DB | LanceDB ベクトルストア。Gnōsis MCP で検索 |
| **docs/** | ドキュメント | 設計文書、研究ノート、レポート |
| **.agent/** | AI エージェント設定 | Rules, Workflows (47), Skills (55), Templates |
| **scripts/** | ユーティリティ | PJ 登録、MCP ラッパー、ヘルスチェック |

---

## 中核コンポーネント

### 1. Hermēneus (CCL コンパイラ)

```
CCL 式 → Parser → AST → Expander → LMQL → LLM 実行 → 検証
         ↑                               ↑
     hermeneus/src/parser.py     hermeneus/src/executor.py
```

| モジュール | 役割 |
|:-----------|:-----|
| `parser.py` | CCL 構文解析 → AST |
| `expander.py` | マクロ展開 |
| `translator.py` | AST → LMQL 変換 |
| `executor.py` | LLM 実行 + Multi-Agent Debate 検証 |
| `dispatch.py` | AST + WF マッチング + 実行計画テンプレート |
| `mcp_server.py` | MCP プロトコル (6 ツール) |

### 2. mekhane/ (実行基盤)

**Terminal Object**: `anamnesis` — ほぼ全モジュールが依存（被依存数 9）

| 層 | モジュール | 役割 |
|:---|:-----------|:-----|
| L0 外部接点 | api, mcp | FastAPI REST, MCP servers |
| L1 統合 | symploke | /boot シーケンス、統合 |
| L2 認知 | fep, ccl, taxis, synedrion | FEP 計算、分類、評議会 |
| L3 基盤 | anamnesis, dendron, peira, poiema | 記憶、存在証明、監視、出力 |
| L4 ツール | ergasterion, scripts | 開発ワークショップ |

→ [mekhane 内部アーキテクチャ](mekhane/ARCHITECTURE.md)

### 3. hgk-desktop/ (デスクトップ UI)

| ファイル | 役割 |
|:---------|:-----|
| `src/views/graph3d.ts` | Three.js 3D グラフ可視化 (96要素 + LinkGraph 544ノード) |
| `src/api/client.ts` | バックエンド API クライアント |
| `src-tauri/` | Tauri ネイティブシェル設定 |

### 4. .agent/ (AI 設定)

| ディレクトリ | 数 | 内容 |
|:-------------|:---|:-----|
| `rules/` | 16+ | 行動制約 (BC-1〜BC-16)、安全不変条件 |
| `workflows/` | 47 | ワークフロー定義 (/boot, /bye, /noe, /s 等) |
| `skills/` | 55 | スキル定義 (6 系列 × 各4定理 + ユーティリティ) |

---

## MCP サーバー

| 名前 | 提供元 | ツール数 | 用途 |
|:-----|:-------|:---------|:-----|
| **hermeneus** | ローカル | 6 | CCL dispatch/compile/execute/audit |
| **gnosis** | ローカル | 3 | 論文検索 (LanceDB) |
| **sophia** | ローカル | 4 | KI 検索、バックリンク |
| **mneme** | ローカル | 3 | 統合記憶検索 |
| **sympatheia** | ローカル | 6 | 通知、WBC、フィードバック |
| **jules** | ローカル | 4 | Jules コーディング連携 |
| **prompt-lang** | ローカル | 1 | プロンプト生成 |
| **digestor** | ローカル | 3 | 論文消化パイプライン |

---

## データフロー

```
ユーザー入力
    ↓
/.agent/workflows/ → WF 定義読込
    ↓
hermeneus/ → CCL パース + 実行
    ↓
mekhane/fep/ → FEP 認知計算
    ↓
mekhane/anamnesis/ → 記憶検索 (LanceDB)
    ↓
出力 → mneme/ (記録) + hgk-desktop/ (可視化)
```

---

## 技術スタック

| 領域 | 技術 |
|:-----|:-----|
| 言語 | Python 3.13, TypeScript |
| フレームワーク | FastAPI, Vite, Tauri |
| 可視化 | Three.js, d3-force-3d |
| DB | LanceDB (ベクトル検索) |
| AI | Anthropic Claude, Google Gemini, OpenAI |
| 形式検証 | FEP (変分自由エネルギー最小化) |
| CI | pytest, pyproject.toml |

---

## 関連文書

| ドキュメント | 内容 |
|:-------------|:-----|
| [README.md](README.md) | 96要素体系と設計思想 |
| [mekhane/ARCHITECTURE.md](mekhane/ARCHITECTURE.md) | mekhane 内部の依存グラフ・層構造 |
| [kernel/SACRED_TRUTH.md](kernel/SACRED_TRUTH.md) | 不変真理 |
| [AGENTS.md](AGENTS.md) | AI エージェント向けガイド |
| [.agent/rules/hegemonikon.md](.agent/rules/hegemonikon.md) | 公理体系 v3.3 |

---

*Hegemonikón Architecture — 認知の地図 (2026-02-10)*
