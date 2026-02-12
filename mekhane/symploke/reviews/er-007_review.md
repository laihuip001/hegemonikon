# カスタム例外推進者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- (Low) `JulesClient.__init__` にて API キー未設定時に組み込みの `ValueError` を送出しています。これは設定ミスを表すドメイン固有の例外（例: `JulesConfigurationError`）であるべきです。
- (Low) `JulesClient.poll_session` にてタイムアウト時に組み込みの `TimeoutError` を送出しています。`JulesError` を継承した `JulesTimeoutError` を定義し、例外階層を統一すべきです。
- (Low) `JulesClient.synedrion_review` にて `ImportError` をそのまま送出しています。これは機能不足を表すドメイン例外としてラップすることが望ましいです。

## 重大度
Low
