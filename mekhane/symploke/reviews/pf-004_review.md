# 再計算防止者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **`_load_skills` 内での `split` の重複実行 (Low)**
  - `content.split("---", 2)` が同一ループ内で2回実行されています（YAMLパース時と本文抽出時）。一度変数に格納して再利用すべきです。

- **`postcheck_boot_report` 内での `count` の重複実行 (Low)**
  - `content.count("<!-- FILL -->")` が `fill_count` (Check 1) と `fill_remaining` (BS-3b) の計算で2回実行されています。

- **`_load_projects` 内でのリスト走査と辞書ルックアップの重複 (Low)**
  - `projects` リストを `active`, `dormant`, `archived` のフィルタリングで3回走査し、さらにカテゴリ分けで1回走査しています。また、その都度 `p.get("status")` が呼び出されています。1回のループで集計可能です。

## 重大度
Low
