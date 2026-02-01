# デッドコード検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- `JulesClient._session` (@property): クラス内で定義されていますが、一度も使用されていません。また、アクセス時に新しい `ClientSession` を作成し、クローズする手段がないため、リソースリーク（CWE-772）のリスクがあります。
- `with_retry` デコレータ: `for` ループ後の `raise last_exception` は到達不能コードです。ループ内の最後の試行で例外が再送出されるため、ここには到達しません。
- `main` 関数: ライブラリコード内にテスト用CLIが含まれています。これはデッドコードではありませんが、本番環境では不要なコードであり、テストファイルに分離すべきです。
- `batch_execute` メソッド: `use_global_semaphore=True`（デフォルト）の場合、`max_concurrent` 引数は無視され、使用されません。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
