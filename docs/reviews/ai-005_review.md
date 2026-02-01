# 不完全コード検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- `_request` メソッド内 (L192): `session.request` 呼び出しにおいて `json=json` がコメントアウトされており、ペイロードが送信されない不完全なコードが存在する。
- `create_session` メソッド内 (L217): `JulesSession` コンストラクタ呼び出しにおいて `source=source` がコメントアウトされており、必須引数が不足し実行時エラーが発生する。
- `poll_session` メソッド内 (L281): `UnknownStateError` コンストラクタ呼び出しにおいて `session_id=session_id` がコメントアウトされており、引数不足でエラーハンドリング自体がクラッシュする。
- `batch_execute` メソッド内 (L353): `JulesResult` 生成時に `task=task` がコメントアウトされており、エラー時のコンテキスト情報が欠落する。

## 重大度
- Critical

## 沈黙判定
- 発言（要改善）
