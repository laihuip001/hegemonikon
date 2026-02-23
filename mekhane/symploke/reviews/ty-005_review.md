# Immutableの司祭 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- Global Mutable State (High): `THEOREM_REGISTRY`, `SERIES_INFO`, `MODE_REQUIREMENTS` がモジュールレベルで可変辞書として定義されています。これらは不変（例: `types.MappingProxyType` や frozen dataclasses）にして、偶発的な変更を防ぐべきです。
- Mutable Configuration Lists (High): `MODE_REQUIREMENTS` 内の `required_sections`（例: `["Handoff 個別要約", ...]`) が可変リストになっています。これらは設定の整合性を保つために不変タプル `(...)` にすべきです。
- Missing `@dataclass(frozen=True)` (Medium): `_load_projects`, `_load_skills`, `get_boot_context`, `postcheck_boot_report` などの関数が生の辞書を返しています。これらの構造化された戻り値は、構造と不変性を保証するために frozen dataclasses として定義すべきです。

## 重大度
High
