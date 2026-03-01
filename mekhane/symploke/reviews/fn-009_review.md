# 純粋関数推進者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects`: ファイルからのI/O（`registry_path.read_text`）とデータフォーマット（表示用文字列の生成など）の計算が混在しています。可能であれば、データの読み込みとフォーマット生成を分離し、フォーマット部分を純粋関数にしてください。
- `_load_skills`: 外部ファイルシステムへのアクセス（`skills_dir.iterdir()`, `skill_md.read_text`）と、スキルのパース/文字列フォーマット生成が混ざっています。
- `get_boot_context`: 外部状態である n8n の webhook へ HTTP POST しています。また、`Path.home()` からのファイルシステムアクセスに依存しています。
- `generate_boot_template`: `datetime.now()` による隠れた時間への依存があり、出力結果が毎回変わるためテストが困難になります。時刻は引数として受け取るようにすることが望ましいです。

## 重大度
Low
