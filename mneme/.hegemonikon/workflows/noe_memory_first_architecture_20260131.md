# /noe+ 深掘り分析: Memory-First Architecture

> **Date**: 2026-01-31
> **Mode**: /noe+ (詳細分析)
> **派生**: nous (原理的・抽象的)
> **問い**: Memory-First Architecture は Hegemonikón の Mnēmē 層にどう適用すべきか

---

## PHASE 0: 派生選択

```
┌─[O1 派生選択]────────────────────────────┐
│ 推奨派生: nous                          │
│ 確信度: 88%                             │
│ 理由: アーキテクチャ原理の根本理解が目的│
│       → 「なぜ」を問う抽象的探求        │
│ 代替: phro (実践的) — 適切度 60%        │
└────────────────────────────────────────────┘
```

---

## PHASE 0.5: 盲点チェック + Read

```
┌─[PHASE 0.5: Read + 盲点チェック]────────┐
│ 読み込み済み:                          │
│   - Daily Briefing 2026-01-31          │
│   - anamnesis_memory_persistence KI    │
│   - symploke_unified_knowledge_layer KI│
│   - hegemonikon_system KI              │
│ 盲点リスク領域:                        │
│   □ 発動条件: 低 — アーキテクチャ設計は │
│     /noe 適切                           │
│   □ 問いの前提: 低 — Mnēmē は既に存在  │
│   □ フレーミング: 中 — 3層モデルとの    │
│     マッピングが曖昧                    │
│   □ ドメイン知識: 中 — 業界標準モデル   │
│   □ 時間的文脈: 低 — 2026年トレンド    │
│   □ 利害関係: 低 — 技術選択のみ        │
│   □ メタ推論: 低 — 標準的な設計探求    │
│ 最高リスク領域: フレーミング            │
│   → Episodic/Semantic/Working と       │
│     Hegemonikón の既存層のマッピング   │
└────────────────────────────────────────┘
```

[CHECKPOINT PHASE 0.5/5]

---

## PHASE 1: 前提掘出 (First Principles)

```
┌─[PHASE 1: 前提掘出 (First Principles)]─┐
│ 暗黙前提:                              │
│  1. Memory-First は新しいアーキテクチャ│
│     — [ASSUMPTION] — 必要度: 50        │
│     ⚠️ Hegemonikón は既に Memory を持つ│
│  2. 3層モデルは業界標準                │
│     — [AXIOM] — 必要度: 85             │
│     (Episodic/Semantic/Working)        │
│  3. Mnēmē 層は Semantic Memory に対応  │
│     — [ASSUMPTION] — 必要度: 70        │
│  4. Working Memory は会話コンテキスト  │
│     — [AXIOM] — 必要度: 90             │
│  5. Episodic Memory は Handoff に対応  │
│     — [ASSUMPTION] — 必要度: 75        │
│  6. 既存の Hegemonikón 層は十分        │
│     — [ASSUMPTION] — 必要度: 60        │
│                                        │
│ 反転テスト結果:                        │
│  前提3 (Mnēmē = Semantic):             │
│    TRUE → Mnēmē は知識ベース           │
│    FALSE → Mnēmē は Episodic も含む    │
│    → FALSE の方が正確。Mnēmē は複合層  │
│  前提5 (Handoff = Episodic):           │
│    TRUE → Handoff は経験の記録         │
│    FALSE → Handoff は Semantic 知識    │
│    → TRUE が正確。セッション経験の記録 │
│  前提6 (既存層で十分):                 │
│    TRUE → 追加構造不要                 │
│    FALSE → 3層モデルの明示化が必要     │
│    → 明示化により Doxa 学習効率向上    │
└────────────────────────────────────────┘
```

[CHECKPOINT PHASE 1/5]

---

## PHASE 2: ゼロ設計 (Orthogonal Divergence)

