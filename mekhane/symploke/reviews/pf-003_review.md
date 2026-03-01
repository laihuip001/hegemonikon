# in list vs in set審判 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- 複数回の探索が行われるループ内で、`tuple` (`("kalon", "aristos", "autophonos")`、`("ccl", "kernel", "pepsis")`、`("in_progress", "blocked")`) に対する `in` 判定が行われています。`tuple` への `in` 探索は O(N) の計算量がかかります。`set` (`{...}`) を使用して O(1) に最適化することを推奨します。

## 重大度
Medium
