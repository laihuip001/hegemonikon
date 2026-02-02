# Perplexity 調査結果: Sophia 知識グラフ実装

> **調査日**: 2026-01-28
> **ソース**: Perplexity Deep Research

---

## 結論サマリー

| Phase | 実装項目 | 期間 | 技術 |
|:------|:---------|:-----|:-----|
| 1 | バックリンク検出 | 1-2週 | NetworkX + 正規表現 |
| 2 | グラフビュー | 3-4週 | D3 v7 → Pixi.js |
| 3 | HybridRAG | 6-8週 | sentence-transformers + Neo4j |

---

## Phase 1: バックリンク検出

```python
class SophiaBacklinker:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.cache = {}  # {note: {outlinks, backlinks, hash}}
    
    def extract_links(self, note_path: str) -> Set[str]:
        """[[wikilink]] パターン抽出"""
        return set(re.findall(r'\[\[([^\]]+)\]\]', content))
    
    def get_backlinks(self, note_name: str) -> Set[str]:
        """O(1) バックリンク検索"""
        return set(self.graph.predecessors(note_name))
```

**性能**: 10k ノート @ メモリ内可 (~500MB), O(1) 検索

---

## Phase 2: グラフビュー

| ノード数 | 技術 | FPS |
|:---------|:-----|:----|
| ≤1k | SVG (D3) | 60 |
| 1k-5k | Canvas (D3) | 45 |
| 5k-100k | Pixi.js + WebGL | 60 |
| 100k+ | Cosmos.gl | 60 |

---

## Phase 3: HybridRAG

```
HybridRAG = VectorRAG + GraphRAG

評価結果 (arXiv:2408.04948):
- Faithfulness: 95.2% (HybridRAG) vs 72.1% (VectorRAG)
- Answer Relevancy: 92.8%
- Context Recall: 89.4%
```

---

## 根拠リンク

- [HybridRAG 論文](https://arxiv.org/abs/2408.04948) (2024)
- [RGL Framework](https://arxiv.org/html/2503.19314) (2025)
- [Cosmos.gl](https://openjsf.org/blog/introducing-cosmos-gl/) (2025)
- [D3 + Pixi.js](https://graphaware.com/blog/scale-up-your-d3-graph-visualisation-webgl-canvas-with-pixi-js/)
