# VectorDB アダプタの抽象化設計 — Symploke

> **ID**: C11
> **想定媒体**: Zenn（技術記事）
> **想定読者**: Python エンジニア、設計パターン好き
> **フック**: hnswlib → faiss → sqlite-vss を1行で切り替える設計

---

## リード文（案）

最初は hnswlib で始めた。次に faiss を試した。sqlite-vss も候補に。

VectorDB を切り替えるたびに全コードを書き直すのは地獄だ。
**Factory + ABC パターン**で、1行の設定変更で切り替え可能にした。

---

## 本文構成（案）

### 1. 問題

```python
# ❌ Before: hnswlib に直結
import hnswlib
index = hnswlib.Index(space='cosine', dim=384)
index.init_index(max_elements=10000)
```

### 2. 解決: アダプタパターン

```python
# ✅ After: 抽象化
class VectorStoreAdapter(ABC):
    @abstractmethod
    def create_index(self, dimension: int): ...
    @abstractmethod
    def add_items(self, vectors, ids): ...
    @abstractmethod
    def search(self, query, k): ...

class VectorStoreFactory:
    @staticmethod
    def create(adapter: str) -> VectorStoreAdapter:
        if adapter == 'hnswlib': return HNSWAdapter()
        if adapter == 'faiss': return FaissAdapter()
        if adapter == 'sqlite-vss': return SQLiteVSSAdapter()
```

### 3. 使い方

```python
# config で切り替え
store = VectorStoreFactory.create('hnswlib')
store = VectorStoreFactory.create('faiss')  # 1行変更
```

### 4. 各アダプタの特性

| アダプタ | 速度 | メモリ | 永続化 | 向き |
|:---------|:-----|:-------|:-------|:-----|
| hnswlib | ◎ | △ | ファイル | RAM 余裕あり |
| faiss | ◎ | ○ | ファイル | GPU 活用時 |
| sqlite-vss | ○ | ◎ | DB | 永続化重視 |

### 5. 学んだこと

- ABCの`@abstractmethod`で「実装漏れ」をコンパイル時に検出
- Factory は `config: dict` を受け取る形にすると柔軟
- テストは ABC の interface テスト + 各アダプタの integration テスト

---

*ステータス: たたき台*
*関連: C6 (ローカル検索), C1 (4層メモリ)*
