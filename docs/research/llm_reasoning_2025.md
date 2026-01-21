---
doc_id: "LLM_REASONING_RESEARCH_2025"
version: "1.0.0"
created: "2026-01-20"
source: "Perplexity AI 調査"
status: "REFERENCE"
---

# AIエージェント熟考プロセス最適化フレームワーク｜2025-2026年推論能力強化研究

> **要約**: LLMの推論能力強化は4軸（フレームワーク進化・自己批判・適応的知識統合・メタ認知）で進化中。

---

## 主要知見サマリー

### 1. 推論フレームワークの進化

| 技法 | 構造 | 特徴 |
|------|------|------|
| **CoT** | 線形 | 単一パス、誤り波及リスク |
| **ToT** | 木構造 | BFS/DFS探索、分岐評価 |
| **GoT** | 有向グラフ | 集約操作、部分結果再利用 |
| **TaT** | 表形式 | 並列評価、構造化思考 |

### 2. 自己批判メカニズム

| 技法 | 構造 | 効果 |
|------|------|------|
| **Reflexion** | Generate→Critique→Refine | +4-10点改善 |
| **Multi-Persona** | 楽観/悲観/現実 | 15-22%正解率向上 |
| **MAD (Debate)** | Proponent-Opponent-Arbitrator | +4-7%改善 |

### 3. 外部知識統合

| 技法 | 特徴 |
|------|------|
| **Agentic RAG** | クエリ複雑度に応じて動的戦略 |
| **SIM-RAG** | 情報充足性Critic判定 |
| **Search-R1** | RL最適化、41%向上 |

### 4. メタ認知

| 技法 | 目的 |
|------|------|
| **RES** | 推論-説明対称性で不確実性推定 |
| **知識境界** | PAK/PSK/MSK/MAK四分類 |
| **DeepSeek-R1** | RL訓練で推論パターン自動習得 |

---

## /think への実装ロードマップ

### Phase 1（即時実装可能）

- [x] Self-Discovery: atomic module選択
- [x] Reflexion: 独立Critiqueステップ
- [x] Simple Multi-Agent: 2 agent debate

### Phase 2（リソース確保後）

- [ ] Agentic RAG: 複雑度判定+適応検索
- [ ] Multi-Persona: 3-persona並列生成
- [ ] ToT (shallow): B=2-3探索

### Phase 3（大規模リソース）

- [ ] RL推論スケーリング
- [ ] Graph-of-Thoughts
- [ ] 完全Agentic Multi-Agent

---

## ベンチマーク参照

| 技法 | MATH | AIME 2024 | 実装複雑度 |
|------|------|-----------|-----------|
| CoT Base | ~35% | 15.6% | 低 |
| ToT (B=3) | ~55% | ~42% | 中 |
| DeepSeek-R1 | 90.9% | 79.8% | 高 |

---

*参照: arxiv, nature, semanticscholar (2024-2026)*
