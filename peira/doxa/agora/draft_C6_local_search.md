# 日本語セマンティック検索をローカルで動かす

> **ID**: C6
> **想定媒体**: Zenn（技術記事）
> **想定読者**: NLP エンジニア、Agent 開発者
> **フック**: GPU なし + pip install だけで日本語セマンティック検索

---

## リード文（案）

「日本語のセマンティック検索」と聞くと、
OpenAI の Embeddings API か、GPU マシンを想像するだろう。

**両方不要。** BGE-small + janome + hnswlib で、ローカル CPU だけで動く。

---

## 本文構成（案）

### 1. 技術スタック

| コンポーネント | ライブラリ | 役割 |
|:-------------|:---------|:-----|
| 埋め込み | BGE-small-en-v1.5 | テキスト→384次元ベクトル |
| 推論 | ONNX Runtime | CPU で高速推論 |
| 日本語前処理 | janome | 形態素解析 |
| ベクトル検索 | hnswlib | ANN (近似最近傍) |

### 2. 日本語前処理のポイント

```python
def preprocess_ja(text: str) -> str:
    """BGE-small の WordPiece トークナイザのために形態素分解"""
    tokens = janome.tokenize(text)
    content_words = [t for t in tokens 
                     if t.pos in {'名詞', '動詞', '形容詞'}]
    return ' '.join(w.base_form for w in content_words)
```

- BGE-small は英語モデルだが、日本語でも使える
- janome で意味のある単語単位に分割してから埋め込む
- 機能語（助詞、助動詞）を除外すると精度向上

### 3. VectorStore アダプタ設計

```python
class VectorStoreAdapter(ABC):
    def create_index(self, dimension: int): ...
    def add_items(self, vectors, ids, metadata): ...
    def search(self, query_vector, k): ...

class HNSWAdapter(VectorStoreAdapter): ...
class FaissAdapter(VectorStoreAdapter): ...
class SQLiteVSSAdapter(VectorStoreAdapter): ...
```

Factory パターンで切り替え可能。

### 4. パフォーマンス

| データ量 | 検索速度 | メモリ |
|:---------|:---------|:-------|
| 1,000 docs | ~5ms | ~50MB |
| 10,000 docs | ~10ms | ~200MB |
| 34,000 docs | ~20ms | ~500MB |

### 5. 失敗と教訓

- 最初は LanceDB → 依存が重い → hnswlib に移行
- janome の遅延初期化が重要（最初の呼び出しに数秒）
- ONNX Runtime の providers 指定を忘れると GPU を探して失敗

### 6. 読者が試せること

```bash
pip install onnxruntime janome hnswlib
# BGE-small ONNX モデルをダウンロード
# 10 行のコードでセマンティック検索
```

---

*ステータス: たたき台*
*関連: C1 (4層メモリ), C11 (VectorDB抽象化)*
