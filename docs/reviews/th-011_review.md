# JTB知識評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **「沈黙」検出の論理的誤謬 (False Belief):** `synedrion_review` メソッドにおいて、`"SILENCE" in str(r.session)` という条件でレビューの「沈黙」を検出しようとしている。しかし、`JulesSession` データクラスは API レスポンスの `outputs` (レビュー本文) を保持しておらず、文字列表現にはメタデータしか含まれないため、この判定は常に偽となる（または意図しない誤検知を起こす）構造的な欠陥がある。
- **成功定義の不正確さ (Imprecise Definition):** `JulesResult.is_success` プロパティは、RPC 呼び出し自体が例外なく完了したことを「成功」と定義しており、セッション状態 (`state`) が `FAILED` や `CANCELLED` であっても `True` を返す。これは「タスクの成功」と「通信の成功」を混同しており、`synedrion_review` の集計ログにおいて失敗したタスクが「成功」としてカウントされる誤解を招く表現となっている。
- **並行性制限の回避 (Unjustified Bypass):** `batch_execute` は `_global_semaphore` を使用して並行数を制御しているが、`create_and_poll` を直接呼び出す場合はこのセマフォをバイパスする。これは `MAX_CONCURRENT` (Ultra plan limit) というビジネスルールの適用を一貫させておらず、下位層 (`TCPConnector`) の制限のみに依存する正当化できない設計となっている。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
