# HGK Vocabulary — 定理名・用語辞典

> Jules 向け: コード内のギリシャ語・専門用語の意味リファレンス。
> これらの名前はランダムではなく、体系的な理論に基づく。

## 24 Theorems (定理) — 変数名・モジュール名の由来

### O-series (Ousia 本質, L0)

| # | Name | Japanese | Role in Code |
|:--|:-----|:---------|:-------------|
| O1 | **Noēsis** | 深い認識 | `noe` — 本質追求 WF |
| O2 | **Boulēsis** | 意志 | `bou` — 目的設定 WF |
| O3 | **Zētēsis** | 探求 | `zet` — 問い発見 WF |
| O4 | **Energeia** | 行為 | `ene` — 実行 WF |

### S-series (Schema 様態, L1)

| # | Name | Japanese | Role in Code |
|:--|:-----|:---------|:-------------|
| S1 | **Hermēneia** | 解釈 | `hermeneus/` — CCL パーサー |
| S2 | **Mekhanē** | 方法 | `mekhane/` — 実装基盤 |
| S3 | **Chronos** | 計画 | `chr` — 時間管理 |
| S4 | **Praxis** | 実践 | `pra` — 実践 WF |

### H-series (Hormē 傾向, L2a)

| # | Name | Japanese | Role in Code |
|:--|:-----|:---------|:-------------|
| H1 | **Propatheia** | 前感情 | `pro` — 直感評価 |
| H2 | **Pistis** | 確信 | `pis` — 確信度評価 |
| H3 | **Orexis** | 欲求 | `ore` — 欲求評価 |
| H4 | **Doxa** | 信念 | `dox` — 信念記録 |

### P-series (Perigraphē 条件, L2b)

| # | Name | Japanese | Role in Code |
|:--|:-----|:---------|:-------------|
| P1 | **Khōra** | 空間 | `kho` — 環境設定 |
| P2 | **Telos** | 目的 | `tel` — 目標設定 |
| P3 | **Eukairia** | 好機 | `euk` — タイミング |
| P4 | **Stasis** | 安定 | `sta` — 状態管理 |

### K-series (Kairos 文脈, L3)

| # | Name | Japanese | Role in Code |
|:--|:-----|:---------|:-------------|
| K1 | **Taksis** | 配置 | `tak` — タスク分類 |
| K2 | **Sophia** | 知恵 | `sop` — 調査依頼 |
| K3 | **Anamnēsis** | 想起 | `ana` — 記憶検索 |
| K4 | **Epistēmē** | 知識 | `epi` — 知識確立 |

### A-series (Akribeia 精密, L4)

| # | Name | Japanese | Role in Code |
|:--|:-----|:---------|:-------------|
| A1 | **Hexis** | 認知態勢 | 態勢設定・習慣化 |
| A2 | **Krisis** | 判定 | `dia` — 敵対的レビュー |
| A3 | **Epimeleia** | 配慮 | 保守・メンテナンス |
| A4 | **Epistēmē** | 知識 | `epi` — 知識確立 |

## Module Name Glossary

| Greek Module | Meaning | Location |
|:-------------|:--------|:---------|
| **Hermēneus** | Interpreter | `hermeneus/` — CCL parser + WF engine |
| **Mekhanē** | Machine/Method | `mekhane/` — implementation layer |
| **Symplokē** | Interweaving | `mekhane/symploke/` — Jules reviews |
| **Ochēma** | Vehicle | `mekhane/ochema/` — LLM routing |
| **Dendron** | Tree | `mekhane/dendron/` — structural checks |
| **Peira** | Trial | `mekhane/peira/` — health monitoring |
| **Synteleia** | Completion | `mekhane/synteleia/` — safety verification |
| **Ergastērion** | Workshop | `mekhane/ergasterion/` — paper analysis |
| **Anamnēsis** | Recollection | `mekhane/anamnesis/` — knowledge search |
| **Mnēmē** | Memory | `mneme/` — session/handoff storage |
| **Gnōsis** | Knowledge | knowledge base — 27K+ papers |
| **Taxis** | Arrangement | `.agent/projects/taxis/` — classifier |
| **Aristos** | Best | `.agent/projects/aristos/` — evolution |
| **Kairos** | Right moment | conversation index |

## Common Abbreviations in Code

| Abbrev | Full | Context |
|:-------|:-----|:--------|
| `WF` | Workflow | Cognitive workflow |
| `BC` | Behavioral Constraint | Agent rules |
| `KI` | Knowledge Item | Sophia entries |
| `CCL` | Cognitive Control Language | DSL |
| `FEP` | Free Energy Principle | Core theory |
| `HGK` | Hegemonikón | Project codename |
| `LS` | Language Server | Antigravity IDE backend |

## HGK Knowledge Base CLI

`scripts/hegemonikon_kb.py` — プロジェクト知識の統合検索ツール。

| Command | Usage | Example |
|:--------|:------|:--------|
| `query` | 全ソース横断検索 | `hegemonikon-kb query FEP` |
| `theorem` | 定理詳細表示 | `hegemonikon-kb theorem K4` |
| `vocab` | 用語検索 | `hegemonikon-kb vocab Mekhanē` |
| `context` | context/ 一覧 | `hegemonikon-kb context` |
