# FEP Agent 拡張タスク

## 概要

arXiv:2412.10425 論文から吸収したパターンを Hegemonikón FEP に実装

## タスク

- [x] **Phase 1**: 2-step政策horizon導入
  - [x] `fep_agent.py` に `policy_len=2` 追加
  - [x] `inference_horizon=1` 明示設定
  - [x] テスト `test_policy_len_is_2` 追加

- [x] **Phase 2**: A行列永続化
  - [x] `persistence.py` 作成
  - [x] `save_learned_A()` メソッド実装
  - [x] `load_learned_A()` メソッド実装
  - [x] ラウンドトリップテスト追加

- [x] **Phase 3**: Dirichlet更新
  - [x] `update_A_dirichlet()` メソッド実装
  - [x] 学習率パラメータ (η=50.0)
  - [x] テスト追加

- [ ] **Phase 4**: ワークフロー統合 (後続対応)
  - [ ] `/bye` で A行列保存
  - [ ] `/boot` で A行列読込

## 完了条件

- [x] 既存10テスト維持
- [x] 新規9テスト追加・全通過 (19 passed)

## 結果

✅ **コミット完了**: `5df3fad1`
