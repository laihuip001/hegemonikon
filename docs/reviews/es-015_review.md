# オンボーディング障壁検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **ドメイン固有の専門用語 (Cognitive Barrier)**: `synedrion_review` メソッド内で "Hegemonikón theorem grid", "480 orthogonal perspectives", "20 domains x 24 axes" といった用語が説明なしに使用されています。新規参加者にとって、これらが何を指すのか、なぜ必要なのかを理解するのは困難です。参照ドキュメントへのリンクが必要です。
- **誤解を招くCLIテスト (Misleading Tooling)**: `main` 関数の `--test` フラグは "Run connection test" と説明されていますが、実際にはクラスを初期化して設定を表示するだけで、APIへの接続確認（ping等）を行っていません。ユーザーは「接続成功」と誤認する可能性があります。
- **デフォルト設定の前提 (Configuration Assumption)**: `MAX_CONCURRENT = 60` が "Ultra plan limit" としてハードコードされています。Ultraプランを持たない開発者がデフォルトで実行すると、即座にレート制限にかかる可能性があります。デフォルトは安全な低い値（例: 5-10）にし、設定で引き上げる形が望ましいです。
- **隠れた依存関係 (Hidden Dependency)**: `mekhane.ergasterion.synedrion` が `synedrion_review` 内で動的にインポートされています。トップレベルでのインポートでないため、依存関係が直感的に把握しづらいです。
- **過去の経緯への依存 (Contextual Dependency)**: "cl-003 review", "ai-006 review" といった特定のレビューIDへの参照が散見されます。これらにアクセスできない、または知らない参加者にとってはノイズとなり、コードの意図（Why）を理解する助けになりません。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
