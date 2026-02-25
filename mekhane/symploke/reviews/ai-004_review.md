# 過保護try検出者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `extract_dispatch_info` 関数内: `AttractorDispatcher` のインポート、初期化、実行全体が `except Exception: pass` で囲まれており、インポートエラーや論理エラーが隠蔽されている (Low)
- `_load_projects` 関数内: `registry.yaml` の読み込みとパース処理全体が `except Exception: pass` で囲まれており、YAML構文エラーやファイルIOエラーが隠蔽されている (Low)
- `_load_skills` 関数内: ディレクトリ走査と各スキルファイルの読み込みループ全体が `except Exception: pass` で囲まれており、予期せぬエラーが隠蔽されている (Low)
- `get_boot_context` 関数内: `IntentWALManager` の読み込みと実行、`bc_violation_logger` の読み込み、`urllib` による n8n 通知の3箇所で `except Exception` が使用され、エラーが握りつぶされている (Low)
- `print_boot_summary` 関数内: `theorem_recommender` のインポートと実行が `except Exception: pass` で囲まれており、エラーが隠蔽されている (Low)

## 重大度
Low
