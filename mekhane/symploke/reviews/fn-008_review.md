# SRP外科医 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **`get_boot_context` (Critical)**:
  - 12軸のデータ取得（Logic/IO）、`IntentWAL` のロード（Logic）、`incoming` ディレクトリのチェック（IO）、n8n への Webhook 送信（Side Effect）、および最終的な出力文字列のフォーマット（View）が単一の関数に混在しています。
  - これは「統合」という名目を超えた責務の肥大化であり、テスト困難かつ変更に弱い構造です。

- **`_load_projects` / `_load_skills` (High)**:
  - データのロード・解析（YAML/Markdown Parsing）と、表示用の Markdown 生成（View Construction）が混在しています。
  - データ構造の変更が表示に影響し、表示の変更がデータロードロジックに影響する結合度の高さが問題です。

- **`postcheck_boot_report` (High)**:
  - バリデーションロジック（必須項目のチェック、Drift計算などの Business Rules）と、その結果の表示フォーマット（View）が混在しています。

- **`print_boot_summary` (Medium)**:
  - 処理のオーケストレーションに加え、統計情報の計算（Business Logic）、定理提案の取得（Logic）、および標準出力へのプリント（IO）が混在しています。
  - IO と Logic は分離されるべきです。

- **`generate_boot_template` (Medium)**:
  - テンプレートの定義（Configuration）、文字列構築（View）、ファイル書き込み（IO）が混在しています。

## 重大度
Critical
