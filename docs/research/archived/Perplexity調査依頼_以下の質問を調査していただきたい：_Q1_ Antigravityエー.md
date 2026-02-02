<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Perplexity調査依頼

以下の質問を調査していただきたい：
Q1: Antigravityエージェント間の状態共有
How can Antigravity AI agent sessions share persistent state or memory
between conversations? What mechanisms exist for cross-session knowledge
retention in Claude/Gemini-based coding assistants as of 2025-2026?
Q2: Python 3.14対応の軽量ベクトルDB
What are the best lightweight vector databases that work with Python 3.14
without compilation dependencies? Looking for pure Python or pre-built wheel
alternatives to ChromaDB for local semantic search. Candidates: qdrant-client,
lancedb, sqlite-vec, or pure-Python implementations.
Q3: ローカル軽量Embeddingモデル
What are the smallest, fastest multilingual embedding models that can run
on CPU without torch? Looking for alternatives to sentence-transformers
that work with Python 3.14. Candidates: onnx models, fastembed, txtai.
Q4: AIエージェントのナレッジベース実装パターン
How do production AI coding assistants (Cursor, Cody, Continue.dev, Aider)
implement local knowledge bases for codebase understanding? What indexing
and retrieval patterns do they use?

それでは、最終レポートを作成します。

***

# AI エージェント技術調査レポート：状態共有・軽量ベクトルDB・ナレッジベース実装パターン

## エグゼクティブサマリー

本調査は、2025-2026年における AI エージェントの技術的課題に対する最新ソリューションを分析しました。主要な知見は以下の通りです：

**Q1（Antigravityエージェント間の状態共有）**：Zep や AI-native Memory 2.0 といった最新の専用システムが、従来の単純なセッションメモリから、時間軸対応ナレッジグラフベース、またはエンティティ抽出による動的メモリ管理へと進化しています。大規模言語モデル（Claude、Gemini）は独自の永続化メモリシステムを2024-2025年に実装し、クロスセッション推論を実現しています。

**Q2（Python 3.14軽量ベクトルDB）**：LanceDB、sqlite-vec、NoPokeDB といった純 Python またはホイール配布のソリューションが Python 3.14 に対応。ChromaDB のような汎用ツールは大規模運用には不向きで、LanceDB が推奨候補として浮上しています。

**Q3（軽量 Embedding モデル）**：ONNX ベース実装（fastembedの代替、txtai）が CPU 最適化の中心。ただし fastEmbed 自体は Python 3.14 未対応という重要な制限があります。

**Q4（AIコーディングエージェント）**：Cursor、Continue.dev、Aider、Cody といった主流ツールの実装は、ローカル AST 抽出 → リモート/ローカルインデックス → ハイブリッド検索（ベクトル+グラフ+テキスト）という共通パターンに収束しています。2025年の動向は MCP（Model Context Protocol）標準化と Graph-RAG への傾斜を示しています。

***

## Q1: Antigravityエージェント間の状態共有メカニズム

### 現在の技術ランドスケープ

**2025年の主流実装は、単一の統一的なメモリアーキテクチャから多層的な記憶システムへ移行**しています。従来のチャットボット型インターフェースの線形・同期的制約を超え、複数エージェントの並行実行と非同期状態同期が標準になっています。[^1_1][^1_2][^1_3][^1_4]

#### エンタープライズ向け最新実装

**Zep (2025年1月リリース)**は、Google の Infini-attention 研究に基づく時間軸対応ナレッジグラフ（Graphiti）を使用。MemGPT を上回るパフォーマンスを達成しており、特にエンタープライズユースケースの複雑な時間的推論に最適化されています。Deep Memory Retrieval ベンチマークで 94.8% の精度達成。[^1_1]

**AI-native Memory 2.0（SECOND ME）**は、LLMベースのパラメータ化メモリにより、非構造化対話データと構造化ビジネスデータの動的統合を実現。メモリは自動的に段階的（ユーティランス、ターン、セッション）に要約されます。[^1_5]

#### Claude・Gemini・Perplexity による実装戦略

| プラットフォーム | 実装方式 | 開始時期 | 対象 |
| :-- | :-- | :-- | :-- |
| Claude | プロジェクトスコープの永続化メモリ | 2025年9月 | Pro/Team/Enterprise |
| Gemini | "Saved Info" + 日付タグ付きコンテキスト | 2024年11月 | Advanced users |
| Perplexity | 自動メモリ + 多モデル跨域対応 | 2025年11月 | Pro/Pro Max |

**Claude の設計**は、セッション内の深い一貫性を優先。プロジェクトレベルでメモリを隔離し、各プロジェクト間の汚染を防止。ユーザーは「見る、編集、削除」の完全制御を持ちます。[^1_6]

