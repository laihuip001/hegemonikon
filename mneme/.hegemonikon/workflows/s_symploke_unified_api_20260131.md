# /s- Symplokē 統一 API 設計

> **Date**: 2026-01-31
> **Mode**: /s- (最小計画)
> **Origin**: Memory-First Architecture (/noe+ 2026-01-31)

---

## STAGE 0: Scale Determination

```
📊 Scale 宣言: 🔭 Meso
   → 強制レベル: L2-std
   → 理由: 既存 Symplokē 層に 3層 API を追加
           複数 KI/ファイルに影響
```

---

## STAGE 1: Strategy Selection

```
⚖️ Explore/Exploit: Exploit (確実なパス)
📋 Plans: B (Robust) — 段階的実装

📅 Y-1 評価:
  Fast:    ✅ 即座に 3層検索が可能
  Slow:    ✅ 6ヶ月でパターン蓄積
  Eternal: ✅ 業界標準との整合性
```

---

## STAGE 2: Success Criteria

| 軸 | Must | Should | Could |
|:---|:-----|:-------|:------|
| 機能 | 3層別検索 API | 全層統合検索 | 優先度付き検索 |
| 品質 | 既存 Symplokē と整合 | 型安全 | キャッシュ |
| 性能 | < 1秒 | — | — |

---

## STAGE 3: Blueprint

### アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                    Symplokē Unified API                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐                                        │
│  │  retrieve()     │ ← 統一エントリポイント                  │
│  │  layer: Enum    │                                        │
│  └────────┬────────┘                                        │
│           │                                                  │
│  ┌────────┴────────┬─────────────┬─────────────┐            │
│  ↓                 ↓             ↓             ↓            │
│ [episodic]      [semantic]    [working]     [all]          │
│  ↓                 ↓             ↓             ↓            │
│ Handoff          Sophia        Context       並列検索      │
│ persona          KI            task.md       結果マージ    │
│ values           Doxa                                       │
│                  patterns                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3層マッピング詳細

| 層 | Hegemonikón 対応 | 検索対象 |
|:---|:-----------------|:---------|
| **Episodic** | 経験的記憶 | Handoff, persona.yaml, values.json |
| **Semantic** | 意味的記憶 | Sophia, KI, Doxa, patterns.yaml |
| **Working** | 作業記憶 | Chat context, task.md, active plans |

### API 仕様

