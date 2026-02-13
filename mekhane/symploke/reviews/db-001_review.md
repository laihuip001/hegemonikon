# N+1検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `poll_session` メソッド内で `while` ループを使用し、完了するまで `get_session` を繰り返し呼び出しています (Critical)
- `synedrion_review` メソッド内で `for` ループを使用し、バッチごとに `batch_execute` を呼び出しています (Critical)

## 重大度
Critical