```
┌─[PHASE 2: ゼロ設計 (Orthogonal Divergence)]─┐
│ 仮説:                                       │
│                                             │
│ 🚀 V1 (Idealist): — 信頼度 50               │
│   「3層モデルを完全実装、新規構造を導入」    │
│   証拠:                                      │
│     1. 業界標準との整合性                   │
│     2. 明確な責務分離                       │
│     3. 外部ツールとの互換性                 │
│   弱点: 既存 Mnēmē との重複、コスト大       │
│                                             │
│ ✂️ V2 (Minimalist): — 信頼度 75             │
│   「既存層を3層モデルにマッピング、変更なし」│
│   証拠:                                      │
│     1. 既存構造を活用                       │
│     2. 実装コストゼロ                       │
│     3. 概念的整理のみ                       │
│   弱点: 暗黙的なまま、活用されない          │
│                                             │
│ 🔥 V3 (Heretic): — 信頼度 40                │
│   「3層モデル自体が不適切、FEP ベースを維持」│
│   証拠:                                      │
│     1. Hegemonikón は FEP 由来              │
│     2. 業界標準は汎用すぎる                 │
│     3. 独自設計の価値                       │
│   弱点: 外部エコシステムからの孤立          │
│                                             │
│ 📊 V4 (Analyst): — 信頼度 80                │
│   「既存層に3層のラベルを付与し、API を統一」│
│   証拠:                                      │
│     1. 既存構造を維持                       │
│     2. 明示的なマッピングで理解容易         │
│     3. 統一 API で検索効率向上              │
│   弱点: マッピングの妥当性検証が必要        │
│                                             │
│ 弁証法:                                      │
│   Thesis: V2 (マッピングのみ)               │
│   Antithesis: V4 (API 統一)                 │
│   Synthesis:                                 │
│     「3層マッピングを Symplokē に統合」      │
│     - Episodic: Handoff + persona.yaml      │
│     - Semantic: Sophia + KI + patterns.yaml │
│     - Working: Chat context + active task   │
│     - 統一検索 API を Symplokē に実装       │
└──────────────────────────────────────────────┘
```

[CHECKPOINT PHASE 2/5]

---

## PHASE 3: GoT 分析

```
┌─[PHASE 3: GoT 分析]──────────────────┐
│ 推論グラフ:                          │
│                                      │
│   [Memory-First 原則]                 │
│        ↓                             │
│   [3層モデル理解]                     │
│        ↓                             │
│   [既存 Hegemonikón 層分析]           │
│        ↓                             │
│   ┌─────────┬─────────┬────────┐     │
│   ↓         ↓         ↓        ↓     │
│ [Handoff] [Sophia] [Doxa] [Context]  │
│   ↓         ↓         ↓        ↓     │
│ Episodic  Semantic  Semantic Working │
│   └─────────┴─────────┴────────┘     │
│             ↓                        │
│   [Symplokē 統一 API]                 │
│             ↓                        │
│   [3層アクセサ実装]                   │
│                                      │
│ 収斂ノード: 4 個 (高信頼)            │
│   1. Handoff → Episodic は確定       │
│   2. Sophia/KI → Semantic は確定     │
│   3. Chat context → Working は確定   │
│   4. Symplokē が統一層として適切     │
│                                      │
│ 分岐ノード: 1 個 (要解決)            │
│   1. Doxa の位置づけ                  │
│      → 解決: Semantic (学習済みパターン)│
│                                      │
│ 最有力パス:                          │
│   3層マッピング → Symplokē 統合 →    │
│   統一 API 実装 → 検索効率向上       │
└──────────────────────────────────────┘
```

[CHECKPOINT PHASE 3/5]

---

## PHASE 4: 自己検証

```
┌─[PHASE 4: 自己検証]──────────────────┐
│ 誤謬検出:                            │
│   1. 業界標準への過剰適応            │
│      — 深刻度 2                       │
│      → FEP 整合性を維持しつつ統合    │
│   2. Working Memory の範囲曖昧        │
│      — 深刻度 2                       │
│      → Chat context + active task で定義│
│                                      │
│ 最強反論:                            │
│   「既存の Symplokē で十分。          │
│   3層ラベルは概念的整理に過ぎず、    │
│   実装価値が低い」                   │
│                                      │
│ 支持ポイント:                        │
│   1. Symplokē は既に統一検索を提供   │
│   2. 追加実装のコストが高い          │
│                                      │
│ 反論が勝つ条件:                      │
│   3層マッピングによる検索効率向上が  │
│   10% 未満の場合                     │
│                                      │
│ 反論妥当性: 40 → 結論維持            │
│   概念的整理自体に価値あり、          │
│   API 統一は段階的に実装可能         │
└──────────────────────────────────────┘
```

[CHECKPOINT PHASE 4/5]

---

