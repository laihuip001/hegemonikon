# 事前知識査定者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **高度な非同期処理 (AsyncIO / Aiohttp)**:
    - `asyncio` (Semaphore, gather, sleep) および `aiohttp` (ClientSession, TCPConnector, Context Manager) の深い理解が必須。特にコネクションプーリングや並行数制御の実装を理解するには、これらのライブラリの仕様に精通している必要がある。
- **Hegemonikón / Synedrion ドメイン知識**:
    - "Synedrion v2.1", "480 orthogonal perspectives", "Hegemonikón theorem grid" といった用語や、`mekhane.ergasterion.synedrion` への依存関係がある。これらが何を指し、どのようなロジックで動いているか（20ドメイン×24軸など）を理解するためのドメイン知識が必要。
- **Google Jules API 仕様**:
    - セッションの状態遷移 (QUEUED -> PLANNING -> ... -> COMPLETED) やポーリングの仕組み、レートリミット (429) の挙動など、Jules API 固有の仕様を知っている必要がある。
- **分散トレーシング (OpenTelemetry)**:
    - `opentelemetry` によるトレースコンテキストの注入 (`inject`) が行われており、オブザーバビリティの基礎知識があると望ましい。
- **Python 最新文法**:
    - `int | None` のような Union 型の短縮記法や dataclass の使用など、比較的新しい Python の機能が使われている。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