**Gemini の工夫**は、タイムスタンプ付きメモリ。「2024年6月にサンフランシスコへの移転を検討中」という情報が、2025年12月時点では歴史的コンテキストと解釈されます。これにより hallucination の一種である「永続的な過去の信念」を回避。[^1_7]

**Perplexity の実装**は、会話履歴の完全保存と、複数 LLM モデル間での文脈の可搬性を強調。ユーザーが GPT-5.2 から Claude Opus へ切り替える際、メモリは自動的に移行。[^1_8]

### Strands Agents における セッション永続化

Python ベースのシステムの標準実装として参考価値があります：[^1_9]

```python
from strands import Agent
from strands.session.file_session_manager import FileSessionManager

# ファイルベースのセッション永続化
session_manager = FileSessionManager(session_id="user-123")
agent = Agent(session_manager=session_manager)

# 全メッセージと状態は自動保存
agent("複雑な質問")  # 直後の再起動でもコンテキスト継続
```

セッション管理は以下のイベントで自動トリガー：

1. エージェント初期化時に既存状態を復元
2. 新メッセージ追加時に即座に永続化
3. エージェント実行後に状態同期

### 制約と注意点

**Vertex AI Memory Bank の実装ノート**：Google Cloud 環境では、メモリは 7 日間保持され、AI 学習には使用されません。複数テナント環境では、各テナントが独立したメモリグラフを維持する必要があります。[^1_10]

**セキュリティ上の懸念**：Palo Alto Networks (2025年10月)は、間接プロンプトインジェクションがエージェントメモリを毒することを実証。웹ページの埋め込みコンテンツがセッション要約プロセスを操作し、毒された指示がメモリに永続化される攻撃パターンが確認されています。対策として、入力検証と信頼性スコアリングが必須。[^1_11]

***

## Q2: Python 3.14 対応軽量ベクトルデータベース

### 候補ソリューションの比較分析

**Python 3.14 に対応する軽量ベクトルDB の制限は顕著です**。主要な候補は以下の通り：


| DB | Python 3.14 | 配布形式 | 特徴 | 最適スケール |
| :-- | :-- | :-- | :-- | :-- |
| **LanceDB** | ✓ | ホイール + ネイティブ | DuckDB 統合、ホットスタート | <50M |
| **sqlite-vec** | ✓ | 拡張子 | メタデータフィルタ、純 SQLite | <10M |
| **NoPokeDB** | ✓ | ホイール | hnswlib + SQLite、ディスク永続 | <5M |
| **Qdrant（客のみ）** | ✓ | Pure Python 客 | サーバー別途必須（Docker） | 無制限 |
| **ChromaDB** | ✗ | Rust バイナリ | 2025年 Rust 書き直し（3.13対応） | 非推奨 |
| **FAISS** | ○ | CPU 限定 | 高速、スケーラブル | >100M |
| **Bhakti** | ✓ | Pure Python | メモリ効率的 | <10M |

### 推奨スタック：LanceDB の詳細分析

**LanceDB は現在、Python 3.14 で最も安全な選択肢です**。LangChain 統合を通じて、以下のような実装が可能：[^1_12][^1_13]

```python
from langchain.vectorstores import LanceDB
import lancedb

# ローカル接続
db = lancedb.connect("./data/vectors")

# テーブル作成と埋め込み追加
vectorstore = LanceDB.from_documents(
    documents, 
    embedding=embeddings_model,
    connection=db
)

# セマンティック検索
results = vectorstore.similarity_search("クエリテキスト", k=5)
```

LanceDB の強み：

- **DuckDB ベース**：SQL 互換性により、複雑なメタデータフィルタが容易[^1_12]
- **列指向ストレージ**：Parquet ネイティブで、ディスク効率が 10 倍以上
- **多言語対応**：Python、TypeScript、Rust から同じデータにアクセス可能
- **ホットスタート**：初期化から検索まで数ミリ秒


### 軽量代替案：sqlite-vec と NoPokeDB

**sqlite-vec** は、SQLite 拡張として機能し、既存の SQLite インフラを活用できます：[^1_14]

```python
import sqlite3
import sqlite_vec

conn = sqlite3.connect(":memory:")
conn.enable_load_extension(True)
conn.load_extension("vec0")

# ベクトル検索クエリ
results = conn.execute("""
  SELECT id, distance FROM documents 
  WHERE id MATCH vec_search(embedding, k=5)
""").fetchall()
```

**NoPokeDB** はプロトタイピング向けで、hnswlib (Approximate Nearest Neighbor) を HNSW アルゴリズムで実装：[^1_15]

