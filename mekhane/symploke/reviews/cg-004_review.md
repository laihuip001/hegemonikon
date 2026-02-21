# 意図コメント推進者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` (L87) に `# PURPOSE:` コメントが欠落している (Medium)
- `MODE_REQUIREMENTS` (L352) のマジックナンバー (`handoff_count: 10`, `min_chars: 3000` 等) に対する意図（なぜその数値か、どの程度の認知負荷を求めているか）が記述されていない (Low)
- `_load_projects` (L110) のプロジェクト分類ロジック（特定のIDを「研究・概念」や「理論・言語基盤」に振り分ける基準）に意図が示されていない (Low)

## 重大度
Medium
