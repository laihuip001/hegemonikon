# fail-fast伝道者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **Critical**: `_load_projects` および `_load_skills` 内の `except Exception: pass` が、YAML 構文エラーなどの設定不備を完全に隠蔽している。無効な設定ファイルが存在する場合、修正の機会を奪い、正常な空状態として処理を進めてしまう。
- **Critical**: `extract_dispatch_info` が `AttractorDispatcher` の全例外を握りつぶしている。ディスパッチャに致命的なバグや設定ミスがあっても、呼び出し元は気づけず、機能不全のまま処理が継続される。
- **High**: `get_boot_context` が `mode` 引数を検証していない。不正なモード（例: Typo）が渡された場合、即座にエラーにならず、下流の関数で予期せぬ挙動を引き起こすか、デフォルト動作に倒れて気づかれない可能性がある。
- **High**: `postcheck_boot_report` が不正な `mode` に対してエラーを上げず、黙って "standard" モードの要件を適用している。検証ロジックが意図と異なる基準で実行され、誤った合格判定を出すリスクがある。

## 重大度
Critical
