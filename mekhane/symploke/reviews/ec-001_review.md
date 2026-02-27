<!-- PROOF: [L2/Quality] <- mekhane/symploke/ -->
# 空入力恐怖症 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` において、`yaml.safe_load` は空ファイルに対して `None` を返します。続く `data.get("projects", [])` で `AttributeError` が発生し、例外処理に落ちます。明示的な `if data is None:` チェックが必要です。(High)
- `_load_skills` において、Frontmatter が空（`---` のみ等）の場合、`yaml.safe_load` が `None` を返し、`meta.get` で `AttributeError` が発生します。(Medium)
- `extract_dispatch_info` において、`context` が空文字列の場合のガード節がありません。空入力でも `AttractorDispatcher` が起動されます。(Low)

## 重大度
High
