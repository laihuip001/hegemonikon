# NOT NULL推進者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- **`JulesResult` クラスの `session` フィールドの不要な NULL 許可 (Medium)**
  現状、`session: JulesSession | None = None` と定義されているが、`batch_execute` メソッド内の実装（`bounded_execute`）では成功時も例外発生時も必ず `JulesSession` インスタンス（例外時はFAILED状態のダミー）が設定される。コードの意図として `None` になるケースが存在しないにもかかわらず、型定義上で `None` を許容しているため、利用側で不要なNULLチェック（`is_success` プロパティ内の `self.session is not None` など）が必要になっている。また、デフォルト引数 `None` により、セマンティクス上不完全な `JulesResult` インスタンスが作成可能になってしまっている。これは「不要なNULL許可」に該当する。

## 重大度
Medium
