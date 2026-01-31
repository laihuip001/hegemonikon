# 信念状態一貫性評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **成功判定のセマンティック不一致**: `JulesResult.is_success` は `session` オブジェクトが存在し、Pythonレベルの例外がない場合に `True` を返すが、API上のセッション状態が `FAILED` であっても `True` となる。これにより `synedrion_review` の失敗カウントが不正確になる。
- **幻覚的指標 ("SILENCE" Blindness)**: `synedrion_review` 内で `str(r.session)` に "SILENCE" が含まれるかを判定しているが、`JulesSession` データクラスにはレビュー結果のテキスト（出力）が含まれていないため、この判定は常に機能しない（またはプロンプト等に反応する偽陽性となる）。
- **並行性制御の矛盾**: `synedrion_review` は `MAX_CONCURRENT` サイズで手動バッチ処理を行っており、各バッチの完了を待機してから次を開始するため、バッチ間で並行性がゼロに落ちる「パイプラインドレイン」が発生している。`_global_semaphore` の目的である継続的なスループット維持と矛盾する。
- **例外型の不統一**: `poll_session` メソッドでのタイムアウト時に、ドメイン固有の `JulesError` サブクラスではなく、標準の `TimeoutError` を送出しており、エラーハンドリングの一貫性が損なわれている。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
