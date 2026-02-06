# ストア派規範評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **[Justice違反] コンテキストの喪失**
  `create_and_poll` メソッドにおいて、`poll_session` がタイムアウト (`TimeoutError`) した場合、生成された `session_id` が例外に含まれず失われる。これにより呼び出し元はセッションの状態確認やキャンセルを行う手段を失い、「孤児セッション」が発生する。これはリソースに対する責任（Justice）の欠如である。

- **[Prudence適合] 鍵の隠蔽**
  `mask_api_key` 関数において、短いキーに対する完全マスク処理など、情報漏洩を防ぐための賢慮（Prudence）が実装されている。

- **[Fortitude適合] 回復性**
  `with_retry` デコレータおよびポーリング中の `RateLimitError` ハンドリングにより、外部障害に対して粘り強く動作する不屈さ（Fortitude）が示されている。

- **[Temperance適合] 節制**
  `_global_semaphore` による同時実行制御が実装されており、過剰なリソース消費を抑制する節制（Temperance）が働いている。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
