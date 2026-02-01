# 再試行ロジック評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **Jitter（ゆらぎ）の欠如**: `with_retry` デコレータおよび `poll_session` メソッドのバックオフ計算において、ランダムな Jitter（ゆらぎ）が含まれていません。複数の同時リクエストが失敗した場合、同期的に再試行が行われ、再度レート制限に抵触する「Thundering Herd」問題を引き起こすリスクがあります。
- **Retry-After ヘッダー解析の堅牢性**: `_request` メソッド内で `Retry-After` ヘッダーを `int()` で変換していますが、数値以外の値が返された場合に `ValueError` が発生し、再試行ロジックが中断される可能性があります（`ValueError` は再試行対象外のため）。

## 重大度
- Low

## 沈黙判定
- 発言（要改善）
