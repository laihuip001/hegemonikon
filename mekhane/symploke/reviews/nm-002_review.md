# 動詞/名詞の裁定者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- [Medium] リスト型変数に形容詞が単独で使用されている (`active`, `dormant`, `archived`, `related`, `incomplete`)。名詞を補うべき（例: `active_projects`）。
- [Medium] カウント変数に過去分詞が単独で使用されている (`done`, `checked`, `unchecked`)。名詞を補うべき（例: `done_count`）。
- [Medium] 真偽値（Boolean）変数に曖昧な名前（状態を示す `is_` などの前置詞がない）が使用されている (`gpu_ok`, `wal_filled`, `all_passed`)。

## 重大度
Medium
