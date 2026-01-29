# ハードコードパス検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- `BASE_URL` が "https://jules.googleapis.com/v1alpha" に固定されている。環境（ステージング、本番）やAPIバージョンの変更に対応できない構造になっている。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