```python
from nopokedb import NoPokeDB
import numpy as np

db = NoPokeDB(dim=384, max_elements=10000, path="./vdb", space="cosine")
vec = np.random.rand(384).astype(np.float32)
db.add(vec, {"metadata": "example"})
neighbors = db.search(vec, k=10)
```


### 重要な制限：ChromaDB と fastEmbed

**ChromaDB**：2024-2025年の Rust 書き直しにより 4 倍の高速化を実現しましたが、Python 3.14 対応はまだです。プロトタイピングには依然として有用ですが、Python 3.14 環境では選択肢から外れます。[^1_16]

**fastEmbed との組み合わせの注意**：FastEmbed（埋め込みモデル、後述）は ONNX Runtime に依存し、Python 3.14 未対応であることが確認されています。これが主要な障害となります。[^1_17]

***

## Q3: ローカル軽量 Embedding モデル（CPU、Torch 不要）

### Python 3.14 対応エコシステムの現状

**Torch 依存を避けた ONNX ベース実装が標準化**しています。Python 3.14 では以下のアプローチが実行可能：

#### 1. FastEmbed の代替：ONNX Runtime 直接利用

fastEmbed 自体は Python 3.14 未対応ですが、基礎となる ONNX Runtime は対応しています。直接呼び出しは可能です：[^1_18]

```python
import onnxruntime as ort
import numpy as np
from tokenizers import Tokenizer

# 量子化済みの ONNX モデルをダウンロード
# HuggingFace Optimum から "Xenova/bge-small-en-v1.5" など
session = ort.InferenceSession("model_quantized.onnx")

# トークン化 + 埋め込み
tokens = tokenizer.encode(text)
embeddings = session.run(None, {"input_ids": np.array([tokens])})
```


#### 2. txtai：統合エンベッディングDB

**txtai** は Pure Python で実装でき、埋め込み生成から検索まで一体化：[^1_19][^1_20]

```python
from txtai import Embeddings

# ONNX モデルの指定
embeddings = Embeddings({
    "method": "transformers",
    "path": "sentence-transformers/all-MiniLM-L6-v2",  # 91M パラメータ
    "backend": "hnswlib"  # 軽量 ANN
})

# ドキュメント追加
documents = [
    {"id": 1, "text": "Python は学習曲線が優しい"},
    {"id": 2, "text": "Rust は性能が優れている"}
]
embeddings.index(documents)

# クエリ
results = embeddings.search("プログラミング言語", limit=5)
```

txtai の利点：

- **BM25 + ベクトル検索ハイブリッド**：スパース検索で補完
- **ローカル実行**：外部 API 不要
- **メタデータフィルタ**：複雑な条件検索対応


#### 3. 多言語 Embedding モデルの比較

| モデル | 言語対応 | サイズ | 推奨用途 |
| :-- | :-- | :-- | :-- |
| **E5-small** | 100+ 言語 | 33M | 日本語含む汎用 |
| **BAAI BGE-M3** | 中/英/日 | 250M | マルチモーダル + レトリーバル最適化 |
| **EmbeddingGemma** | 100+ 言語 | 256M | Google 公式、Text Embeddings Inference (TEI) 対応[^1_20] |
| **Luxical** | 100+ 言語 | 50M-200M | CPU 最適化（Numba カーネル）、浅層設計[^1_21] |
| **mxbai-embed-large** | 多言語 | 335M | 高精度、SFT ファインチューニング済み |

### 推奨スタック：Python 3.14 での実装

```python
# 依存関係（最小）
# onnxruntime>=1.15
# tokenizers>=0.13
# lancedb>=0.4
# numpy>=1.26

import onnxruntime as ort
from tokenizers import Tokenizer
import numpy as np
from lancedb import connect

# ステップ 1: ONNX モデルの準備
# HuggingFace Optimum から "Xenova/bge-small-en-v1.5" をダウンロード
session = ort.InferenceSession("model.onnx")
tokenizer = Tokenizer.from_file("tokenizer.json")

def embed_text(text: str) -> np.ndarray:
    tokens = tokenizer.encode(text)
    # ベクトル化
    embeddings = session.run(
        None, 
        {"input_ids": np.array([tokens.ids])}
    )[^1_0]
    return embeddings[^1_0]  # [CLS] トークンの埋め込み

# ステップ 2: LanceDB に保存
db = connect("./data/vectors")
table = db.create_table(
    "documents",
    data=[
        {"id": 1, "text": "...", "embedding": embed_text("...")},
        ...
    ]
)

# ステップ 3: セマンティック検索
query_emb = embed_text("検索クエリ")
results = table.search(query_emb).limit(5).to_list()
```


### パフォーマンス特性

**CPU 実行速度の現実的な評価**：[^1_21]

