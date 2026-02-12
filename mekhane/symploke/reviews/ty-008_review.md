# ジェネリクスの調律師 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `JulesResult` クラスと `batch_execute` メソッドにおいて、`task` フィールドが `dict` 型で定義されています。これにより、タスクデータの型情報が消失しています。`TypeVar` を導入し、`JulesResult` を `Generic[T]` とすることで、入力されたタスクの型を出力まで保持すべきです。 (Medium)
- `with_retry` デコレータが型情報を保持していません。`ParamSpec` と `TypeVar` を使用して、デコレートされた関数の引数と戻り値の型を維持すべきです。 (Medium)

## 重大度
Medium
