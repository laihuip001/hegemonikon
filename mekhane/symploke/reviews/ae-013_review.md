# シンプリシティの門番 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **デッドコード (Low)**: `_load_projects` (lines 88-154) および `_load_skills` (lines 158-216) は定義されているが、`get_boot_context` (lines 228-241) では `boot_axes` からインポートされた同名の関数を使用しているため、これらは完全に冗長であり削除すべきである。
- **デッドコード (Low)**: `THEOREM_REGISTRY` (lines 35-64) および `SERIES_INFO` (lines 67-70) は定義されているが、コード内のロジックで一切参照されていない。使用予定がないなら削除すべきである。
- **デッドコード (Low)**: `extract_dispatch_info` (lines 74-85) は定義されているが、どの関数からも呼び出されていない。

## 重大度
Low
