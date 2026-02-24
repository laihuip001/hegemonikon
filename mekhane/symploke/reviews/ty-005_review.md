# Immutableの司祭 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言

## 発見事項
- **グローバルな可変状態 (High)**: `THEOREM_REGISTRY`, `SERIES_INFO`, `MODE_REQUIREMENTS` がモジュールレベルで可変な `dict` として定義されています。これらは不変であるべきです（例: `types.MappingProxyType` などを使用）。
- **可変な設定リスト (High)**: `MODE_REQUIREMENTS` 内の `"required_sections"` の値が可変なリスト（`[...]`）になっています。これらは不変なタプル（`(...)`）であるべきです。
- **構造化されていない戻り値 (Medium)**: `extract_dispatch_info`, `_load_projects`, `_load_skills`, `get_boot_context`, `postcheck_boot_report` などの関数が可変な `dict` オブジェクトを返しています。データの形状と不変性を保証するために `@dataclass(frozen=True)` を使用すべきです。

## 重大度
High
