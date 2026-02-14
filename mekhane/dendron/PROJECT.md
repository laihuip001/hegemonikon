---
name: "Dendron"
status: operational
phase: "運用中 — EPT フルマトリクス稼働"
updated: 2026-02-14
next_action: "REASON カバレッジ向上 (reason --apply)"
---

# Dendron Project Status

> 存在証明検証ツール — FEP の予測誤差最小化を存在次元に適用

## Current Phase

**EPT フルマトリクス運用中**: NF1 Surface + NF2 Structure + NF3 Function + BCNF Verification

## Milestones

- [x] MVP 実装 (checker, reporter, cli)
- [x] CLI パッケージ化
- [x] CI 統合 (pre-commit + dendron guard)
- [x] EPT フルマトリクス実装 (NF2/NF3/BCNF)
- [x] REASON 自動推定ツール (reason_infer.py)
- [x] CI モードで EPT 自動有効化
- [ ] REASON カバレッジ 30%+ 到達
- [ ] GitHub Actions 統合テスト
- [ ] 外部リポジトリ対応

## Current Metrics (2026-02-14)

```
Coverage: 100.0% (L1:45/L2:231/L3:61)
Purpose:  2637 ok, 0 weak, 21 missing
TypeHints: 3328/3753 (89%)
EPT:      5128/6207 (83%)
├── NF2:  2269/2454 (92.4%)
├── NF3:  1458/1952 (74.6%)
└── BCNF: 1401/1801 (78.0%)
REASON:   42/3110 (1.3%)
```

## Next Steps

1. `dendron reason mekhane/ --apply` で REASON カバレッジ向上
2. NF3/BCNF スコア改善 (関数分割リファクタリング)
3. GitHub Actions での自動実行設定