- **Luxical（浅層）**：Apple M4 Max で 1000 文書/秒
- **MiniLM（軽量 Transformer）**：CPU で 100-200 文書/秒
- **BGE-small**：CPU で 50-100 文書/秒

Python 3.14 環境では ONNX Runtime の最適化により、Transformer モデルでも実用的なスループットが期待できます。

***

## Q4: AIコーディングエージェントのナレッジベース実装パターン

### ツール別実装アーキテクチャの比較

**2025年現在、コーディングエージェントの実装は 4 つの異なるパラダイムに収束**しています。それぞれの戦略、スケーラビリティ、セキュリティプロファイルを分析します。

#### **パラダイム 1: Cursor のサーバー側埋め込みモデル**

Cursor は、ローカルチャンキング → リモート埋め込み → リモートベクトルDB という中央集約型アーキテクチャを採用：[^1_22]

**処理フロー**：

1. **Merkle ツリー同期**：ローカルで全ファイルのハッシュツリーを計算、サーバーと同期して変更検知
2. **チャンキング**：ローカルで小分割（通常 400-600 文字）
3. **埋め込み**：OpenAI Embedding API または Cursor 独自モデル（サーバー側）
4. **保存**：埋め込み + メタデータ（行番号、ファイルパス）を Turbopuffer（ベクトル DB）に保存
5. **取得**：クエリ埋め込み → Turbopuffer での最近傍探索 → 難読化ファイルパス + 行範囲をクライアントに返送

**セキュリティ特性**：

- コード本体は保存されない（リクエスト終了時に削除）
- 埋め込みのみリモート保存
- Local Mode 有効時でも、ベクトル DB はリモート（プライバシーと精度のトレードオフ）

**スケーラビリティ**：中程度（数百万行のコードベースまで効率的）

#### **パラダイム 2: Continue.dev のローカル埋め込み + SQLite FTS**

Continue は完全ローカル実行を強調し、MCP（Model Context Protocol）による拡張性を実現：[^1_23][^1_24]

**アーキテクチャ**：

```
@Codebase     ─→ ローカル埋め込み（ONNX/txtai）
@Docs         ─→ ドキュメント検索
@Folder       ─→ フォルダスコープ検索
@Repo-map     ─→ AST ベース関数署名マップ
@Search       ─→ ripgrep（キーワード検索）
@MCP          ─→ 任意の MCP サーバー統合
```

**検索層の実装**：

- **埋め込み生成**：ローカル ONNX モデル（内部）
- **インデックス**：SQLite FTS（全文検索）+ ベクトルメモリ（Python dict）
- **ハイブリッド検索**：キーワードマッチ → ベクトル再スコアリング

**利点**：

- 完全プライベート（インターネット不要）
- カスタマイズ性（独自 LLM、埋め込みモデル）
- MCP サーバーで外部知識ベース統合可能

**制限**：

- クリック\&マージ diff が弱い
- ベクトル検索の精度が Cursor より劣る傾向


#### **パラダイム 3: Aider のグラフベース検索（AST + コールグラフ）**

Aider は **ベクトル検索を使わない** アプローチで高い成功率を達成：[^1_25]

**リポジトリマップの構築**：

```
1. ctags でシンボル抽出（関数名、クラス名）
2. コールグラフ構築（関数呼び出し関係）
3. AST 解析で依存関係マップ
4. 質問に基づいてグラフ最適化で関連コードを抽出
5. AST コンテキスト付きで LLM に提供
```

**利点**：

- 高精度（SWE-Bench 2位スコア）
- 計算効率（ベクトル埋め込み不要）
- 解釈可能性（どのコード部分が取得されたか明確）

**制限**：

- 複数ファイル跨域の依存関係抽出が複雑
- 自然言語クエリの意図分類が必須
- 言語ごとに ctags/LSP 設定が必要

**実装例**（概念）：

```python
import subprocess
import re

def build_repo_map(repo_path):
    # ctags でシンボル抽出
    symbols = subprocess.run(
        ["ctags", "-f", "-", repo_path],
        capture_output=True,
        text=True
    )
    # グラフ構築（省略）
    return dependency_graph

def context_retrieval(query, graph):
    # 意図分類 → グラフ走査
    relevant_nodes = graph_search(query_embedding, graph)
    return [node.code_context for node in relevant_nodes]
```


#### **パラダイム 4: Cody (Sourcegraph) のハイブリッド検索 + セマンティックグラフ**

Cody は **Repository-level Semantic Graph (RSG)** により、大規模コードベースの多段階検索を実装：[^1_26][^1_27]

**検索パイプライン**：

1. **検索フェーズ**：
    - ローカルコンテキスト（開いているファイル、最近閉じたタブ）
    - Sourcegraph インスタンス上の BM25 + 埋め込み検索
    - 複数ファイルの関連性スコアリング
