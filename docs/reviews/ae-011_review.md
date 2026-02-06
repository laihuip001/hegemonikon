# docstring構造家 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `JulesError`: 一行目が動詞でない (Base exception...) - Severity: Low
- `SessionState`: 一行目が動詞でない (Jules session states.) - Severity: Low
- `SessionState.from_string`: Args/Returns不足 - Severity: Low
- `JulesResult`: 一行目が動詞でない (Result wrapper...) - Severity: Low
- `JulesResult.is_success`: docstring欠如 - Severity: Medium
- `JulesResult.is_failed`: docstring欠如 - Severity: Medium
- `with_retry`: 一行目が動詞でない (Decorator for...) - Severity: Low
- `JulesClient`: 一行目が動詞でない (Async client...) - Severity: Low
- `JulesClient.__aenter__`: 一行目が動詞でない (Context manager entry...) - Severity: Low
- `JulesClient.__aexit__`: 一行目が動詞でない (Context manager exit...) - Severity: Low
- `JulesClient._request`: 一行目が動詞でない (Unified HTTP request handler.) - Severity: Low
- `main`: 一行目が動詞でない (CLI entry point...) - Severity: Low

## 重大度
Medium
