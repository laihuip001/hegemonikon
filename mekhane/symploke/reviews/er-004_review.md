# fail-fast伝道者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- Critical: `extract_dispatch_info`関数で `try...except Exception: pass` によりすべての例外が握りつぶされている。
- Critical: `_load_projects`関数で `try...except Exception: pass` によりすべての例外が握りつぶされている。
- Critical: `_load_skills`関数で `try...except Exception: pass` によりすべての例外が握りつぶされている。
- Critical: `get_boot_context`関数で `IntentWALManager` の読み込み失敗時、`try...except Exception: pass` によりすべての例外が握りつぶされている。
- Critical: `get_boot_context`関数で n8n Webhook 送信失敗時、`try...except Exception: pass` によりすべての例外が握りつぶされている。
- Critical: `print_boot_summary`関数で `theorem_recommender` 実行時、`try...except Exception: pass` によりすべての例外が握りつぶされている。
- High: `get_boot_context`関数の `mode` 引数に対する入力検証が関数の冒頭で行われていない（`argparse` 依存）。

## 重大度
Critical
