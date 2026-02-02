# FEP フル統合タスク (2026-01-28)

## 目標

pymdp を /noe と /bou ワークフローに統合し、O1 → O2 → O4 の FEP フローを完成する。

## Phase 1: /noe 統合

- [x] fep_bridge.py 作成 (ワークフロー呼び出し用ラッパー) ✅ 17/17 tests
- [x] /noe PHASE 5 で信念エントロピーを出力 (O1 SKILL.md に既存)
- [x] テスト追加 ✅ test_fep_bridge.py

## Phase 2: /bou 統合

- [x] /bou PHASE 5 で政策分布 q_pi を出力 (O2 SKILL.md に既存)
- [x] Expected Free Energy に基づく優先順位補強
- [x] fep_bridge.boulesis_analyze() 使用例追加

## Phase 3: 検証

- [x] 統合テスト実行 ✅ 36/36 passed
- [x] SKILL.md ドキュメント更新 ✅ O1, O2 両方
- [x] コミット ✅ hegemonikon (cba156a5), oikos (fda5c6f4)
