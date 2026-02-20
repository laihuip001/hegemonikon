# NOT NULL推進者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `get_boot_context` および `print_boot_summary` の引数 `context` が `Optional[str] = None` となっている。
  - 文字列が欠如している状態は空文字列 `""` で表現可能であり、`None` を許容する必要がない (Null Object Pattern / Empty String)。
  - `Optional` 型ヒントにより、関数内部で不要な `None` チェックや `context or ""` のようなガード節が必要になっている。
  - Medium

- `main` 関数内の `argparse` 定義で `context` 引数のデフォルト値が明示されていないため、指定がない場合に `None` が混入する。
  - `default=""` を指定することで、プログラム全体を通して `context` を非NULL (`str`) として扱える。
  - Medium

- `_load_projects` 内で `ep = p.get("entry_point")` が使用されており、キーが存在しない場合に `None` が変数 `ep` に代入される。
  - `p.get("entry_point", {})` とすることで、`None` の変数を排除できる。
  - Low

## 重大度
Medium
