# None恐怖症 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **`_load_projects` における `yaml.safe_load` の None 返却未考慮 (High)**
  - `yaml.safe_load` は空ファイルに対して `None` を返すが、その直後に `data.get("projects", [])` が実行されている。
  - `AttributeError: 'NoneType' object has no attribute 'get'` が発生するリスクがある。

- **`_load_skills` における `yaml.safe_load` の None 返却未考慮 (High)**
  - 同様に `meta = yaml.safe_load(parts[1])` が `None` になる可能性があり、`meta.get(...)` でクラッシュする。

- **`get_boot_context` における `.metadata` 属性の None 未考慮 (High)**
  - `handoffs_result["latest"].metadata.get("primary_task", "")` において、`metadata` 属性自体が `None` である可能性が考慮されていない。
  - オブジェクトが存在しても `metadata` が未設定の場合にクラッシュする。

- **`generate_boot_template` における `.metadata` 属性の None 未考慮 (High)**
  - `h.metadata.get(...)` および `ki.metadata.get(...)` において、`metadata` が `None` の場合のガードがない。
  - `hasattr` チェックのみでは不十分（属性が存在しても値が `None` の場合がある）。

## 重大度
High
