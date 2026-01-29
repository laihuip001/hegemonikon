# 入力検証欠落検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- `create_session` メソッドにおいて、`prompt` および `source` 引数が空文字列でないか、または適切な形式であるかの検証が欠落している。
- `create_session` メソッドの `automation_mode` 引数に対し、許容される値（Allowlist）に基づいた検証が行われていない。
- `get_session` メソッドの `session_id` 引数が URL パス構築に使用される前に、不正な文字が含まれていないか等の検証やサニタイズが行われていない。
- `poll_session` メソッドの `poll_interval` および `timeout` 引数に対し、正の数値であるかの検証が欠落している。
- `batch_execute` メソッドにおいて、`tasks` リスト内の辞書が必要なキー（`prompt`, `source`）を含んでいるかどうかの事前検証がなく、実行時の例外に依存している。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
