# fail-fast伝道者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- (Critical) **エラーの隠蔽 (`except Exception: pass`)**:
  - `_load_projects`: YAMLの構文エラーや読み込みエラーが発生しても、空の結果を返し、ユーザーに問題を通知しない。設定ファイルの不備に気づけない。
  - `_load_skills`: スキル定義ファイルのパースエラーを完全に無視している。
  - `extract_dispatch_info`: `AttractorDispatcher` のインポートエラーや実行時エラーを握りつぶしている。
  - `get_boot_context`: `IntentWALManager` や `n8n` 連携の失敗を無視している。
  - `print_boot_summary`: `Theorem recommender` の失敗を無視している。
  - **理由**: 「Graceful degradation」を意図していると思われるが、バグ（例: `NameError` や `SyntaxError`）と環境要因（例: 依存関係の欠如）を区別せず全て無視するため、開発中の問題発見を著しく遅らせる。

- (High) **入力検証の欠如・遅延**:
  - `get_boot_context`: 引数 `mode` の値（"fast", "standard", "detailed"）を検証していない。不正な値を渡してもそのまま後続処理（`load_handoffs` 等）に伝播する。
  - `postcheck_boot_report`: 引数 `mode` が不正な場合、警告なしでデフォルト（"standard"）の要件を適用している。意図しない検証レベルで実行される危険がある。

## 重大度
Critical
