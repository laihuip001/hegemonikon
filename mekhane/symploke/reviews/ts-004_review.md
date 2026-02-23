# テスト速度の時計師 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `get_boot_context` 内で `urllib.request.urlopen` を使用した同期的な外部ネットワーク呼び出し（`http://localhost:5678`）があり、最大5秒間のブロッキングが発生する可能性がある。(High)
- `load_attractor` 等の軸ローダーにおいて、`HegemonikónFEPAgentV2` や `TheoremAttractor` などの重量級モデル初期化が含まれており、最大30秒のタイムアウトが設定されているため、テスト実行時間を著しく損なう。(High)
- `_load_skills` および `_load_projects` において、ループ内での同期ファイル読み込みが行われており、ファイル数増加に伴う速度低下のリスクがある。(Medium)

## 重大度
High
