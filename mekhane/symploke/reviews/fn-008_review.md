# SRP外科医 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **責務の混在 (Logic/Presentation)**: `_load_projects` および `_load_skills` は、データの読み込み処理と、その結果を表示するための文字列整形処理 (`formatted` キーへの格納) を同一関数内で行っている。データ取得と表示ロジックは分離されるべきである。
- **責務の混在 (Side Effects)**: `get_boot_context` は、Bootコンテキストの収集・統合を行う一方で、n8nへのWebhook送信という副作用を含んでいる。また、Intent-WALの読み込みやBC違反ログの集計など、多岐にわたる処理を直接実行している。
- **複数の仕事**: `get_boot_context` は、各軸の統合という主目的以外に、`incoming` ディレクトリのファイルチェックや、`bc_violation_logger` を使用した違反集計など、本来別のモジュールや関数に委譲すべき詳細な実装を含んでいる。
- **戻り値の意味の混在**: `_load_projects` などの関数が返す辞書には、生データ（リストやカウント）と、プレゼンテーション用の整形済み文字列が混在しており、データ構造としての純粋性が損なわれている。

## 重大度
High