```python
# symploke/memory_api.py

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Any
from pathlib import Path

class MemoryLayer(Enum):
    """3層メモリモデル"""
    EPISODIC = "episodic"   # 経験的記憶
    SEMANTIC = "semantic"   # 意味的記憶
    WORKING = "working"     # 作業記憶
    ALL = "all"             # 全層検索

@dataclass
class MemoryResult:
    """検索結果"""
    layer: MemoryLayer
    source: str           # "handoff", "ki", "doxa", etc.
    content: str
    relevance: float      # 0.0 - 1.0
    path: Optional[Path]  # ファイルパス（存在する場合）

class UnifiedMemoryAPI:
    """Symplokē 統一メモリ API"""
    
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self._init_indices()
    
    def retrieve(
        self, 
        query: str, 
        layer: MemoryLayer = MemoryLayer.ALL,
        limit: int = 10
    ) -> List[MemoryResult]:
        """
        指定層からクエリに関連する記憶を検索
        
        Args:
            query: 検索クエリ
            layer: 検索対象層（省略時は全層）
            limit: 最大結果数
        
        Returns:
            関連度順にソートされた検索結果
        """
        if layer == MemoryLayer.ALL:
            return self._search_all(query, limit)
        elif layer == MemoryLayer.EPISODIC:
            return self._search_episodic(query, limit)
        elif layer == MemoryLayer.SEMANTIC:
            return self._search_semantic(query, limit)
        elif layer == MemoryLayer.WORKING:
            return self._search_working(query, limit)
    
    # ─────────────────────────────────────────────────
    # Episodic Memory: 経験的記憶
    # ─────────────────────────────────────────────────
    def _search_episodic(self, query: str, limit: int) -> List[MemoryResult]:
        """Handoff + persona + values から検索"""
        results = []
        
        # Handoff 検索
        handoff_results = self.handoff_index.search(query, limit)
        for r in handoff_results:
            results.append(MemoryResult(
                layer=MemoryLayer.EPISODIC,
                source="handoff",
                content=r.content,
                relevance=r.score,
                path=r.path
            ))
        
        # persona.yaml 検索
        persona_results = self._search_persona(query)
        results.extend(persona_results)
        
        return sorted(results, key=lambda x: x.relevance, reverse=True)[:limit]
    
    # ─────────────────────────────────────────────────
    # Semantic Memory: 意味的記憶
    # ─────────────────────────────────────────────────
    def _search_semantic(self, query: str, limit: int) -> List[MemoryResult]:
        """Sophia + KI + Doxa + patterns から検索"""
        results = []
        
        # Sophia (外部知識)
        sophia_results = self.sophia.search(query, limit)
        results.extend(sophia_results)
        
        # KI (Knowledge Items)
        ki_results = self.ki_index.search(query, limit)
        results.extend(ki_results)
        
        # Doxa (信念)
        doxa_results = self.doxa_store.search(query, limit)
        results.extend(doxa_results)
        
        # patterns.yaml
        pattern_results = self._search_patterns(query)
        results.extend(pattern_results)
        
        return sorted(results, key=lambda x: x.relevance, reverse=True)[:limit]
    
    # ─────────────────────────────────────────────────
    # Working Memory: 作業記憶
    # ─────────────────────────────────────────────────
    def _search_working(self, query: str, limit: int) -> List[MemoryResult]:
        """Chat context + active task から検索"""
        results = []
        
        # Active task.md
        task_path = self.workspace / ".gemini/antigravity/brain" / self.conversation_id / "task.md"
        if task_path.exists():
            content = task_path.read_text()
            if query.lower() in content.lower():
                results.append(MemoryResult(
                    layer=MemoryLayer.WORKING,
                    source="task",
                    content=content,
                    relevance=0.9,
                    path=task_path
                ))
        
        # Implementation plan
        plan_path = self.workspace / ".gemini/antigravity/brain" / self.conversation_id / "implementation_plan.md"
        if plan_path.exists():
            content = plan_path.read_text()
            if query.lower() in content.lower():
                results.append(MemoryResult(
                    layer=MemoryLayer.WORKING,
                    source="plan",
                    content=content,
                    relevance=0.85,
                    path=plan_path
                ))
        
        return results[:limit]
    
    # ─────────────────────────────────────────────────
    # 全層検索
    # ─────────────────────────────────────────────────
    def _search_all(self, query: str, limit: int) -> List[MemoryResult]:
        """全層を並列検索してマージ"""
        all_results = []
        
        # 各層から検索
        all_results.extend(self._search_episodic(query, limit))
        all_results.extend(self._search_semantic(query, limit))
        all_results.extend(self._search_working(query, limit))
        
        # 関連度でソートして返却
        return sorted(all_results, key=lambda x: x.relevance, reverse=True)[:limit]
```

---

## STAGE 4: Devil's Advocate (Skip - Meso)

| 視点 | 質問 | 回答 |
|:-----|:-----|:-----|
| Feasibility | 既存インデックスで実現可能？ | はい、LanceDB + 既存構造で可能 |
| Necessity | 3層分離の価値は？ | 検索精度向上 + 概念的整理 |

---

## STAGE 5: SE振り返り

```
🔄 KPT
  Keep:    /noe+ の分析結果を直接 API 設計に反映
  Problem: Working Memory のスコープがまだ曖昧
  Try:     P1 で Episodic/Semantic、P2 で Working

⏱️ 時間検証
  所要時間: 6分 / 45分 (13%)
```

---

## 実装計画

| Phase | 内容 | 成果物 |
|:------|:-----|:-------|
| P1 | MemoryLayer enum + retrieve() | memory_api.py |
| P2 | Episodic/Semantic 検索実装 | インデックス統合 |
| P3 | Working Memory 実装 | コンテキスト検索 |
| P4 | 全層統合検索 | マージロジック |

---

*Generated by /s- v5.6 — 2026-01-31*
