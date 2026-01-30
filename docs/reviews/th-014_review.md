# 目的論的一貫性評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- `synedrion_review` メソッドが含まれており、汎用的なAPIクライアントと特定のビジネスロジック（Synedrion/Hegemonikón）が混在している。
- APIクライアントは「接続（Symplokē）」の責務に集中すべきであり、パースペクティブマトリックスのロードやプロンプト生成といった「作業（Ergasterion）」のロジックを持つべきではない。
- クライアントがドメインロジック（`mekhane.ergasterion.synedrion`）に依存しており、層間の結合度が高まっている。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