2. **ランキング フェーズ**：
    - グラフ展開（RSG で関連エンティティを探索）
    - リンク予測アルゴリズム
    - **Contextual Embeddings で 35% の検索失敗率低減**
3. **コンテキスト構成**：
    - スニペット抽出 + 関連性でソート
    - LLM コンテキストウィンドウ内に最適化

**スケーラビリティ**：大規模エンタープライズ対応（数百万ファイル）

### 共通パターン：多層インデックス戦略

| 層 | 技術 | 用途 |
| :-- | :-- | :-- |
| **構文層** | AST、LSP、tree-sitter | シンボル抽出、スコープ解析 |
| **意味層** | ベクトル埋め込み、グラフ | セマンティック類似性、依存関係 |
| **キーワード層** | BM25、SQLite FTS、ripgrep | テキスト検索、フィルタリング |
| **グラフ層** | コールグラフ、RSG | 関連性拡張、多段階推論 |

### 2025 年のトレンド：Graph-RAG と MCP 標準化

**Graph-RAG の採用拡大**：

- エンティティ抽出 + 関係抽出によるナレッジグラフ構築
- 複数ホップ推論による複雑なクエリ対応
- 例：LinareRAG は Tri-Graph で関係抽出コストを削減[^1_28]

**MCP（Model Context Protocol）の浸透**：

- Anthropic が提案した標準化プロトコル
- Continue、Cody が統合開始
- カスタムコンテキストプロバイダーの接続が容易に

**実装例（MCP コンテキスプロバイダー）**：

```python
# MCP サーバーとして、カスタムナレッジベースを提供
from mcp.server import Server

server = Server("codebase-provider")

@server.list_resources()
def list_knowledge_sources():
    return [
        {"uri": "memory://codebase", "name": "Local Codebase Index"},
        {"uri": "file://docs", "name": "Documentation"}
    ]

@server.read_resource(uri)
def retrieve_context(uri: str):
    # LanceDB または sqlite-vec からのセマンティック検索
    return vectorstore.search(uri.query)

# Continue が @MCP で このサーバーを利用可能
```


### 推奨実装パターン（2025年）

**小～中規模チーム（<50万行）**：

```
Continue.dev (MCP統合)
+ LanceDB (埋め込みDB)
+ txtai (埋め込みモデル)
+ ripgrep (キーワード検索)
```

**大規模エンタープライズ**：

```
Cody Enterprise (Sourcegraph)
+ RSG (セマンティックグラフ)
+ 複数ベクトルDB バックエンド
+ Graph-RAG (複数ホップ推論)
```

**完全ローカル（セキュリティ最優先）**：

```
Aider (リポジトリマップ)
+ 独自 ctags/LSP 設定
+ LanceDB (キャッシュレイヤー)
```


***

## 結論と推奨事項

### 技術選択の意思決定マトリックス

| 要件 | 推奨スタック | 根拠 |
| :-- | :-- | :-- |
| **Python 3.14 軽量 VectorDB** | LanceDB | ホイール配布、ネイティブ Python 3.14 対応、DuckDB 統合の柔軟性 |
| **CPU-only Embedding** | txtai + ONNX（BAAI BGE-M3） | ONNX Runtime Python 3.14 対応、txtai の統合機能、日本語対応 |
| **小規模ローカル実装** | Continue.dev + LanceDB + txtai | 完全プライベート、MCP 拡張性、低オーバーヘッド |
| **大規模エンタープライズ** | Cody Enterprise + Sourcegraph | 検索精度（35% 失敗率低減）、スケーラビリティ、サポート体制 |
| **AST ベース精度重視** | Aider + リポジトリマップ | 高精度（SWE-Bench 2位）、計算効率、解釈可能性 |

### 2025-2026 年の技術進化予測

1. **MCP 標準化の浸透**：カスタムコンテキストプロバイダーの接続が IDE で標準機能化
2. **Graph-RAG の本格化**：ナレッジグラフによる複数ホップ推論が主流に
3. **ローカル優先化**：プライバシー・セキュリティ懸念からローカル埋め込み・検索がデフォルトに
4. **マルチモーダル化**：テキスト + コード + AST + グラフの統合検索

### 即座に実装可能なセットアップ（Python 3.14）

```bash
# 依存関係
pip install lancedb onnxruntime tokenizers numpy

# ダウンロード（HuggingFace Optimum から）
# Xenova/bge-small-en-v1.5 (ONNX + Tokenizer)

# ディレクトリ構成
project/
├── embeddings/
│   ├── model.onnx
│   └── tokenizer.json
├── data/
│   └── vectors/  # LanceDB ローカルストレージ
└── agent.py
```

