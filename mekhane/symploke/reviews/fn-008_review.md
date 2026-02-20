# SRP外科医 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **`get_boot_context`**: 責務混在 (High)
  - データの取得 ("get")、文字列のフォーマット ("formatted" キーの生成)、外部副作用 (n8n Webhook送信) が混在している。
  - WAL読み込み、BC違反チェック、Incomingファイル確認などのロジックが関数内に直書きされており、`boot_axes` への委譲パターンと不整合を起こしている。
- **`_load_projects` / `_load_skills`**: 責務混在 (Medium)
  - データのロード・フィルタリングロジックと、表示用文字列 (`formatted`) の生成ロジックが同一関数内にある。データ構造の構築とプレゼンテーションは分離されるべき。
- **`print_boot_summary`**: 責務混在 (Medium)
  - 「サマリーの表示」という名前だが、統計情報の計算、今日の定理 (Theorem) の推奨ロジック実行、テンプレート生成処理 (`generate_boot_template` 呼び出し) を含んでいる。

## 重大度
High
