# atomic commit教官 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- オーケストレーション（`get_boot_context`）と実装詳細（`_load_projects`, `_load_skills`）が同居している。
- `boot_axes.py` からの実装呼び出し（`from mekhane.symploke.boot_integration import _load_projects`）により循環依存が発生しており、役割分担が不明確。
- ビュー層の責務であるテンプレート生成（`generate_boot_template`）が混入している。
- 品質保証層の責務であるレポート検証（`postcheck_boot_report`）が混入している。
- 単一ファイルが「統合」「実装」「表示」「検証」の4つの責務を持っており、変更理由が多岐にわたるため、atomic commit を阻害する要因となっている。

## 重大度
Medium
