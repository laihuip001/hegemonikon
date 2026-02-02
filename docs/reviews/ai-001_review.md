# 命名ハルシネーション検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **実在しないAPIエンドポイント**: `https://jules.googleapis.com/v1alpha` というURLが定義されていますが、これはGoogle Cloudの公開APIとして実在しません（Resource Hallucination）。外部サービスへの依存がハルシネーションに基づいています。
- **言語ルールのハルシネーションによるコード破壊**: `_request`, `create_session`, `poll_session`, `batch_execute` メソッド内において、`# NOTE: Removed self-assignment: ...` というコメントと共に、有効なキーワード引数渡し（`json=json`, `source=source`, `session_id=session_id`, `task=task`）が削除されています。AIが「キーワード引数への変数渡し」を「冗長な自己代入」と誤って認識（ハルシネーション）した結果、必須引数の欠落による `TypeError` やデータの消失（POSTボディの欠落など）を引き起こしています。
- **型ヒントの誤用**: `synedrion_review` メソッドの引数 `progress_callback` において、`typing.Callable` ではなく組み込み関数の `callable` が型ヒントとして使用されています。実在する名前ですが型としての用法は不適切です。

## 重大度
- Critical

## 沈黙判定
- 発言（要改善）
