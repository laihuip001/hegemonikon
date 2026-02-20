# 再計算防止者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `generate_boot_template` 関数: `projects` リストに対する `[p for p in projects if ...]` 内包表記が3回（active, dormant, archived）実行されており、かつメインループでもう1回反復されている（計4回）。加えて `p.get("status")` が複数回呼び出されている。 (Low)
- `postcheck_boot_report` 関数: `content.count("<!-- FILL -->")` が `fill_count` と `fill_remaining` の2箇所で同一の計算を行っている。 (Low)
- `_load_skills` 関数: `content.split("---", 2)` が2回実行されている。 (Low)
- `_load_projects` 関数: `projects` リストに対する `[p for p in projects if ...]` が3回実行されており、ループ内で `p.get("id")`, `p.get("status")` が複数回呼び出されている。 (Low)

## 重大度
Low
