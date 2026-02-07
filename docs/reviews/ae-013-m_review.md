# AE-013.M Simplicity Gatekeeper (Macro) レビュー

## 対象
`mekhane/symploke/` ディレクトリ全体

## 概要
本モジュールは全体的にコード量が多く、静的データ定義とロジックが混在しています。また、開発初期の遺産と思われる重複スクリプトやハードコードされたパスが散見されます。YAGNI原則に基づき、不要な複雑さを排除するための改善点を指摘します。

## 発見事項

### 1. 重複・冗長なスクリプト
- **ファイル**: `mekhane/symploke/run_remaining.py`
  - **内容**: `run_specialists.py` と機能が重複しており、ハードコードされたパスや古いロジックが含まれています。
  - **推奨**: **削除**。`run_specialists.py` に統合されている機能であり、メンテナンスコストのみが増大しています。

### 2. レガシーコードと非推奨機能
- **ファイル**: `mekhane/symploke/jules_client.py`
  - **内容**: `parse_state` 関数は "Legacy alias" と明記されています。内部利用のみであれば、呼び出し元を修正して削除すべきです。
  - **推奨**: **削除**し、`SessionState.from_string` を直接使用する。

### 3. デッドコード / コメントアウトされたコード
- **ファイル**: `mekhane/symploke/factory.py`
  - **内容**: `_register_adapters` 内にコメントアウトされた `faiss` アダプタ登録コードがあります。
  - **推奨**: **削除**。バージョン管理システムがあれば、コードに履歴を残す必要はありません。

### 4. 過剰な抽象化 (Factory Pattern)
- **ファイル**: `mekhane/symploke/factory.py`
  - **内容**: `VectorStoreFactory` がありますが、現状 `hnswlib` しか有効化されておらず、他のアダプタは実装されていないかコメントアウトされています。
  - **推奨**: 現状はYAGNI。直接 `HNSWlibAdapter` を使用するか、単純な関数で十分な可能性があります。ただし拡張性を考慮して保留も可（Severity: Low）。

### 5. データとロジックの混在
- **ファイル**: `specialist_prompts.py`, `phase0_specialists.py`, `phase2_specialists.py`, `phase3_specialists.py`
  - **内容**: 膨大な専門家定義がPythonコードとして記述されています。合計1000行以上のコードが単なるデータ定義です。
  - **推奨**: これらは静的データであり、**YAML/JSON等の設定ファイルに分離**することでコードの見通しを良くし、行数を劇的に削減できます。ロジックとデータを分離すべきです。

### 6. 重複した検索ロジック
- **ファイル**: `search_helper.py` vs `kairos_ingest.py` vs `sophia_ingest.py`
  - **内容**: 各ファイルに検索ロジックやインデックスロード処理が散在しており、DRY原則に違反しています。
  - **推奨**: 検索ロジックを単一のモジュール（例: `search_service.py`）に集約し、重複を排除する。

### 7. ハードコードされたパス
- **ファイル**: `config.py`, `handoff_search.py`, `kairos_ingest.py`, `persona.py`, `search_helper.py`, `sophia_backlinker.py`, `sophia_ingest.py`
  - **内容**: `/home/laihuip001/...` という特定のユーザパスがハードコードされています。
  - **推奨**: 環境変数または設定ファイルから読み込むように修正し、ポータビリティを向上させる。

## 判定
**発言（要改善）**

## 推奨アクション
1. `run_remaining.py` の即時削除。
2. `factory.py` のコメントアウトコード削除。
3. 専門家定義データの外部ファイル化（YAML化）の検討。
4. 検索ロジックの共通化。
