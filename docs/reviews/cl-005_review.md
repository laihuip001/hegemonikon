# 事前知識査定者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **非同期通信・並行処理の高度な知識**: `asyncio` (Semaphore, gather, Event Loop) および `aiohttp` (Session Lifecycle, Connection Pooling) の深い理解が必須であり、学習コストが高い。
- **ドメイン固有知識の混入 (Synedrion/Hegemonikón)**: インフラ層 (`L2/インフラ`) のクライアントであるにも関わらず、`synedrion_review` メソッドにおいて `mekhane.ergasterion.synedrion` という別領域の知識（PerspectiveMatrix, Theorem Grid, Orthogonal Perspectivesなど）が直接参照されている。これにより、汎用APIクライアントとして理解しようとする開発者に対して、無関係なドメイン知識を要求している。
- **独自ステートマシンの理解**: Jules API 固有のセッション状態遷移 (QUEUED -> ... -> COMPLETED) やポーリング仕様への理解が必要。
- **可観測性 (OpenTelemetry)**: 必須ではないが、分散トレーシング (`opentelemetry`) の知識があるとコードの意図（ヘッダー注入など）がより理解しやすい構造になっている。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
