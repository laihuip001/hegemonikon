# 階層的予測評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **抽象化レイヤーの混在 (Layer Violation)**: `JulesClient` は `[L2/インフラ]` として定義されていますが、`synedrion_review` メソッドが含まれており、これは特定のドメインロジック（Synedrion v2.1 レビュー、パースペクティブ行列）を実装しています。インフラストラクチャ層が上位のアプリケーションロジックや特定のユースケース（`mekhane.ergasterion`）に深く依存しており、関心事の分離（Separation of Concerns）に違反しています。このメソッドは `JulesClient` を使用する別のサービスクラス（例: `SynedrionReviewer`）に移動すべきです。
- **データ契約の不透明さ (Abstraction Leakage)**: `batch_execute` メソッドが `tasks: list[dict]` を受け取っていますが、辞書の構造（`prompt`, `source`, `branch` 等）が明示的な型定義（Dataclass や Pydantic model）で抽象化されていません。これにより、クライアントと呼び出し元の間の契約が緩く、内部実装の詳細が API インターフェースに漏れ出しています。
- **識別子の合成 (Identity Synthesis)**: `batch_execute` 内での例外発生時に `error-` プレフィックス付きの UUID を生成して `JulesSession` を擬似的に作成しています。これはクライアント側で生成された「存在しないセッション」と、サーバー側の「実在するセッション」の区別を曖昧にし、下流の処理で混乱を招く可能性があります。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
