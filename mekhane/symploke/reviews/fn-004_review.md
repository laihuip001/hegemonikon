# early return推進者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **`_load_skills` 内の深いネスト**: `for` ループ内で `if content.startswith` -> `if len(parts)` -> `try` と4段階にネストしています。解析ロジックを関数に抽出するか、ガード節を用いて平坦化すべきです。
- **`get_boot_context` 内の Intent-WAL 読み込み**: `if mode != "fast":` ブロック内に `try` -> `if prev_wal` -> `if incomplete` と続く深いネストがあります。このブロック全体を `_load_intent_wal` のような独立した関数に抽出すれば、早期リターンを活用してネストを解消できます。
- **`_load_projects` 内の条件分岐**: ループ内で `entry_point` の有無を確認し、さらにその内部で `cli` の有無を確認する `if` が重なっています（3レベル）。

## 重大度
Medium
