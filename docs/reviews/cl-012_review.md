# コンテキストスイッチ検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **APIロジックの重複**: `jules_client.py` と `mekhane/symploke/run_specialists.py` の間で Jules API (jules.googleapis.com) への接続ロジック（URL構築、ヘッダー設定）が重複している。API仕様変更時に複数箇所の修正が必要となり、認知負荷が高い。
- **隠蔽された依存関係**: `synedrion_review` メソッド内で `mekhane.ergasterion.synedrion` を import しており（遅延インポート）、モジュールレベルの依存関係として明示されていない。このメソッドの動作を理解・デバッグするために別パッケージへ移動する必要がある。
- **テスト/CLIの機能重複**: `jules_client.py` の `main` 関数が `tests/test_jules_client.py` と目的が重複するテスト用CLIを実装している。テストコードと本番コードの境界が曖昧になり、確認のためにファイルを移動する必要がある。
- **プロンプト生成ロジックの分断**: プロンプト生成が `synedrion_review`（`PerspectiveMatrix`を使用）と `run_specialists.py`（`specialist_prompts.py`を使用）で分断されており、タスク生成ロジックを理解するためのコンテキストスイッチが発生する。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
