# チャンク化効率評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **SRP違反 (Single Responsibility Principle)**: `JulesClient` クラスが、低レベルなHTTP通信/セッション管理と、高レベルなビジネスロジックである `synedrion_review` を混在させています。本来、APIクライアントはドメインロジック（Synedrion）を知るべきではありません。
- **God Method**: `synedrion_review` メソッドが過大です。パースペクティブのロード、フィルタリング、タスク生成、バッチ処理、実行ループ、進捗報告、集計を全て一箇所で行っており、凝集度が低下しています。
- **依存関係の逆転**: `JulesClient` 内で `mekhane.ergasterion.synedrion` を動的にインポートしており、下位レイヤー（Client）が上位レイヤー（Business Logic）に依存する形になっています。
- **非効率なバッチ処理**: `synedrion_review` 内でリストをチャンクに分割し、`await` で順次実行しているため、バッチ内の最も遅いタスクに全体が足を引っ張られる「Stop-and-Wait」が発生しています。`asyncio.gather` とセマフォを用いたスライディングウィンドウ方式などで効率化すべきです。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
