# docstring構造家 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- (Medium) `RateLimitError.__init__`: docstring欠如
- (Medium) `UnknownStateError.__init__`: docstring欠如
- (Medium) `JulesResult.is_failed`: docstring欠如
- (Low) モジュールdocstring: 一行目が動詞でない、ピリオド欠落
- (Low) `JulesError`: 一行目が動詞でない
- (Low) `SessionState`: 一行目が動詞でない
- (Low) `SessionState.from_string`: Args/Returns不足
- (Low) `parse_state`: Args/Returns不足
- (Low) `JulesResult`: 一行目が動詞でない
- (Low) `JulesResult.is_success`: 一行目が動詞でない、Returns不足
- (Low) `with_retry`: 一行目が動詞でない、Returns不足
- (Low) `JulesClient`: 一行目が動詞でない
- (Low) `JulesClient.__aenter__`: 一行目が動詞でない
- (Low) `JulesClient.__aexit__`: 一行目が動詞でない
- (Low) `main`: 一行目が動詞でない

## 重大度
Medium
