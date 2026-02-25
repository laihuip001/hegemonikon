# Immutableの司祭 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言

## 発見事項
- **グローバル可変状態**: `THEOREM_REGISTRY`、`SERIES_INFO`、`MODE_REQUIREMENTS` が可変な `dict` や `list` として定義されています。これらの基盤となる定数は、実行時の偶発的な変更を防ぐために不変（`Mapping`、`tuple`、または frozen dataclasses）であるべきです。(High)
- **プリミティブへの執着 (可変辞書)**: `extract_dispatch_info`、`_load_projects`、`_load_skills`、`get_boot_context`、`postcheck_boot_report` 関数が可変な `dict` オブジェクトを返しています。これらは不変性を強制し明確なスキーマを提供するために `@dataclass(frozen=True)` としてモデル化されるべきです。(Medium)
- **可変設定リスト**: `MODE_REQUIREMENTS` 内の `required_sections` フィールドがリスト（例: `[...]`）として定義されています。静的な設定シーケンスは不変性を保証するためにタプル `(...)` であるべきです。(Low)

## 重大度
High
