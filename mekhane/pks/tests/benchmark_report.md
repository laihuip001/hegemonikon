# PKS 検索品質ベンチマークレポート

実行日時: 2026-02-14 16:26

## サマリー

| 指標 | 値 | 目標 | 判定 |
|:-----|---:|:----:|:----:|
| **Precision@5** (平均) | 0.880 | ≥ 0.60 | ✅ |
| **MRR** (平均) | 0.933 | ≥ 0.50 | ✅ |
| **Source Coverage** (平均) | 0.489 | ≥ 0.70 | ❌ |
| **Latency** (平均) | 2.7s | ≤ 15s | ✅ |
| **Latency** (合計) | 40.2s | — | — |

## クエリ別結果

| ID | カテゴリ | 説明 | P@5 | MRR | Cov | Latency | KW |
|:---|:---------|:-----|----:|----:|----:|--------:|---:|
| T1 | theoretical_ | FEP の基礎理論 | 1.00 ✅ | 1.00 | 1.00 | 8.3s | 4/5 |
| T2 | theoretical_ | 能動的推論と計画 | 1.00 ✅ | 1.00 | 1.00 | 2.2s | 4/4 |
| T3 | theoretical_ | マルコフ毛布と自己組織化 | 0.40 ⚠️ | 1.00 | 1.00 | 2.3s | 2/4 |
| H1 | hgk_concepts | CCL ワークフロー言語 | 1.00 ✅ | 1.00 | 0.00 | 2.2s | 5/5 |
| H2 | hgk_concepts | O-series 定理群 | 1.00 ✅ | 1.00 | 0.33 | 2.2s | 5/6 |
| H3 | hgk_concepts | 二層フィルター理論 | 0.80 ✅ | 1.00 | 1.00 | 2.2s | 1/5 |
| I1 | implementati | PKS 実装 | 1.00 ✅ | 1.00 | 0.50 | 2.2s | 5/5 |
| I2 | implementati | Dendron 存在証明 | 1.00 ✅ | 1.00 | 0.00 | 2.3s | 3/5 |
| I3 | implementati | Hermēneus パーサー | 1.00 ✅ | 1.00 | 0.00 | 2.2s | 4/6 |
| X1 | cross_domain | 圏論と認知の接続 | 1.00 ✅ | 1.00 | 0.50 | 2.2s | 3/5 |
| X2 | cross_domain | 精度加重と注意 | 1.00 ✅ | 1.00 | 1.00 | 2.3s | 5/5 |
| X3 | cross_domain | Cortex API 直接アクセス | 1.00 ✅ | 1.00 | 0.50 | 2.4s | 1/5 |
| E1 | edge_case | 完全無関係クエリ (ノイズ検出) | 0.00 ❌ | 0.00 | 0.00 | 2.3s | — |
| E2 | edge_case | 日本語クエリの精度 | 1.00 ✅ | 1.00 | 0.50 | 2.4s | 3/3 |
| E3 | edge_case | 運用系キーワード | 1.00 ✅ | 1.00 | 0.00 | 2.5s | 5/5 |

## カテゴリ別分析

### ✅ 理論コア (P@5=0.80, MRR=1.00, Cov=1.00)

- **T1** FEP の基礎理論: P@5=1.00
  1. [gnosis] 1.240 — Improving the Minimum Free Energy Principle to the
  2. [gnosis] 1.182 — Unifying Message Passing Algorithms Under the Fram
  3. [gnosis] 1.167 — A Message Passing Realization of Expected Free Ene
- **T2** 能動的推論と計画: P@5=1.00
  1. [gnosis] 1.250 — Expected Free Energy-based Planning as Variational
  2. [gnosis] 1.196 — Whence the Expected Free Energy?
  3. [gnosis] 1.140 — Retrospective surprise: A computational component 
- **T3** マルコフ毛布と自己組織化: P@5=0.40
  1. [gnosis] 1.250 — The Markov blankets of life: autonomy, active infe
  2. [gnosis] 1.070 — Attractor Engine Deep Dive
  3. [kairos] 1.000 — Bye Session Finalization

### ✅ HGK 概念 (P@5=0.93, MRR=1.00, Cov=0.44)

- **H1** CCL ワークフロー言語: P@5=1.00
  1. [gnosis] 1.274 — Implementing EPT Structure Layer
  2. [gnosis] 1.241 — Enhancing Hegemonik n Documentation
  3. [gnosis] 1.240 — Bou Ccl Meta Verification 20260129
