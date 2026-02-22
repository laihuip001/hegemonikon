# NOT NULL推進者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `get_boot_context` の引数 `context: Optional[str] = None` は不要なNULL許可である。関数内部では `if not ki_context` (None または空文字) として扱われており、空文字列 `""` と `None` の区別がない。NULL状態を持たせず `str` 型 (デフォルト `""`) に統一すべきである。(Medium)
- `print_boot_summary` の引数 `context: Optional[str] = None` も同様に不要なNULL許可である。呼び出し元である `main` 関数では `argparse` から `None` が渡りうるが、境界で `""` に変換して内部ロジックから `None` を排除すべきである。(Medium)

## 重大度
Medium
