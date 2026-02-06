# 予測誤差バグ検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **幻覚のセッションID (Hallucinated Error UUIDs)**: `batch_execute` 内でエラー発生時に `uuid.uuid4()` を生成して `JulesSession` の ID に設定している。これは実在しないセッションIDであり、下流システムがこのIDを用いて参照しようとすると不整合（サプライズ）を引き起こす。
- **レイヤー違反 (Layer Violation)**: インフラ層（L2）の `JulesClient` が、ドメイン層の `mekhane.ergasterion.synedrion` に依存している (`synedrion_review` メソッド)。これは依存性逆転の原則に反し、予測不可能な結合を生む。
- **リソースリーク (Resource Leaks)**: `_session` プロパティが、アクセスされるたびに新しい `aiohttp.ClientSession` を作成し（`_shared` や `_owned` がない場合）、クローズしない。これはエントロピーの増大（リソース枯渇）を招く。
- **誤解を招く沈黙検出 (Fragile Silence Detection)**: `synedrion_review` メソッドで `str(r.session)` に "SILENCE" が含まれるかを判定しているが、`JulesSession` には出力内容（content/output）が含まれていないため、この判定は常に期待外れの結果（偽陰性）になる可能性が高い。
- **硬直的なポーリング方針 (Rigid Polling Policies)**: `poll_session` が `with_retry` デコレータを持つ `get_session` を呼び出しつつ、自身でも再試行ロジックを持つため、再試行戦略が重複・複雑化しており、予測困難なタイムアウト挙動を引き起こす。

## 重大度
- Critical

## 沈黙判定
- 発言（要改善）
