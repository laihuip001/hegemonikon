# 支配二分法評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **硬直的な並行性制限 (Hardcoded Concurrency Limit)**: `MAX_CONCURRENT = 60` は「Ultra plan」という特定の契約状況（変更可能な側面）をコード内の定数（システム制約）として埋め込んでいます。契約変更や環境の違いに対応するにはコード修正が必要になります。
- **リトライポリシーの固定化 (Fixed Retry Policy)**: `@with_retry(max_attempts=3, ...)` のようにデコレータ引数がハードコードされており、ネットワーク環境や要件に応じた柔軟な制御（Control）が困難です。
- **未知の状態への過剰な制御 (Rigid Unknown State Handling)**: `poll_session` における `UNKNOWN` 状態への3回連続検出での例外送出は、外部システムの変化（新しい中間状態の追加など）に対して脆弱であり、クライアント側の都合による過度な制約となっています。
- **論理とリソースの混同 (Conflation of Logic and Resources)**: `synedrion_review` において `batch_size = self.MAX_CONCURRENT` としており、論理的なバッチサイズを物理的な接続数制限に直結させています。これらは本来別個に制御されるべき変数です。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
