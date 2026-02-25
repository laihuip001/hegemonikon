# NOT NULL推進者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `get_boot_context` (line 245) の引数 `context` が `Optional[str] = None` と定義されていますが、内部では `context or ""` (line 351) や `if not ki_context` (line 257) のように空文字と同等に扱われています。これは不要な NULL 許容であり、三値論理（None/Empty/Value）の罠を招きます。 (Medium)
- `print_boot_summary` (line 365) の引数 `context` も同様に不要な `Optional[str]` です。これらはデフォルト値を `""` (空文字) にすべきです。 (Medium)
- `_load_projects` (line 137) 内の `p.get("entry_point")` (line 173) はキーが存在しない場合に `None` を返します。`p.get("entry_point", {})` とすることで NULL チェック `if ep:` を回避し、常に辞書として扱うことで安全性を向上させることができます。 (Low)

## 重大度
Medium
