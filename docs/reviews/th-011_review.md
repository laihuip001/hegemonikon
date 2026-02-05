# JTB知識評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **Critical TypeError (create_session)**: `JulesSession` コンストラクタで必須引数 `source` が欠落しているため、呼び出し時にクラッシュする。
- **Critical TypeError (poll_session)**: `UnknownStateError` の初期化時に必須引数 `session_id` が欠落しているため、未知の状態を検出した際にクラッシュする。
- **レイヤー違反 (Layer Violation)**: インフラ層 (L2) の `jules_client` が、ドメイン層 (L3/Workshop) の `mekhane.ergasterion.synedrion` に依存している (`synedrion_review` メソッド)。依存関係逆転の原則に違反している。
- **非効率なバッチ処理**: `synedrion_review` が手動でバッチ分割を行っており、各バッチの完了を待ってから次へ進むため、並行処理のスループットが低下している（スライディングウィンドウ方式ではない）。
- **誤解を招くログ**: `main` 関数において、TCPコネクタが初期化される前（コンテキストマネージャに入る前）に "Connection Pooling: Enabled" と表示しており、事実に反する可能性がある。
- **脆弱なロジック**: 沈黙検知ロジックが `str(r.session)` の文字列判定に依存しており、実装として脆弱である。

## 重大度
- Critical

## 沈黙判定
- 発言（要改善）
