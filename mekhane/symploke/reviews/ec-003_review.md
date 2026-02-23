# 境界値テスター レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **詳細モードのHandoff最小件数不整合 (Medium)**:
    - `generate_boot_template` は `all_handoffs[:10]` で最大10件に制限している。
    - `postcheck_boot_report` の `detailed` モードは `expected_h = 10` を要求する。
    - システム内の Handoff が 9件以下の場合（新規環境や履歴不足時）、テンプレートは9件しか生成されず、ポストチェックは10件未満のため必ず **FAIL** する。0〜9件の境界値で動作不能になる。

- **マジックナンバーによるスコア歪曲 (Low)**:
    - `postcheck_boot_report` 内の `max(fill_remaining, 25)` という固定値25。
    - 実際のテンプレートのフィル箇所数が25未満の場合でも分母が25に固定されるため、進捗率の計算が不正確になる。

- **散在するハードコードされた境界値 (Low)**:
    - `[:3]` (alternatives), `[:5]` (KI/files), `[:50]` (summary), `[:200]` (context) など、リテラルによるスライスが多数存在。
    - これらは `MAX_ALTERNATIVES = 3` のように定数化されるべき。特に `[:50]` で切った後に `...` を足すと53文字になるなど、厳密な境界制御が曖昧。

- **Phase範囲の固定 (Low)**:
    - `range(7)` (0〜6) がハードコードされている。プロジェクトのPhase定義が変更された場合や、1-based (1〜7) の場合に off-by-one エラーとなるリスクがある。

## 重大度
Medium
