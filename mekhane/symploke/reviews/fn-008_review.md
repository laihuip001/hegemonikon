# SRP外科医 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **`get_boot_context`**: データの取得、統合、フォーマット、副作用（n8nへの送信）が混在している (Critical)
- **`_load_projects`**: データの読み込み・フィルタリングと、表示用文字列の生成が混在している (High)
- **`_load_skills`**: ディレクトリ探索・データパースと、全文を含む表示用文字列の生成が混在している (High)
- **`postcheck_boot_report`**: 検証ロジックと結果のフォーマットが混在している (Medium)
- **`print_boot_summary`**: 出力処理と、「今日の定理」提案や統計計算ロジックが混在している (Medium)

## 重大度
High
