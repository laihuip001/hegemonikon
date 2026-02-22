# early return推進者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **`get_boot_context` 内の深いネスト (Medium)**: `if mode != "fast":` ブロック内の WAL 読み込みロジックにおいて、`try` ブロックの中で `if prev_wal`、`if incomplete`、`for` ループと続き、ネストが深さ5に達しています。このブロックを独立した関数 (`_load_wal_context` 等) に切り出し、ガード節 (`if mode == "fast": return`) を使用して平坦化すべきです。
- **`_load_projects` 内の複雑な条件分岐 (Medium)**: プロジェクト出力ループにおいて、`if ep...` の中に `if cli:` があるなど、ネストが深さ4になっています。行生成ロジックを関数化し、条件を満たさない場合に早期リターンすることで可読性を向上させることができます。
- **`_load_skills` の解析ロジック (Medium)**: YAML Frontmatter の解析において、`if` ブロック内に `try-except` があり、視線の移動が激しくなっています。解析関数を分離し、ガード節を活用して構造を整理すべきです。
- **`_load_skills` のロジック重複 (Low)**: `content.split("---", 2)` の処理がメタデータ取得と本文取得で重複しており、無駄なネストを生んでいます。

## 重大度
Medium
