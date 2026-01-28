# Markov blanket 検出者 レビュー
## 対象ファイル: mekhane/symploke/jules_client.py
## 発見事項:
1. **リソース依存性の分離不全**: `create_session`, `get_session` メソッド内で都度 `aiohttp.ClientSession` を生成・破棄している。特に `poll_session` のループや `batch_execute` での並列実行時において、TCP コネクションの再利用（Keep-Alive）が行われず、OS レベルの ephemeral port を大量に消費するリスクがある。これはクライアント（Markov blanket）内部で完結すべきリソース管理が、外部（OS）の状態に不必要に依存・影響を与えていることを意味する。
2. **並行性制御のスコープ限定**: `batch_execute` 内の `asyncio.Semaphore` がメソッド呼び出しごとのローカルスコープで生成されている。これにより、複数の `batch_execute` 呼び出しや同一プロセスの並行動作において、クラスで定義された `MAX_CONCURRENT`（API のグローバル制限）を順守できない。外部環境（API 制限）との条件付き独立性が保たれておらず、意図しないレート制限超過を招く可能性がある。
3. **状態判定の不確実性**: `parse_state` が未知のステータスを一律に `IN_PROGRESS` と判定している。API 仕様変更により新たな終了ステータスが追加された場合、無限ポーリング（タイムアウトまで）を引き起こし、不要なリソース消費を招く。
## 重大度: High
## 沈黙判定: 発言（要改善）
