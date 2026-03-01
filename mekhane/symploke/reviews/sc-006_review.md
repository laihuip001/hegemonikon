# 入力検証推進者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` (L120): `yaml.safe_load(registry_path.read_text(encoding="utf-8"))` の戻り値に対する型検証がない。空ファイルやリストなど、辞書(`dict`)以外のYAMLが渡された場合、直後の `data.get("projects", [])` で `AttributeError` が発生する可能性がある。
- `_load_skills` (L228): `yaml.safe_load(parts[1])` の戻り値に対する型検証がない。YAMLが辞書以外の場合、直後の `meta.get("name", ...)` で `AttributeError` が発生する可能性がある（`except Exception: pass` で握り潰されるが、検証漏れによる予期せぬ挙動につながる）。
- `postcheck_boot_report` (L721): `path.read_text(encoding="utf-8")` の直前に `path.exists()` でファイルの存在確認はしているが、外部から渡された `report_path` がディレクトリを指している場合（例えば `/tmp` など）、`read_text` 呼び出し時に `IsADirectoryError` が発生する。`path.is_file()` による検証が必要。

## 重大度
High