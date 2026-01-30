# 自己矛盾検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **同時実行数設定の不一致**: `__init__` メソッドは引数 `max_concurrent` を受け取りセマフォの制限値を設定するが、`__aenter__` メソッドでの `aiohttp.TCPConnector` 初期化時にはハードコードされたクラス定数 `self.MAX_CONCURRENT` (60) が使用されている。これにより、ユーザーが60以上の同時実行数を指定しても、TCPコネクションプールの上限によりボトルネックが発生し、設定が無視される矛盾がある。
- **バッチ処理ロジックの不整合**: `synedrion_review` メソッド内でのバッチサイズ計算において、インスタンスの `_global_semaphore` 設定値ではなく、ハードコードされた `self.MAX_CONCURRENT` (60) が使用されている。これにより、インスタンスがより高い同時実行数（例: 100）で初期化されていても、処理は常に60件ごとのバッチに分割・待機され、リソースが過小利用される矛盾がある。
- **成功判定の定義矛盾**: `JulesResult.is_success` は例外が発生しなかった場合に `True` を返すが、これにはセッション状態が `FAILED` の場合も含まれる（例外が捕捉され `session.error` に格納された場合を除く、APIが正常に `FAILED` 状態を返した場合など）。`synedrion_review` のログ出力では `is_success` を基に「成功」件数をカウントしているため、タスクが失敗したセッションも「成功」として報告されるという、意味論的な矛盾がある。
- **非推奨関数の内部使用**: `parse_state` 関数は非推奨（Deprecated）とされ、`SessionState.from_string` の使用が推奨されているが、同クラス内の `create_session` および `get_session` メソッドが依然として `parse_state` を内部で使用している。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
