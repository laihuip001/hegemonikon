# early return推進者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **`_load_projects` 関数内の深いネスト（最大7段）**
  `try` -> `if` -> `for p in projects` -> `if/elif` -> `for cat_name, cat_projects in categories.items()` -> `if not cat_projects` -> `for p in cat_projects` -> `if len(summary) > 50` などと非常に深いネストが発生しています。`registry_path.exists()` などのチェックで早期リターンを徹底し、プロジェクトのカテゴリ分類や整形処理を別の関数に切り出すことで、ネストを浅く保つことができます。(Medium)
- **`_load_skills` 関数内の深いネスト（最大5段）**
  `try` -> `for skill_dir in sorted(...)` -> `if content.startswith("---")` -> `if len(parts) >= 3` -> `try` などのネストがあります。各スキルの解析処理（メタデータ抽出など）を別関数に抽出するか、guard clause を用いて `if not content.startswith("---"): continue` のように早期に次のループへ進むことでネストを削減できます。(Medium)
- **`get_boot_context` 関数内の深いネスト（最大5段）**
  WAL関連の処理内で `if mode != "fast"` -> `try` -> `if prev_wal` -> `if prev_wal.blockers` や `if incomplete` -> `for e in incomplete[:5]` のようなネスト構造が見られます。特定の軸（WAL処理など）のロードを独立した関数（例: `_load_wal_context`）に切り出すことで、主関数のネストを抑え可読性を向上させることができます。(Medium)

## 重大度
Medium
