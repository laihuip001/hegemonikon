# Symplokē Unified Knowledge Layer

## 概要

**Symplokē (統合知識層)** は、Hegemonikón における多様な知識ドメイン（Gnōsis, Mnēmē, Kairos, Chronos）を統合し、統一的なインターフェースで提供するためのインフラ層である。

## 主要コンポーネント

### 1. アダプタ層 (Adapters)

- **VectorStoreAdapter**: ベクトルDBの抽象界面。
- **実装**: HNSWLib, FAISS, SQLite-VSS, LanceDB 対応。

### 2. インデックス管理 (Indices)

- **GnosisIndex**: アカデミック・技術論文。
- **KairosIndex**: 実装・ハンドオフ・コンテキスト。
- **SophiaIndex**: 概念・真理（Sophia）。
- **ChronosIndex**: 会話履歴・エピソード記憶。

### 3. 検索／抽出ロジック

- **Hybrid Search**: ベクトル検索と全文検索の統合。
- **Specialists**: 特定ドメインに特化した専門家プロンプトと抽出ロジックの管理。

## 必然性の証明 (PROOF)

- **A0 (FEP)**: 多様な感覚入力を単一の内部モデルに統合する必要がある。
- **演繹**: 異なるソースからの知識を共通のベクトル空間に投影し、文脈に応じて呼び出す「結合装置（Symplokē）」が不可欠である。

## ディレクトリ構造

```
mekhane/symploke/
├── adapters/        # ベクトルDBアダプタ
├── indices/         # 各ドメインのインデックスロジック
├── search/          # 検索エンジン統合
├── config.py        # 統合設定
└── factory.py       # アダプタ生成ファクトリ
```

---
*Status: Production | Managed by: mekhane/symploke*
