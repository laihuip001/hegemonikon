# 副作用の追跡者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **暗黙のネットワーク通信 (High)**: `get_boot_context` 内で `urllib.request` を使用して `localhost:5678` (n8n) に POST リクエストを送信している (L379)。関数名からは想像できない重大な副作用である。
- **例外の隠蔽 (High)**: `_load_projects` (L148), `_load_skills` (L215), `extract_dispatch_info` (L90), `get_boot_context` (L385), `print_boot_summary` (L407) で `except Exception: pass` を多用しており、I/Oエラーや内部エラーが隠蔽されている。
- **グローバル警告設定の変更 (Medium)**: `sys.exit` 直前に `warnings.filterwarnings("ignore")` を実行している (L515)。これはプロセス全体の警告設定を暗黙に変更する。
- **ファイル書き込みの副作用 (Medium)**: `generate_boot_template` が `/tmp/boot_report_...` にファイルを書き込んでいる (L409)。関数名からは「生成して返す」ことが期待されるが、実際にはファイルシステムへの書き込みを行っている。
- **sys.path の改変 (Low)**: `sys.path.insert(0, ...)` (L30) により、インポート時にグローバルなモジュール検索パスを変更している。

## 重大度
High