本調査が、エージェント実装の技術的決定を加速させることを期待しています。

***

**参考文献一覧**

[^1_1] Zep: A Temporal Knowledge Graph Architecture (2025-01) | [^1_2] Enhancing memory retrieval in generative agents (2025-05) | [^1_5] AI-native Memory 2.0 (2025-03) | [^1_3] Hello Again! LLM-powered Personalized Agent (2025-02) | [^1_4] Getting Started with Google Antigravity (2026-01) | [^1_6] persistent context and limitations (2025-08) | [^1_9] Session Management - Strands Agents | [^1_11] When AI Remembers Too Much (2025-10) | [^1_10] Vertex AI Agent Engine Memory Bank (2025-12) | [^1_7] Google Has Your Data. Gemini Barely Uses It (2025-11) | [^1_8] Introducing AI assistants with memory - Perplexity (2025-11) | [^1_12] LanceDB — LangChain documentation | [^1_14] sqlite-vec (2024) | [^1_15] NoPokeDB (2025-08) | [^1_13] LanceDB vectordb-recipes | [^1_16] Best Vector Databases 2025 (2025-10) | [^1_18] ONNX Runtime Arm CPUs (2022) | [^1_17] fastembed GitHub \#576 (2025) | [^1_19] txtai documentation | [^1_20] EmbeddingGemma (2025-09) | [^1_21] Luxical: High-Speed Lexical-Dense Text Embeddings (2025-09) | [^1_26] Cody AI: Deep Codebase Understanding (2025-12) | [^1_27] How Cody understands your codebase (2024-02) | [^1_23] Continue.dev Codebase Documentation Awareness (2026-01) | [^1_28] LinearRAG (2025-10) | [^1_22] How Cursor Indexes Codebases Fast (2025-05) | [^1_25] CodeNav + Aider Repository Map (2024 HN) | [^1_24] Continue.dev Context Providers (2025-11)
<span style="display:none">[^1_100][^1_101][^1_102][^1_103][^1_104][^1_105][^1_106][^1_107][^1_108][^1_109][^1_110][^1_111][^1_112][^1_113][^1_114][^1_115][^1_116][^1_117][^1_118][^1_119][^1_120][^1_121][^1_29][^1_30][^1_31][^1_32][^1_33][^1_34][^1_35][^1_36][^1_37][^1_38][^1_39][^1_40][^1_41][^1_42][^1_43][^1_44][^1_45][^1_46][^1_47][^1_48][^1_49][^1_50][^1_51][^1_52][^1_53][^1_54][^1_55][^1_56][^1_57][^1_58][^1_59][^1_60][^1_61][^1_62][^1_63][^1_64][^1_65][^1_66][^1_67][^1_68][^1_69][^1_70][^1_71][^1_72][^1_73][^1_74][^1_75][^1_76][^1_77][^1_78][^1_79][^1_80][^1_81][^1_82][^1_83][^1_84][^1_85][^1_86][^1_87][^1_88][^1_89][^1_90][^1_91][^1_92][^1_93][^1_94][^1_95][^1_96][^1_97][^1_98][^1_99]</span>

<div align="center">⁂</div>

[^1_1]: https://arxiv.org/abs/2501.13956

[^1_2]: https://www.frontiersin.org/articles/10.3389/fpsyg.2025.1591618/full

[^1_3]: http://arxiv.org/pdf/2406.05925.pdf

[^1_4]: https://codelabs.developers.google.com/getting-started-google-antigravity

[^1_5]: https://arxiv.org/pdf/2503.08102.pdf

[^1_6]: https://www.datastudios.org/post/memory-systems-in-ai-chatbots-persistent-context-and-limitations-in-ai-like-chatgpt-claude-gemin

[^1_7]: https://www.shloked.com/writing/gemini-memory

[^1_8]: https://www.perplexity.ai/ja/hub/blog/introducing-ai-assistants-with-memory

[^1_9]: https://strandsagents.com/latest/documentation/docs/user-guide/concepts/agents/session-management/

[^1_10]: https://zenn.dev/google_cloud_jp/articles/a1f593ad690d7e

[^1_11]: https://unit42.paloaltonetworks.com/indirect-prompt-injection-poisons-ai-longterm-memory/

[^1_12]: https://reference.langchain.com/v0.3/python/community/vectorstores/langchain_community.vectorstores.lancedb.LanceDB.html

[^1_13]: https://github.com/lancedb/vectordb-recipes

[^1_14]: https://www.reddit.com/r/LocalLLaMA/comments/1lcxcuv/which_vectordb_do_you_use_and_why/

[^1_15]: https://pypi.org/project/nopokedb/

