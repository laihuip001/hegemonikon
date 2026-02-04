# 命名ハルシネーション検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- `create_session` メソッド内での `JulesSession` コンストラクタ呼び出しにおいて、必須引数 `source` が欠落している（コメントアウトされている）。これは、4引数のコンストラクタが存在すると誤認している（シグネチャのハルシネーション）。
- `poll_session` メソッド内での `UnknownStateError` コンストラクタ呼び出しにおいて、必須引数 `session_id` が欠落している。
- `_request` メソッド内で `session.request` を呼び出す際、`json` 引数がコメントアウトされている。これは `json=json` を自己代入と誤認して削除したもので、API呼び出しに必要なデータが渡されない状態となっている。
- `batch_execute` メソッド内で `JulesResult` を生成する際、`task` 引数がコメントアウトされている。

## 重大度
- Critical

## 沈黙判定
- 発言（要改善）
