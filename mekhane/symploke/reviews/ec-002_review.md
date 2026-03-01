# None恐怖症 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- yaml.safe_load() の戻り値が None になる可能性への考慮漏れ:
  - 120行目付近: `data = yaml.safe_load(...)` の直後に `projects = data.get("projects", [])` を呼んでおり、`data` が `None` (空の YAML ファイルなど) の場合に `AttributeError` が発生する。
  - 228行目付近: `meta = yaml.safe_load(parts[1])` の直後に `name = meta.get("name", ...)` などを呼んでおり、`meta` が `None` (Frontmatter が空など) の場合に `AttributeError` が発生する。
- 308行目付近: `handoffs_result["latest"].metadata` が `None` である可能性への考慮漏れ:
  - `ki_context = handoffs_result["latest"].metadata.get("primary_task", "")` にて、`metadata` が辞書ではなく `None` の場合に `AttributeError` が発生する。
- 605行目付近: `h.metadata` が `None` である可能性への考慮漏れ:
  - `title = h.metadata.get("primary_task", h.metadata.get("title", "Unknown"))` にて、`h.metadata` が `None` の場合に `AttributeError` が発生する。
- 623行目・624行目付近: `ki.metadata` が `None` である可能性への考慮漏れ:
  - `name = ki.metadata.get("ki_name", "Unknown")` や `summary = ki.metadata.get("summary", "N/A")` にて、`ki.metadata` が `None` の場合に `AttributeError` が発生する。

## 重大度
High
