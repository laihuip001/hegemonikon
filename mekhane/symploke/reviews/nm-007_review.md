# ブール命名の審判 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `OTEL_AVAILABLE` (L36): 接頭辞欠如 (Medium)
- `close_after` (L342): 接頭辞欠如 (Medium)
- `auto_approve` (L387): 接頭辞欠如 (Medium)
- `fail_on_unknown` (L467): 接頭辞欠如 (Medium)
- `use_global_semaphore` (L568): 動詞のブール名/接頭辞欠如 (Medium)

## 重大度
Medium
