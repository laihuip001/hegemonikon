# 入力検証欠落検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **`batch_execute` メソッドのタスク構造検証欠落**: `tasks` 引数として渡される辞書リストに対し、必須キー（`prompt`, `source`）の存在確認が行われていない。
- **例外ハンドラ内の二次クラッシュ**: `batch_execute` 内の `bounded_execute` 関数において、`KeyError`（必須キー欠落など）を捕捉した際、エラーレポート作成のために再度 `task["prompt"]` や `task["source"]` にアクセスしている。これにより、元の `KeyError` の原因がキー欠落だった場合、例外ハンドラ内で再び `KeyError` が発生し、プロセスがクラッシュする脆弱性がある。
- **`create_session` メソッドの引数検証欠落**: `prompt`（空文字列チェック）や `source`（形式チェック）に対するバリデーションが存在しない。APIへの無駄なリクエストや予期せぬエラーを防ぐための事前検証が必要。
- **`__init__` および設定値の検証欠落**: `max_concurrent`、`timeout`、`poll_interval` などの数値引数に対して、正の整数であることの検証が行われていない。

## 重大度
- Critical

## 沈黙判定
- 発言（要改善）
