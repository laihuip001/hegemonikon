# 実験ノート

> **Pythōsis 実験・PoC**

---

## 2026-01-31: @repeat テスト

```ccl
@repeat(/u+*^/noe, 2)
```

**結果**: 1回目と2回目で異なる洞察が得られた。反復は深化を生む。

---

## 2026-02-01: Lambda 正式化

`L:[x]{WF}` を CCL 正式仕様として採用 (operators.md v6.52)。

**次の検証予定**:
- `L:[x]{/noe+{x}}` — 引数付き Lambda 実行
- `@retry(3, on_fail=L:{/dia^})` — 高階マクロへの渡し

---

## 次の実験候補

- [ ] `@reduce(*, /o, /s, /h, /p, /k, /a)` — 6 Hub 統合
- [ ] `@cycle(/s+, /dia-, until=?h2>0.9)` — 収束テスト

---

*Experiments Log*
