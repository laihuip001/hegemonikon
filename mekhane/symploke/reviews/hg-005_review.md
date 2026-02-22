# 定理整合性監査官 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- (Medium) 関数 `get_boot_context` が約128行あり、100行制限を超過している (Reduced Complexity違反)
- (Medium) 関数 `generate_boot_template` が約108行あり、100行制限を超過している (Reduced Complexity違反)
- (Medium) 関数 `postcheck_boot_report` が約127行あり、100行制限を超過している (Reduced Complexity違反)
- (Medium) 関数 `_load_projects` に必須の `# PURPOSE:` コメントが欠落している (Project Convention違反)
- (Low) インラインコメントやセクションヘッダに日本語が多用されており、「コードコメントは英語」という規約に違反している (Consistency Over Cleverness違反)

## 重大度
Medium
