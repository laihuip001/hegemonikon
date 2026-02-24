# PR巨大化警報者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **巨大ファイル (896行)**: 300行の限界を約3倍超過しており、認知負荷が限界を超えている。誰も全体像を把握できない。
- **責務の過剰な集中**:
  - 設定定義 (`THEOREM_REGISTRY`, `SERIES_INFO`)
  - データロード (`_load_projects`, `_load_skills`)
  - 統合ロジック (`get_boot_context`)
  - プレゼンテーション (`print_boot_summary`)
  - テンプレート生成 (`generate_boot_template`)
  - バリデーション (`postcheck_boot_report`)
  - CLI エントリーポイント (`main`)
  これらが単一ファイルに詰め込まれており、変更時の影響範囲が予測不能。

## 重大度
High
