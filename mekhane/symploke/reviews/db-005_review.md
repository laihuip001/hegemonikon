# NOT NULL推進者 レビュー

<!-- PROOF: [L2/Mekhane] <- mekhane/symploke/reviews/ DB-005によるレビュー -->

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `get_boot_context` 関数の `context` 引数が `Optional[str] = None` と定義されています。関数内部では `context or ""` や `ki_context = context` のように扱われており、三値論理（None, Empty, String）を持ち込む必要がありません。デフォルト値を `""` とし、型を `str` に単純化すべきです。(Medium)
- `print_boot_summary` 関数の `context` 引数も同様に `Optional[str] = None` です。これも `str = ""` にすべきです。(Medium)
- `_load_projects` 関数内で `yaml.safe_load` を使用していますが、対象ファイルが空の場合 `None` が返ります。その直後に `data.get("projects", [])` を呼び出しているため、`AttributeError` が発生します（現在は広範な `try-except` で捕捉されていますが、NULL の罠です）。`yaml.safe_load(...) or {}` のように NULL ガードを入れるべきです。(Medium)
- `_load_skills` 関数内でも同様に `yaml.safe_load` の戻り値が `None` になる可能性があり、`meta.get(...)` で失敗する可能性があります。(Medium)

## 重大度
Medium
