# 事前知識査定者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **技術的要件:**
    - **非同期処理 (Asyncio):** `asyncio` モジュール (coroutines, gather, Semaphore, Event Loop) の深い理解が必要。
    - **HTTP通信 (Aiohttp):** `aiohttp` (ClientSession, TCPConnector, Context Managers) の使用法とリソース管理の知識が不可欠。
    - **API相互作用:** ポーリング、バックオフ戦略 (Exponential Backoff)、レート制限 (429) ハンドリングの理解が必要。
    - **設計パターン:** デコレータ (`with_retry`)、データクラス、Enumの使用。

- **ドメイン知識の混入 (認知負荷の増大):**
    - `synedrion_review` メソッドが API クライアントに含まれており、`mekhane.ergasterion.synedrion` (Synedrion v2.1, PerspectiveMatrix, Theorem Grid) に関する深いドメイン知識を要求する。
    - 汎用的な API クライアントとしての役割と、特定のビジネスロジック (480の直交的視点によるレビュー) が混在しており、コードの理解を妨げる要因となっている。
    - これにより、単に API クライアントを使用・保守したい開発者に対しても、不要なドメイン知識 (Hegemonikón 特有の概念) の習得を強いる結果となっている。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