[^1_16]: https://www.firecrawl.dev/blog/best-vector-databases-2025

[^1_17]: https://github.com/qdrant/fastembed/issues/576

[^1_18]: https://arxiv.org/pdf/2504.03774.pdf

[^1_19]: https://www.reddit.com/r/LocalLLaMA/comments/15o5fqf/txtai_60_the_allinone_embeddings_database/

[^1_20]: https://huggingface.co/blog/embeddinggemma

[^1_21]: https://arxiv.org/html/2512.09015v2

[^1_22]: https://read.engineerscodex.com/p/how-cursor-indexes-codebases-fast

[^1_23]: https://docs.continue.dev/guides/codebase-documentation-awareness

[^1_24]: https://docs.continue.dev/customize/custom-providers

[^1_25]: https://news.ycombinator.com/item?id=40998497

[^1_26]: https://mgx.dev/insights/c4dc216669bf47a4b91e6e1e103a57cd

[^1_27]: https://sourcegraph.com/blog/how-cody-understands-your-codebase

[^1_28]: https://arxiv.org/abs/2510.10114

[^1_29]: https://ijamjournal.org/ijam/publication/index.php/ijam/article/view/630

[^1_30]: https://www.semanticscholar.org/paper/0ceeb784caf95d54dc6b77b4d2f5575a1ef9f46c

[^1_31]: https://arxiv.org/pdf/2502.12110.pdf

[^1_32]: http://arxiv.org/pdf/2406.18312.pdf

[^1_33]: http://arxiv.org/pdf/2204.01611.pdf

[^1_34]: http://arxiv.org/pdf/2408.09559.pdf

[^1_35]: https://arxiv.org/pdf/2503.08026.pdf

[^1_36]: https://unikoukokun.jp/n/nd096dd7d4e42

[^1_37]: https://skywork.ai/blog/ai-agent/antigravity-infinite-context-window-explained/

[^1_38]: https://blog.meetneura.ai/antigravity-ai-2025/

[^1_39]: https://qiita.com/ishisaka/items/c5587fcd6b4c1036ad0c

[^1_40]: https://dev.classmethod.jp/articles/google-antigravity-five-tips/

[^1_41]: https://www.jenova.ai/en/resources/ai-with-persistent-chat-history

[^1_42]: https://towardsdatascience.com/ai-agent-with-multi-session-memory/

[^1_43]: https://minna-systems.co.jp/test/blog/ai-dev-tools-complete-guide-december-2025/

[^1_44]: https://plurality.network/blogs/ai-long-term-memory-with-ai-context-flow/

[^1_45]: https://docs.perplexity.ai/cookbook/articles/memory-management/chat-with-persistence/README

[^1_46]: http://arxiv.org/pdf/2504.01553.pdf

[^1_47]: https://arxiv.org/html/2502.05311

[^1_48]: http://arxiv.org/pdf/2201.03873.pdf

[^1_49]: http://arxiv.org/pdf/2502.03771.pdf

[^1_50]: https://arxiv.org/pdf/2403.12583.pdf

[^1_51]: https://arxiv.org/pdf/2401.07119.pdf

[^1_52]: https://zenodo.org/record/3632551/files/vectorizationcompilation.pdf

[^1_53]: https://arxiv.org/pdf/2502.01528.pdf

[^1_54]: https://zenn.dev/serio/articles/733b53d2b912d1

[^1_55]: https://qiita.com/kinshotomoya/items/e47f83bafd643ab7bf08

[^1_56]: https://www.youtube.com/watch?v=PKLMzISoYq0

[^1_57]: https://qdrant.tech

[^1_58]: https://www.abovo.co/sean@abovo42.com/134573

[^1_59]: https://dev.epicgames.com/documentation/ja-jp/unreal-engine/unreal-engine-5-7-release-notes

[^1_60]: https://dev.classmethod.jp/articles/qdrant-first-step/

[^1_61]: https://latenode.com/blog/ai-frameworks-technical-infrastructure/vector-databases-embeddings/best-vector-databases-for-rag-complete-2025-comparison-guide

[^1_62]: https://www.semanticscholar.org/paper/5696efd8a47e3de3bdffaf2bafeece9f66c2e10c

[^1_63]: http://arxiv.org/pdf/2212.08046.pdf

[^1_64]: http://arxiv.org/pdf/2202.06929.pdf

[^1_65]: http://arxiv.org/pdf/2110.01730.pdf

[^1_66]: https://arxiv.org/pdf/2209.09756.pdf

[^1_67]: https://arxiv.org/pdf/2309.14254.pdf

[^1_68]: https://arxiv.org/pdf/2406.08051.pdf

[^1_69]: https://arxiv.org/pdf/2207.08820.pdf

