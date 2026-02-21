# None恐怖症 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **_load_projects**: `yaml.safe_load` が空ファイルを読み込んだ場合 `None` を返し、後続の `data.get()` で `AttributeError` が発生する (High)
- **_load_skills**: フロントマターが空の場合 `yaml.safe_load` が `None` を返し、`meta.get()` でクラッシュする (High)
- **extract_dispatch_info**: 引数 `context` が `str` と定義されているが、呼び出し元では `Optional[str]` が渡りうるため型不整合および潜在的 `None` 参照のリスクがある (High)

## 重大度
High
