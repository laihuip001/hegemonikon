# bare except処刑人 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- Critical: `extract_dispatch_info` 関数内 - `except Exception:` が使用されている
- Critical: `_load_projects` 関数内 - `except Exception:` が使用されている
- Critical: `_load_skills` 関数内 (YAML parse) - `except Exception:` が使用されている
- Critical: `_load_skills` 関数内 (Function level) - `except Exception:` が使用されている
- Critical: `get_boot_context` 関数内 (WAL loading) - `except Exception:` が使用されている
- Critical: `get_boot_context` 関数内 (BC violation) - `except Exception as e:` が使用されている
- Critical: `get_boot_context` 関数内 (n8n webhook) - `except Exception:` が使用されている
- Critical: `print_boot_summary` 関数内 - `except Exception:` が使用されている
- Critical: `main` 関数内 - `except Exception as e:` が使用されている

## 重大度
Critical