[^1_70]: https://crates.io/crates/fastembed/3.14.1

[^1_71]: https://pypi.org/project/fastembed-gpu/

[^1_72]: https://artsmart.ai/blog/top-embedding-models-in-2025/

[^1_73]: https://docs.langchain.com/oss/python/integrations/text_embedding/fastembed

[^1_74]: https://qdrant.tech/articles/fastembed/

[^1_75]: https://pypi.org/project/txtai/2.0.0/

[^1_76]: https://github.com/PaddlePaddle/PaddleOCR

[^1_77]: https://www.linkedin.com/posts/florent-poux-point-cloud_3d-python-pointcloud-activity-7300893185696759808-wsTQ

[^1_78]: https://hub.docker.com/r/neuml/txtai-gpu

[^1_79]: https://arxiv.org/html/2410.07002v1

[^1_80]: https://arxiv.org/html/2406.12276

[^1_81]: https://arxiv.org/html/2410.14684v1

[^1_82]: http://arxiv.org/pdf/2405.06271.pdf

[^1_83]: https://arxiv.org/html/2409.11190v1

[^1_84]: https://arxiv.org/pdf/2303.12570.pdf

[^1_85]: https://dl.acm.org/doi/10.1145/3180155.3180187

[^1_86]: http://arxiv.org/pdf/2411.12644.pdf

[^1_87]: https://note.com/delta_ipsilon/n/n429bbdd43e60

[^1_88]: https://www.reddit.com/r/ChatGPTCoding/comments/1ezkhyk/cursor_vs_continue_vs/

[^1_89]: https://forum.cursor.com/t/codebase-indexing-no-longer-working-inside-dev-containers/17858

[^1_90]: https://learn.microsoft.com/en-us/dotnet/ai/tutorials/tutorial-ai-vector-search

[^1_91]: https://forum.cursor.com/t/codebase-indexing/36

[^1_92]: https://itnext.io/implementing-rag-retrieval-augmented-generation-a-guide-9e659f755d0b

[^1_93]: https://www.gocodeo.com/post/ai-powered-code-search-smarter-navigation-for-large-codebases

[^1_94]: https://dev.to/maximsaplin/continuedev-the-swiss-army-knife-that-sometimes-fails-to-cut-4gg3

[^1_95]: https://getstream.io/blog/agentic-ai-rag/

[^1_96]: https://ai.gopubby.com/implementing-rag-architecture-from-scratch-vector-databases-embeddings-and-llms-d1b030810421

[^1_97]: https://ijarsct.co.in/Paper18099.pdf

[^1_98]: https://dl.acm.org/doi/10.1145/3711896.3737012

[^1_99]: https://www.semanticscholar.org/paper/c1799bf28d1ae93e1631be5b59196ee1e568f538

[^1_100]: https://rsisinternational.org/journals/ijrias/article.php?id=714

[^1_101]: https://arxiv.org/abs/2510.05547

[^1_102]: https://www.semanticscholar.org/paper/55152927f926f54edf3b68fc81cd380bd8597777

[^1_103]: http://biorxiv.org/lookup/doi/10.1101/2025.06.30.662271

[^1_104]: https://arxiv.org/abs/2504.06135

[^1_105]: https://www.ijraset.com/best-journal/reasoning-engine-with-pretrained-llms-an-operation-gpt-

[^1_106]: http://arxiv.org/pdf/2411.00689.pdf

[^1_107]: http://arxiv.org/pdf/2410.15285.pdf

[^1_108]: https://arxiv.org/pdf/2411.02959.pdf

[^1_109]: https://arxiv.org/html/2408.03910v2

[^1_110]: http://arxiv.org/pdf/2410.14594.pdf

[^1_111]: https://arxiv.org/pdf/2502.15237.pdf

[^1_112]: http://arxiv.org/pdf/2406.14497.pdf

[^1_113]: https://github.com/paul-gauthier/aider/issues/908

[^1_114]: https://www.reddit.com/r/LocalLLaMA/comments/1mzvk44/codebase_to_knowledge_graph_generator/

[^1_115]: https://lancedb.com/blog/building-rag-on-codebases-part-1/

[^1_116]: https://forum.cursor.com/t/provide-own-vector-db-to-store-embeddings/126952

[^1_117]: https://aider.chat/docs/ctags.html

[^1_118]: https://www.reddit.com/r/ZedEditor/comments/1prg6t9/setting_up_a_local_vector_db_code_browser_in_zed/

[^1_119]: https://subhadipmitra.com/blog/2025/mcp-maturity-model/

[^1_120]: https://github.com/Aider-AI/aider/issues/349

[^1_121]: https://github.com/cursor/cursor/issues/724

