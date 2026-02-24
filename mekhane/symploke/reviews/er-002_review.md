# bare except処刑人 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- Line 96: `extract_dispatch_info` 内で `except Exception:` を使用 (Critical)
- Line 188: `_load_projects` 内で `except Exception:` を使用 (Critical)
- Line 231: `_load_skills` 内で `except Exception:` を使用 (Critical)
- Line 271: `_load_skills` 内で `except Exception:` を使用 (Critical)
- Line 362: `get_boot_context` 内で `except Exception:` を使用 (Critical)
- Line 410: `get_boot_context` 内で `except Exception as e:` を使用 (Critical)
- Line 444: `get_boot_context` 内で `except Exception:` を使用 (Critical)
- Line 492: `print_boot_summary` 内で `except Exception:` を使用 (Critical)
- Line 889: `main` 内で `except Exception as e:` を使用 (Critical)

## 重大度
Critical
