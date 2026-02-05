# コンテキスト喪失検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **構文コンテキストの喪失 (Critical)**: Pythonのキーワード引数構文（`key=value`）において、変数が引数名と同じである場合（`arg=arg`）、それを「冗長な自己代入（`var = var`）」と誤認して削除している箇所が複数存在する。これにより、必要な引数が渡されず、機能不全を引き起こしている。
    - `_request` メソッド: `json=json` が削除されており、APIリクエストにペイロードが含まれない。
    - `create_session` メソッド: `JulesSession` コンストラクタ呼び出しで `source=source` が削除されており、必須引数不足でクラッシュする。
    - `poll_session` メソッド: `UnknownStateError` 発生時に `session_id=session_id` が削除されており、例外のインスタンス化に失敗する。
    - `batch_execute` メソッド: `JulesResult` 作成時に `task=task` が削除されており、結果オブジェクトにタスク情報が含まれない。
- **データコンテキストの喪失 (High)**: `synedrion_review` メソッドにおいて、`str(r.session)` の中に "SILENCE" という文字列が含まれているかチェックしているが、`JulesSession` データクラスはメタデータのみを保持しており、レビューの出力内容（コンテンツ）を保持していない。AIは「セッションオブジェクトにレビュー結果のテキストが含まれている」という誤ったコンテキスト（幻覚）に基づいてコードを生成している。

## 重大度
- Critical

## 沈黙判定
- 発言（要改善）
