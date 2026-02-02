# Task: pymdp × Hegemonikón 統合

## Status: ✅ 完了 (Phase 1-3)

---

## Goal Decomposition

```
最終目標: pymdpを認知層として動作させる
  ← [3] noesis/boulesis/energeia APIテスト
  ← [2] HegemonikónAgentクラス作成
  ← [1] pymdpインストール確認
  ← 現在地
```

---

## Checklist

### Subgoal 1: pymdpインストール確認

- [x] `pip install inferactively-pymdp` ✅ v0.0.7.1
- [x] `from pymdp.agent import Agent` 成功確認 ✅

### Subgoal 2: HegemonikónFEPAgentクラス作成

- [x] `mekhane/fep/` ディレクトリ作成 ✅
- [x] `fep_agent.py` (291 lines) ✅
- [x] noesis/boulesis/energeia メソッド実装 ✅

### Subgoal 3: APIテスト

- [x] infer_states (O1 Noēsis) ✅
- [x] infer_policies (O2 Boulēsis) ✅
- [x] sample_action (O4 Energeia) ✅
- [x] 10/10 tests passing ✅

---

## Success Criteria

| 軸 | Must | Status |
|:---|:-----|:-------|
| 機能性 | pymdpインポート成功 | ✅ |
| 機能性 | API呼び出し成功 | ✅ |
| 品質 | エラーなく動作 | ✅ |
| 性能 | 1秒以内で推論完了 | ✅ (1.07s for 10 tests) |

---

*Created: 2026-01-28 / /plan v3.0 完了*
