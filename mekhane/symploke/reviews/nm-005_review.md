# 意味なき名の追放者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `SERIES_INFO` (L52): `info` は具体性に欠ける。`SERIES_DESCRIPTIONS` や `SERIES_METADATA` などが望ましい。
- `extract_dispatch_info` (L59): 関数名に `info` が含まれる。`extract_dispatch_plan` などが望ましい。
- `dispatch_info` (L66): 変数名 `info`。`dispatch_plan` や `dispatch_summary` などが望ましい。
- `result` (L89, L156, L351, L423, L622, L654): `_load_projects`, `_load_skills`, `print_boot_summary`, `generate_boot_template`, `postcheck_boot_report`, `main` 内で `result` が多用されている。`project_stats`, `skill_summary`, `boot_context` など具体的な内容を表す名前にすべき。
- `data` (L96): `_load_projects` 内で `data` が使用されている。`registry_content` や `project_list` などが望ましい。
- `*_result` (L218-240, L307, L323): `get_boot_context` 内で `handoffs_result`, `ki_result` など `_result` 接尾辞が多用されている。`handoffs_data` や単に `handoffs` (辞書であることを示すなら `handoffs_dict` など) の方が文脈に即している場合があるが、`result` 単体よりはマシとはいえ、安易な命名に見える。

## 重大度
Medium
