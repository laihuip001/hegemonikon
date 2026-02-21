# 空入力恐怖症 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `extract_dispatch_info` にて `context` が空文字列の場合の早期リターンがない。空入力でも `AttractorDispatcher` の初期化（高コスト）が実行されてしまう。 (High)
- `_load_projects` にて `registry.yaml` が空ファイルの場合、`yaml.safe_load` が `None` を返し、続く `data.get()` で `AttributeError` が発生する。`try-except` で隠蔽されているが、`if not data:` で明示的にガードすべき。 (Medium)

## 重大度
High
