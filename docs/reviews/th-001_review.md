# 予測誤差バグ検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項

### 1. 幻覚エラーUUIDの生成 (Hallucinated Error UUIDs)
- **箇所**: `batch_execute` メソッド内の例外処理ブロック
- **内容**: タスク失敗時に `error-` で始まるランダムなUUIDを持つ `JulesSession` オブジェクトを生成している。
- **予測誤差**: APIサーバー上に存在しないセッションIDをクライアント側で勝手に捏造（幻覚）している。このIDを用いて後続処理（再試行やステータス確認）を行おうとすると、サーバー側で404エラーとなり、デバッグを困難にする。`JulesResult` には `error` フィールドがあるため、偽のセッションオブジェクトを作る必要はない。

### 2. レイヤー違反と責務の混入 (Layer Violation)
- **箇所**: `synedrion_review` メソッド
- **内容**: L2 Infrastructure層であるはずのクライアントコード内に、L3/Business層（ドメイン固有）の `mekhane.ergasterion.synedrion` への依存とロジックが含まれている。
- **予測誤差**: 汎用的なAPIクライアント (`JulesClient`) が、特定の業務ロジック（Synedrionレビューのパースペクティブ生成など）を知っていることは驚き（Surprise）である。これは関心の分離（Separation of Concerns）に反し、クライアントの再利用性を低下させる。

### 3. リソースリークの罠 (`_session` Property Trap)
- **箇所**: `_session` プロパティ
- **内容**: `self._shared_session` や `self._owned_session` がない場合、アクセスするたびに新しい `aiohttp.ClientSession()` を生成して返している。
- **予測誤差**: プロパティへのアクセス（getter）副作用として、クローズされない新しいセッションが毎回生成される挙動は予測困難である。このプロパティを内部または外部から不用意に利用すると、深刻なリソースリーク（TCPコネクション枯渇）を引き起こす。

### 4. 誤解を招く状態ログ (Misleading Log)
- **箇所**: `main` 関数
- **内容**: `JulesClient` インスタンス化直後に "Connection Pooling: Enabled" と出力している。
- **予測誤差**: 実際にはコネクションプーリング（`TCPConnector` を持つ `_owned_session`）は `__aenter__` (async context manager) に入るまで初期化されない。実装状態とログ出力に乖離があり、利用者を騙す形になっている。

### 5. 硬直的なポーリングバックオフ (Rigid Polling Policy)
- **箇所**: `poll_session` メソッド
- **内容**: レート制限（429）時はバックオフするが、一度でも成功（200 OK）すると即座に `current_interval` を初期値にリセットしている。
- **予測誤差**: APIが高負荷状態にある場合、断続的な成功のたびにリクエスト頻度を最大まで戻す挙動は、サーバーへの攻撃的な振る舞いとなり得る。全体的な経過時間や「成功したが処理中」の状態に応じて、緩やかに間隔を空ける適応的なバックオフが期待される。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
