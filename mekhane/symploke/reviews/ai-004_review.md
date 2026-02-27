# 過保護try検出者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **Critical**: `extract_dispatch_info` (L108-L119)
  - `Exception` を全て捕捉し `pass` している。`AttractorDispatcher` の失敗原因（設定ミスや依存関係エラー）が完全に隠蔽される。
- **Critical**: `_load_projects` (L186-L187)
  - `Exception` を全て捕捉し `pass` している。YAML パースエラーやファイル読み込みエラーが隠蔽される。
- **Critical**: `_load_skills` (L264-L265)
  - `Exception` を全て捕捉し `pass` している。スキル読み込みの失敗原因が隠蔽される。
- **High**: `get_boot_context` (L338-L339)
  - `IntentWALManager` の処理全体を `try-except Exception: pass` で囲んでいる。WAL の読み込み失敗やデータ破損が隠蔽される。
- **Medium**: `get_boot_context` (L374-L376)
  - `bc_violation_logger` の処理全体を `try-except Exception` で囲んでいる。ロギング失敗時のエラー詳細が `logging.debug` に落とされるのみで、ユーザーには通知されない（これは許容範囲かもしれないが、広すぎる捕捉範囲）。
- **Low**: `get_boot_context` (L396-L397)
  - `n8n` への webhook 送信失敗を `pass` で無視している。これは意図的かもしれないが、ネットワークエラー以外の例外も隠蔽される。
- **Low**: `print_boot_summary` (L431-L432)
  - `theorem_recommender` の失敗を `pass` で無視している。推奨機能の失敗が隠蔽される。

## 重大度
High
