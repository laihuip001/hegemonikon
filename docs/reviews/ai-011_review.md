# 過剰最適化検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **階層構造の違反 (Layering Violation)**: `synedrion_review` メソッドが、インフラ層のクライアントコード内にドメイン層の `mekhane.ergasterion.synedrion` を動的にインポートしており、強い結合が生じている。APIクライアントは特定のビジネスロジック（Synedrion v2.1など）を知るべきではない。
- **過度な同時実行数固定**: `MAX_CONCURRENT = 60` が「Ultra plan」を前提にハードコードされており、他のプランや環境での柔軟性を損なっている。
- **責務の肥大化**: `_global_semaphore` によるバッチ間のレート制限管理は、低レベルのHTTPクライアントよりも上位のタスク管理層で扱うべき関心事であり、クライアントクラスが複雑化している。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
