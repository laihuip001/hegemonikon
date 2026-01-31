# DRY違反検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- `JulesClient.create_session` メソッドのAPIコールロジックが `mekhane/symploke/run_specialists.py` の `create_session` 関数および `mekhane/symploke/run_remaining.py` の `create_session` 関数に複製されている（合計3箇所）。
- APIエンドポイント `https://jules.googleapis.com/v1alpha/sessions` が上記3ファイルにハードコードされている。
- HTTPヘッダー生成 `{"X-Goog-Api-Key": key, "Content-Type": "application/json"}` ロジックが3ファイルに分散している。
- `sourceContext` オブジェクト生成および `automationMode` 定義が3ファイルで複製されている。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
