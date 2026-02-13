# 入力検証推進者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `JulesClient.__init__`: `base_url` の形式チェックがない (Critical)
- `JulesClient.__init__`: `max_concurrent` の正数チェックがない (High)
- `create_session`: `prompt`, `source` の空文字チェックや形式検証がない (High)
- `poll_session`: `timeout`, `poll_interval` の正数チェックがない (Medium)
- `batch_execute`: `tasks` リスト内の辞書構造（必須キーの存在）の検証がない (High)
- `synedrion_review`: `domains`, `axes` の有効値チェックがない (Medium)

## 重大度
High
