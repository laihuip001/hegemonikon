# テスト速度の時計師 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **外部依存 (High)**: `get_boot_context` 内で `urllib.request.urlopen("http://localhost:5678/...")` を同期的に呼び出しています。テスト環境で `n8n` が起動していない場合、5秒間のタイムアウト待ちが発生し、テストが著しく遅延・不安定になります。
- **遅いテストのリスク (Medium)**: `extract_dispatch_info` 内で `AttractorDispatcher` を初期化しています。これに伴い `AttractorAdvisor` が初期化され、モデルロード等の重い処理が走る可能性があります。DI (Dependency Injection) や遅延ロードの仕組みがなく、統合テストの速度低下要因となります。
- **I/O ボトルネック (Low)**: `_load_skills` は `.agent/skills/` 以下の全ファイルを走査・読み込みしています。スキル数が増加すると I/O コストが増大し、テスト実行時間に影響を与えます。

## 重大度
High
