# Immutableの司祭 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **Critical**: `THEOREM_REGISTRY`、`SERIES_INFO`、`MODE_REQUIREMENTS` 等のグローバルな状態が、可変な標準の `dict` や `list` として定義されています。これらは実行時の偶発的な変更を防ぐため、不変（例: `types.MappingProxyType`、`tuple`、または `frozen=True` なデータクラス）であるべきです。
- **Medium**: `get_boot_context`、`_load_projects`、`extract_dispatch_info` などの関数が、暗黙的なスキーマを持つ可変な `dict` オブジェクトを返しています。これらはスレッドセーフ性を確保し、偶発的な変更を防ぐために、厳密に型定義された `@dataclass(frozen=True)` インスタンスであるべきです。
- **Medium**: `MODE_REQUIREMENTS` が静的な設定に可変なリスト（例: `required_sections`）を使用しています。これらはタプルであるべきです。

## 重大度
High
