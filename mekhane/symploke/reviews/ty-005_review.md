# Immutableの司祭 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- 可変戻り値（辞書）: `extract_dispatch_info`, `_load_projects`, `_load_skills`, `get_boot_context`, `postcheck_boot_report` は `dict` を返却している。構造化データの返却には `@dataclass(frozen=True)` を使用すべきである。(Medium)
- 可変設定値: `MODE_REQUIREMENTS` 内の `required_sections` が `list` (`[...]`) で定義されている。静的な設定値には `tuple` (`(...)`) を使用すべきである。(Low)
- 可変グローバル状態: `THEOREM_REGISTRY` および `SERIES_INFO` が `dict` で定義されている。これらは定数であり、不用意な変更を防ぐため不変な構造（`types.MappingProxyType` 等）にすべきである。(Low)

## 重大度
Medium
