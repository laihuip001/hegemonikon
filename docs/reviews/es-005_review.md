# エラーメッセージ共感性評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- `JulesClient.__init__` の `ValueError` ("API key required...") は命令的で、ユーザーに対する配慮が不足している。より丁寧な表現（例："Please provide an API Key..."）や、設定方法の具体的なガイダンスを含めると親切である。
- `poll_session` の `TimeoutError` は事実のみを伝えており、ユーザーが次にどうすべきか（タイムアウト値の延長など）の示唆がない。
- `RateLimitError` のデフォルトメッセージ ("Rate limit exceeded") は機械的である。リトライが可能であることや、自動バックオフが機能している文脈であればその旨を伝えると安心感につながる。
- CLI の `print(f"❌ Error: {e}")` はエラー内容をダンプするだけで、ユーザーに対する共感（"申し訳ありません、エラーが発生しました" など）や文脈の提供がない。

## 重大度
- Low

## 沈黙判定
- 発言（要改善）
