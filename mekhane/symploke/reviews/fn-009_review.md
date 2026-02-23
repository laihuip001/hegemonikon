# 純粋関数推進者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **I/Oとロジックの混在 (`_load_projects`, `_load_skills`)**
    - ファイル読み込み（I/O）と、データのフィルタリング・集計・整形（ロジック）が同一関数内で行われています。
    - **改善案**: `read_registry` (I/O) と `process_projects` (Pure) に分離することを推奨します。

- **隠れた副作用 (`get_boot_context`)**
    - 関数名が `get_` で始まる取得系の関数ですが、末尾で `n8n` への webhook 送信（副作用）を行っています。
    - **改善案**: データ取得と通知アクションは分離すべきです。

- **非決定的な動作 (`generate_boot_template`)**
    - 関数内で `datetime.now()` を直接呼び出しており、テスト時に時刻を固定することが困難です。
    - **改善案**: 時刻を引数として受け取る設計にすることを推奨します。

- **I/Oとロジックの混在 (`generate_boot_template`, `postcheck_boot_report`)**
    - ファイルの書き込み・読み込みと、コンテンツの生成・検証ロジックが混在しています。
    - **改善案**: `generate_template_content(data) -> str`, `validate_report_content(text) -> dict` のような純粋関数を切り出し、I/O部分は薄いラッパーに留めるべきです。

## 重大度
Low
