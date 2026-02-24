# RESTの弁護士 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- エンドポイント `http://localhost:5678/webhook/session-start` に動詞 `start` が含まれている。リソース名 `sessions` (POST) や `session_events` などに変更すべき。 (Medium)

## 重大度
Medium
