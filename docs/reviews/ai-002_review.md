# Mapping ハルシネーション検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- `_request` メソッド: `session.request` 呼び出しにおいて `json` 引数が欠落しており、リクエストボディが送信されない（実在しない呼び出しシグネチャの使用）。
- `create_session` メソッド: `JulesSession` コンストラクタの呼び出しにおいて、必須引数 `source` が欠落しており、実行時に `TypeError` が発生する（実在しないコンストラクタシグネチャの使用）。
- `poll_session` メソッド: `UnknownStateError` の初期化において、必須引数 `session_id` が欠落しており、例外送出時に `TypeError` が発生する（実在しないコンストラクタシグネチャの使用）。
- `synedrion_review` メソッド: `str(r.session)` に "SILENCE" が含まれるかチェックしているが、`JulesSession` オブジェクトには出力データを保持するフィールドが存在せず、このチェックは機能しない（データモデルのハルシネーション）。

## 重大度
- Critical

## 沈黙判定
- 発言（要改善）
