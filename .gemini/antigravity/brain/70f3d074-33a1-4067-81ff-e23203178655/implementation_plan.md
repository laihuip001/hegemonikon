# HybridSearch プロトタイプ計画

## 目的

Sophia ベクトル検索結果にバックリンクグラフの情報を統合し、**関連 KI を含む結果をブースト**する HybridSearch を実装する。

---

## STAGE 0: Blindspot + Scale

| カテゴリ | 盲点 | リスク |
|:---------|:-----|:------:|
| Framing | 「Hybrid」の定義が曖昧？ | 中 |
| Scope | Ranker 全体を書き換え？ | 低 — 追加レイヤーのみ |
| Dependencies | sophia_backlinker との統合 | 低 — 既に to_dict() あり |
| Performance | グラフ探索のコスト | 低 — O(1) キャッシュ済み |

**📏 Scale: 🔭 Meso** — 複数ファイル変更、新クラス追加

### 「Hybrid」の定義

**arXiv:2408.04948** の HybridRAG パターン:
> ベクトル類似度 + グラフ隣接関係 を組み合わせてリランキング

**Hegemonikón 実装**:
> 検索結果に「バックリンク元」を追加し、関連度スコアをブースト

---

## STAGE 1: Strategy

### Explore/Exploit 判定

| 軸 | 判定 |
|:---|:-----|
| 失敗コスト | 低 (検索品質改善) |
| 環境確実性 | 中 (新しいランキングロジック) |
| 時間制約 | 余裕あり |

**判定: Explore** — 新しいアプローチだが、低リスク

### 3プラン

| Plan | 概要 | リスク |
|:-----|:-----|:-------|
| A: Conservative | Ranker に backlink boost 追加 | 最小 ← **推奨** |
| B: Robust | HybridRanker クラス新規作成 | 工数中 |
| C: Aggressive | GraphRAG 完全実装 | 過剰 |

**選択: Plan A**

---

## STAGE 2: Success Criteria

| 軸 | Must | Should |
|:---|:-----|:-------|
| 機能 | バックリンクでスコアブースト | ブースト量を調整可能 |
| 品質 | 既存テストが通る | 新規テスト追加 |
| 性能 | 検索応答 < 2秒 | N/A |

---

## STAGE 3: Blueprint

### Goal Decomposition

```text
最終目標: HybridSearch — ベクトル + グラフ統合
  ← サブ1: Ranker.rank() にバックリンクブースト引数追加
  ← サブ2: SearchEngine.search() でバックリンカー連携
  ← 現在地: 独立した sophia_backlinker
```

### 設計詳細

```python
# ranker.py の変更
class Ranker:
    def rank(
        self,
        source_results: Dict[str, List[IndexedResult]],
        weights: Dict[str, float],
        backlink_boost: Optional[Dict[str, float]] = None,  # NEW
    ) -> List[IndexedResult]:
        ...
        # バックリンクブースト適用
        if backlink_boost and result.doc_id in backlink_boost:
            weighted_score *= (1 + backlink_boost[result.doc_id])
        ...

# engine.py の変更
class SearchEngine:
    def __init__(self, ..., backlinker: Optional[SophiaBacklinker] = None):
        self._backlinker = backlinker
    
    def search(self, query, ...):
        ...
        # バックリンクブースト計算
        if self._backlinker:
            backlink_boost = self._compute_backlink_boost(results)
        ...
```

### 変更対象

| ファイル | 変更概要 |
|:---------|:---------|
| `search/ranker.py` | backlink_boost 引数追加 |
| `search/engine.py` | backlinker 連携 |
| `tests/test_search.py` | HybridSearch テスト追加 |

---

## STAGE 4: Devil's Advocate

| 視点 | 結果 |
|:-----|:-----|
| Feasibility | ✅ PASS — 既存コードの拡張 |
| Necessity | ⚠️ 要検討 — 11ノードでは効果薄い？ |
| Risks | ✅ PASS — 後方互換性維持 (オプション引数) |

### Pre-mortem

1. **バックリンクがない KI** — 対策: ブースト = 0 (無影響)
2. **過剰ブースト** — 対策: boost 係数を 0.1-0.5 に制限

---

## 検証計画

1. 既存テスト通過確認
2. バックリンク付き KI が上位に来るか確認
3. ブースト係数調整実験
