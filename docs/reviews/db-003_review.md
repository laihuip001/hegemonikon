# SELECT * 反対者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- **Pollingにおける不要な全量取得**: `poll_session` メソッド内で `get_session` をループ呼び出ししていますが、ここでは `session.state` しか判定に使用していません。`get_session` はAPIからセッション情報の全量（`outputs` や `sourceContext` など含む）を取得するため、完了待ちのポーリング中において帯域とリソースの無駄遣い（SELECT * 相当）が発生しています。 (Severity: Medium)
- **APIレスポンスのフィールド指定欠如**: `get_session` 内の `_request("GET", ...)` において、必要なフィールドのみを取得するパラメータ（例: `?fields=state,name,error`）が指定されていません。Google API標準であれば `fields` パラメータが利用可能である可能性が高いですが、現状は常に全カラムを取得しています。 (Severity: Medium)
- **Synedrionレビューのパースペクティブ全生成**: `synedrion_review` メソッドにおいて、`matrix.all_perspectives()` で全パースペクティブを生成した後に `domains` や `axes` でフィルタリングしています。不要なオブジェクト生成を避けるため、最初から必要なパースペクティブのみを取得すべきです。 (Severity: Low)

## 重大度
Medium
