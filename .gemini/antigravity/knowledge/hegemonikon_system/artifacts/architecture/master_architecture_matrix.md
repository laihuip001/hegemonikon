# Hegemonikón Master Architecture Matrix (Πίναξ)

## 1. 定理と系列の統合マトリックス (6-Series Matrix)

Hegemonikón は、変分自由エネルギー最小化 (FEP) をエンジンとし、6 つの系列（O, S, H, P, K, A）を通じて環境認識から行為実行までの認知フローを制御する。

| 系列 | 名称 | 役割 | FEP 構成要素 |
|:---|:---|:---|:---|
| **O** | **Ousia** | 本質・認識 | 推論 & 生成モデル |
| **S** | **Schema** | 戦略・方法 | 方策選択 (Scale/Tool) |
| **H** | **Hormē** | 衝動・信念 | 精度重み付け (Prior) |
| **P** | **Perigraphē** | 環境・文脈 | 尤度 & 観測空間 |
| **K** | **Kairos** | 時間的文脈 | 時間的足場架け (Scaffolding) |
| **A** | **Akribeia** | 精密・評価 | 精度重み付け (Posterior) |

### 精度重み付けメカニズム (A-Series)

A-Series はシステム全体の精度重み付けを制御する。

- **A1 Pathos**: 精度感情の変調。
- **A2 Krisis**: 判定の確信度閾値設定。
- **A3 Gnōmē**: 抽象精度の決定（具体 vs 普遍）。
- **A4 Epistēmē**: 知識の認識論的確実性調整。

---

## 2. マスター・インデックス (Πίναξ: Pinax)

システムの全階層をマッピングし、発見可能性（Discoverability）を維持するためのインデックス構造。

| 次元 | 数 | 内容 |
|:---|:---|:---|
| **公理** | 7 | FEP, Flow, Value, Scale, Function, Valence, Precision |
| **定理** | 24 | 6系列 × 4定理 (O, S, H, P, K, A) |
| **関係 (X-series)** | 36 | 定理間の接続マトリックス |
| **総計 (System Core)** | **60** | 認知プロセスの完全な体系化 |
| **定理グループ** | **2** | Poiēsis (O,S,H) / Dokimasia (P,K,A) |
| **ワークフロー** | 37+ | 核心コマンド群 |

### 検索ブリッジ (Search Bridge)

レガシーな工業用語と哲学的な定理用語の対応付け。

- **TDD** ↔ S3 Stathmos (Dokimē)
- **Chaos Monkey** ↔ A2 Krisis (Anarkhia)
- **Feature Flags** ↔ O4 Energeia (Kleis)
- **Docker First** ↔ P1 Khōra (Sphragis)

---

## 3. シリーズ間の接続 (X-series Matrix)

全 36 の関係マトリックス（$6 \times 6$）により、系列間の相互作用を定義する。

- **A1 + O**: 感情誘導型の認識確信度。
- **A2 + S**: 判定に基づく戦略選択。
- **A3 + H**: 見識による動機配分。
- **Hub-Oscillation v3.0**: 各ハブ（`/o`, `/s` 等）はシリーズ内 4 定理の巡回振動 (`~`) として駆動。

---

## 4. Mekhanē 実装レイヤーマップ

| レイヤー | コンポーネント | 機能 |
|:---|:---|:---|
| **Mnēmē** | Vault / Index | 原子的な永続化と意味検索 |
| **Symplokē** | Semantic Search | HNSWlib & Sophia 知識グラフ |
| **Mekhanē** | **Synergeia** | **Distributed CCL Execution (Claude/Gemini/Perplexity)** |
| **Audit** | **Synteleia** | **Poiēsis/Dokimasia Ensembles (Audit Agents)** |
| **Strategos** | Derivative Selector | 能動的推論に基づく派生選択 |
| **τ (Tau)** | Tactical Engines | プロトタイプ等の戦術的実行器 |

---
*Updated: 2026-02-01 | Hegemonikón Architectural Record v7.8 (Poiēsis/Dokimasia Layering)*
