# bare except処刑人 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- Line 613: `except Exception as e:` (High) - `batch_execute` 内の過度に広い例外捕捉です。`JulesError` や `aiohttp.ClientError` など具体的な例外に絞るべきです。
- Line 829: `except Exception as e:` (Low) - `main` CLI 内の過度に広い例外捕捉です。

## 重大度
High
