# None恐怖症 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **Critical** (Line 109): `_load_projects` にて、`yaml.safe_load(registry_path.read_text(...))` の戻り値 `data` が `None` である可能性を考慮していない。`data.get("projects", [])` 呼び出し時に `AttributeError: 'NoneType' object has no attribute 'get'` が発生する。
- **High** (Line 174): `_load_skills` にて、`yaml.safe_load(parts[1])` の戻り値 `meta` が `None` である可能性を考慮していない。`meta.get("name", ...)` 呼び出し時に `AttributeError` が発生する。
- **Medium** (Line 227): `get_boot_context` にて、`handoffs_result["latest"].metadata` へのアクセス時、`.metadata` 自体が `None` である可能性を考慮せず `.get()` を呼び出している。
- **Medium** (Line 441): `generate_boot_template` にて、`h.metadata` の存在確認 (`hasattr`) はあるが、値が `None` である場合の考慮がなく、`.get()` 呼び出し時に `AttributeError` が発生する可能性がある。
- **Medium** (Line 457): `generate_boot_template` にて、`ki.metadata` に対しても同様に、値が `None` である場合の考慮がなく、`.get()` 呼び出し時に `AttributeError` が発生する可能性がある。
- **Low** (Line 66): `extract_dispatch_info` の引数 `context` は `str` 型ヒントだが、呼び出し元の `get_boot_context` では `Optional[str]` を許容しており、`None` が渡される可能性がある。

## 重大度
High