- **H2** O-series 定理群: P@5=1.00
  1. [gnosis] 1.250 — Axiom Hierarchy V2.1 Backup
  2. [gnosis] 1.248 — Axiom Hierarchy
  3. [gnosis] 1.246 — Axiom Hierarchy V3 Experimental
- **H3** 二層フィルター理論: P@5=0.80
  1. [gnosis] 1.022 — Implementing Morphism Enforcement
  2. [gnosis] 1.000 — Dendron Project Creation
  3. [kairos] 1.000 — Dendron Package Audit

### ✅ 実装 (P@5=1.00, MRR=1.00, Cov=0.17)

- **I1** PKS 実装: P@5=1.00
  1. [gnosis] 1.150 — Jukudoku Spisak Friston2025 20260207
  2. [gnosis] 1.118 — Attractor Engine Deep Dive
  3. [sophia] 1.050 — ki-hegemonikon_knowledge_infrastructure-maintenanc
- **I2** Dendron 存在証明: P@5=1.00
  1. [gnosis] 1.180 — Dendron Project Creation
  2. [gnosis] 1.175 — Dendron Package Audit
  3. [gnosis] 1.132 — Dendron Automation and Workflow
- **I3** Hermēneus パーサー: P@5=1.00
  1. [gnosis] 1.200 — Hermeneus Development Planning
  2. [gnosis] 1.093 — CCL Execution Guarantee Architecture
  3. [gnosis] 1.093 — CCL Execution Guarantee Architecture

### ✅ クロスドメイン (P@5=1.00, MRR=1.00, Cov=0.67)

- **X1** 圏論と認知の接続: P@5=1.00
  1. [gnosis] 1.180 — Categorial Compositionality: A Category Theory Exp
  2. [gnosis] 1.172 — Category Theory Ccl Report 20260203
  3. [gnosis] 1.124 — Token Space: A Category Theory Framework for AI Co
- **X2** 精度加重と注意: P@5=1.00
  1. [gnosis] 1.117 — No evidence for increased precision-weighting of p
  2. [gnosis] 1.107 — Evidence for implicit and adaptive deployment of p
  3. [gnosis] 1.100 — Transdiagnostic failure to adapt interoceptive pre
- **X3** Cortex API 直接アクセス: P@5=1.00
  1. [gnosis] 1.043 — Synergeia API Optimization
  2. [gnosis] 1.036 — Tier 1 Specialist Expansion
  3. [gnosis] 1.035 — Implementing MCP Server Stub

### ✅ エッジケース (P@5=0.67, MRR=0.67, Cov=0.17)

- **E1** 完全無関係クエリ (ノイズ検出): P@5=0.00
  1. [gnosis] 1.060 — Digestor Automation Setup
  2. [kairos] 1.000 — Defining Specialist Archetypes
  3. [sophia] 1.000 — ki-hegemonikon_multi_agent_orchestration-overview
- **E2** 日本語クエリの精度: P@5=1.00
  1. [gnosis] 1.200 — Axiom Hierarchy V3 Experimental
  2. [gnosis] 1.099 — Implement CCL Debug & Generate
  3. [gnosis] 1.070 — The Free-energy Principle: A Unified Theory of Bra
- **E3** 運用系キーワード: P@5=1.00
  1. [gnosis] 1.298 — Session Handoff and Workflow Update
  2. [gnosis] 1.240 — Workflow Update and Cleanup
  3. [gnosis] 1.234 — Workflow Update and Cleanup

## ソース分布

| ソース | 出現回数 (Top-5) | 平均スコア | 最高 | 最低 |
|:-------|-----------------:|-----------:|-----:|-----:|
| gnosis | 62 | 1.138 | 1.298 | 1.000 |
| kairos | 5 | 1.000 | 1.001 | 1.000 |
| sophia | 4 | 1.012 | 1.050 | 1.000 |
| chronos | 4 | 0.999 | 1.000 | 0.995 |

## 弱点分析 & 改善提案

### 弱いクエリ

- **E1** (完全無関係クエリ (ノイズ検出)): P@5=0.00
  → 期待通り（無関係クエリ）

### ソースカバレッジ不足

- **H1**: 結果ソース={'gnosis'}
- **H2**: 結果ソース={'gnosis'}
- **I2**: 結果ソース={'gnosis'}
- **I3**: 結果ソース={'gnosis'}

### 改善提案

1. **スコア正規化**: Gnōsis (L2距離) と pkl (cosine) の異なるスコア体系を統一
2. **日本語対応**: multilingual embedding モデルの評価
3. **リランキング**: キーワード + セマンティックのハイブリッドスコアリング
4. **インデックス更新**: Sophia (116件) の拡充
