# FEP ワークフロー統合タスク

## 目標

pymdp FEP Agent を Hegemonikón ワークフローに完全統合する。

---

## タスクリスト

- [x] Phase 1-3: FEP Agent コア実装 (fep_agent.py, persistence.py, Dirichlet)
- [x] 19テスト全通過確認
- [x] Phase 4.1: `/bye.md` に Step 3.9 (A行列保存) 追加
- [x] Phase 4.2: `/boot.md` に Step 6.5 (A行列読込) 追加
- [x] /noe 分析: `/noe.md`, `/bou.md` への追加は不要と判定
- [x] Phase 4.5: テスト実行 + 検証完了

---

## 進捗

| Phase | Status | Notes |
|:------|:-------|:------|
| 1-3 | ✅ 完了 | 19テスト通過 |
| 4.1 | ✅ 完了 | bye.md Step 3.9 |
| 4.2 | ✅ 完了 | boot.md Step 6.5 |
| 4.3 | ❌ 不要 | /noe 分析で削除 |
| 4.4 | ❌ 不要 | /noe 分析で削除 |
| 4.5 | ✅ 完了 | 19テスト通過 |
