# ログレベル審議官 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言

## 発見事項
- `get_boot_context` 関数内の `logging.debug("BC violation loading skipped: %s", e)` は、例外発生による機能スキップ（BC違反情報の欠落）を示しています。この情報はユーザーにとって重要であり、デフォルトで隠蔽される `debug` レベルではなく、状況を適切に伝える `info` レベル（または `warning`）が適切です。これは「info は情報、混乱はカオス」の原則に照らし、意図しない情報の隠蔽を防ぐための指摘です。

## 重大度
Low