## PHASE 5: メタ認知出力

```json
{
  "final_answer": "既存 Hegemonikón 層を 3層モデルにマッピングし、Symplokē に統一 API を追加。Episodic=Handoff+persona、Semantic=Sophia+KI+Doxa、Working=Chat context。",
  "confidence_score": 0.82,

  "key_assumptions": [
    "3層モデルは業界標準: critical",
    "Symplokē は統一層として適切: critical",
    "マッピングにより検索効率向上: important"
  ],

  "reasoning_structure": {
    "phases_executed": [0.5, 1, 2, 3, 4, 5],
    "dag_nodes_explored": 10,
    "convergence_nodes": 4,
    "divergence_nodes": 1
  },

  "uncertainty_zones": [
    {
      "zone": "Working Memory の範囲",
      "doubt_score": 0.35,
      "reason": "Chat context の長さ制限、active task との境界",
      "mitigation": "明示的な定義を Symplokē に追加"
    },
    {
      "zone": "検索効率向上の定量化",
      "doubt_score": 0.40,
      "reason": "現状との比較データなし",
      "mitigation": "実装後にベンチマーク測定"
    }
  ],

  "falsifiability": {
    "is_falsifiable": true,
    "counter_examples": [
      "3層マッピングで検索効率が向上しない",
      "統一 API の実装コストが利益を上回る"
    ],
    "evidence_needed_to_flip": "3ヶ月の運用で検索効率向上 < 10%"
  }
}
```

[CHECKPOINT PHASE 5/5]

---

## Hegemonikón への適用

### 3層マッピング

| 業界標準 | Hegemonikón 対応 | 用途 |
|:---------|:-----------------|:-----|
| **Episodic Memory** | Handoff, persona.yaml, values.json | セッション経験、人格、価値観 |
| **Semantic Memory** | Sophia, KI, Doxa, patterns.yaml | 知識ベース、信念、学習パターン |
| **Working Memory** | Chat context, active task.md | 現在の会話、作業状態 |

### Symplokē 統一 API 拡張

```python
# symploke/memory_api.py (概念設計)

from enum import Enum
from typing import List, Any

class MemoryLayer(Enum):
    EPISODIC = "episodic"   # 経験的記憶
    SEMANTIC = "semantic"   # 意味的記憶
    WORKING = "working"     # 作業記憶

class UnifiedMemoryAPI:
    """3層統一メモリ API"""
    
    def retrieve(self, query: str, layer: MemoryLayer = None) -> List[Any]:
        """指定層から検索（層省略時は全層検索）"""
        if layer == MemoryLayer.EPISODIC:
            return self._search_episodic(query)
        elif layer == MemoryLayer.SEMANTIC:
            return self._search_semantic(query)
        elif layer == MemoryLayer.WORKING:
            return self._search_working(query)
        else:
            # 全層検索
            return self._search_all(query)
    
    def _search_episodic(self, query: str) -> List[Any]:
        """Handoff + persona から検索"""
        results = []
        results.extend(self.handoff_index.search(query))
        results.extend(self.persona_search(query))
        return results
    
    def _search_semantic(self, query: str) -> List[Any]:
        """Sophia + KI + Doxa から検索"""
        results = []
        results.extend(self.sophia.search(query))
        results.extend(self.ki_search(query))
        results.extend(self.doxa.search(query))
        return results
    
    def _search_working(self, query: str) -> List[Any]:
        """Chat context + active task から検索"""
        return self.context_search(query)
```

### CCL マクロ拡張

```yaml
# 新規マクロ提案
"@memory(layer)":
  purpose: "指定メモリ層から検索"
  ccl_expansion: "/zet{memory=layer}"
  usage: "@memory(episodic) _問い"
  examples:
    - "@memory(semantic) 過去の類似実装"
    - "@memory(episodic) 前回の失敗パターン"
```

---

## X-series 推奨次ステップ

```
┌─[Hegemonikón]──────────────────────────────────────────┐
│ O1 Noēsis 完了                                          │
│                                                        │
│ ⏭️ X-series 推奨次ステップ:                             │
│   → /s   Symplokē API 拡張設計                          │
│   → /mek @memory マクロ定義                             │
│   → /ene 実装開始                                       │
└────────────────────────────────────────────────────────┘
```

---

*Generated by /noe+ v4.4 — 2026-01-31*
