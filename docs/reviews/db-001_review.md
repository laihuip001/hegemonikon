# N+1検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `synedrion_review` メソッド内において、`tasks` リストを `batch_size` ごとに分割し、`for` ループ内で `await self.batch_execute(batch_tasks)` を呼び出している箇所が存在します。
- これは「ループ内クエリ」に該当し、各バッチの完了を待機してから次のバッチを開始するため、並行処理の効率を著しく低下させています（Critical）。
- `batch_execute` メソッドは既にセマフォによる並行数制御 (`_global_semaphore`) を備えているため、手動でバッチ分割してループする必要はなく、全タスクを一度に渡すべきです。

## 重大度
Critical
