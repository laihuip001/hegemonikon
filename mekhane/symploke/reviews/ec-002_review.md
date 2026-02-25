# None恐怖症 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- (High) `_load_projects` (91行目): `yaml.safe_load` が空ファイルに対して `None` を返す可能性があり、直後の `data.get` で `AttributeError` が発生する。
- (Medium) `_load_skills` (159行目): `yaml.safe_load` が空のフロントマターに対して `None` を返す可能性があり、直後の `meta.get` で `AttributeError` が発生する。
- (Low) `extract_dispatch_info` (64行目): 引数 `context` に `None` が渡された場合のガード処理が存在しない（呼び出し元で `Optional[str]` が許容されているため潜在的なリスク）。
- (Low) `generate_boot_template` (373行目): `h.metadata` が `None` である可能性を考慮せず `.get` を呼び出している（`hasattr` チェックのみでは不十分）。

## 重大度
High
