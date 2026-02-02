# 入力検証欠落検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **`batch_execute` メソッドにおける例外ハンドリングの欠陥 (Critical)**:
  - `tasks` リスト内の辞書に `prompt` または `source` キーが含まれていない場合、`bounded_execute` 内の `try` ブロックで `KeyError` が発生する。
  - その後の `except` ブロック内で、エラー情報を記録した `JulesSession` オブジェクトを作成しようとする際、再び `task["prompt"]` および `task["source"]` にアクセスしている。
  - これにより再度 `KeyError` が発生し、例外ハンドリング自体が失敗するため、単一のタスクの失敗がバッチ全体の実行を中断（クラッシュ）させる恐れがある。

- **`create_session` メソッドにおけるバリデーション欠落 (Medium)**:
  - `prompt` および `source` 引数に対して、空文字や `None` のチェックが行われていない。
  - 不正な値がそのまま API リクエストに渡され、無駄なネットワーク通信が発生する可能性がある。

- **`__init__` メソッドにおけるバリデーション欠落 (Low)**:
  - `max_concurrent` 引数が正の整数であることを確認していない。負の値や 0 が渡された場合、`asyncio.Semaphore` の初期化時に `ValueError` が発生する可能性があるが、明示的なチェックがない。

## 重大度
- Critical

## 沈黙判定
- 発言（要改善）
