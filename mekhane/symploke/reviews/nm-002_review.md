# 動詞/名詞の裁定者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- 変数 `gpu_ok` (bool): 形容詞的。名詞 `gpu_status` または `is_gpu_available` が望ましい。(Medium)
- 変数 `active` (list): 形容詞。名詞 `active_projects` が望ましい。(Medium)
- 変数 `dormant` (list): 形容詞。名詞 `dormant_projects` が望ましい。(Medium)
- 変数 `archived` (list): 分詞（形容詞）。名詞 `archived_projects` が望ましい。(Medium)
- 変数 `latest` (obj): 形容詞。名詞 `latest_handoff` が望ましい。(Medium)
- 変数 `done` (int): 分詞。名詞 `done_count` が望ましい。(Medium)
- 変数 `incomplete` (list): 形容詞。名詞 `incomplete_tasks` が望ましい。(Medium)
- 変数 `unchecked` (int): 形容詞。名詞 `unchecked_count` が望ましい。(Medium)
- 変数 `checked` (int): 分詞。名詞 `checked_count` が望ましい。(Medium)
- 変数 `wal_filled` (bool): 分詞句。名詞 `is_wal_filled` または `wal_fill_status` が望ましい。(Medium)
- 変数 `all_passed` (bool): 文。名詞 `all_checks_passed` が望ましい。(Medium)
- 変数 `fill_remaining` (int): 動詞句的。名詞 `remaining_fills` が望ましい。(Medium)

## 重大度
Medium
