# bare except処刑人 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- Line 86: `extract_dispatch_info` 内で `except Exception` が使用されています (Critical)
- Line 144: `_load_projects` 内で `except Exception` が使用されています (Critical)
- Line 175: `_load_skills` 内のループで `except Exception` が使用されています (Critical)
- Line 207: `_load_skills` 内で `except Exception` が使用されています (Critical)
- Line 278: `get_boot_context` 内の WAL 読み込みで `except Exception` が使用されています (Critical)
- Line 322: `get_boot_context` 内の BC 違反ログ読み込みで `except Exception` が使用されています (Critical)
- Line 350: `get_boot_context` 内の n8n Webhook 送信で `except Exception` が使用されています (Critical)
- Line 393: `print_boot_summary` 内の定理推奨で `except Exception` が使用されています (Critical)
- Line 608: `main` 内で `except Exception` が使用されています (Critical)

## 重大度
Critical
