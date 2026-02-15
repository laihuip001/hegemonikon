# C1: 消化メトリクス・ダッシュボード

> **ステータス**: 設計段階 (2026-02-15)
> **依存**: B3 (/eat v3.1 半自動化) + Desktop Sprint

---

## 概要

過去の /eat 実行結果 (η/ε/Drift/分類) を時系列で可視化し、
HGK Desktop ダッシュボードに統合する。

---

## アーキテクチャ

```mermaid
graph LR
    A["/eat 実行"] --> B["JSON ログ出力"]
    B --> C["mekhane/api/routes/digestion.py"]
    C --> D["Dashboard digestion-card.ts"]
```

### データモデル

```python
@dataclass
class DigestionRecord:
    timestamp: str          # ISO 8601
    source: str             # 論文タイトル or URL
    eta: float              # 情報保存率 η
    epsilon: float          # 構造回復率 ε
    drift: float            # 1 - ε
    level: str              # Naturalized / Absorbed / Superficial
    mode: str               # manual / semi-auto
```

### API エンドポイント

| エンドポイント | メソッド | 説明 |
|:-------------|:--------|:-----|
| `/digestion/history` | GET | 過去の消化記録一覧 |
| `/digestion/stats` | GET | 平均 η/ε、消化レベル分布 |

### Dashboard カード

- 直近10件の η/ε をミニスパークラインで表示
- 消化レベル分布 (Nat/Abs/Sup) のドーナツチャート
- ドリフト傾向の折れ線グラフ

---

## 実装見積り

| 作業 | 見積り |
|:-----|:-------|
| JSON ログ出力 (/eat Phase 3 に hook) | 30min |
| API エンドポイント | 30min |
| Dashboard カード | 1h |
| **合計** | **2h** |

---

## 前提条件

- B3 完了後、/eat が η/ε を出力する仕組みが稼働していること
- Desktop Sprint が安定していること
