# ハードコードパス検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- `BASE_URL` が `https://jules.googleapis.com/v1alpha` に固定されており、コンストラクタや環境変数から変更できない。これにより、テスト時のモックサーバー利用や、将来的なAPIバージョンの変更、異なる環境（Stagingなど）への切り替えが困難になっている。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
