# Logic Gates: 判断決定木

> **消化元**: files.zip → logic-gates.md (SKILL v4.0 参照)
> **消化日**: 2026-02-12
> **第一原理**: 「判断の曖昧さを構造的に排除する」 = Zero Entropy の実装
> **HGK 対応**: /mek, /dia, /dev, BC-14 FaR

---

## 使い方

設計/実装判断で曖昧さが生じたとき、該当する Gate を参照して決定する。
Zero Entropy の「Draft A/B → Propose → Lock」と組み合わせて使用。

---

## Gate 一覧

### G01: Speed vs Quality

```
Deadline
├─ < 24h → SPEED (95% cover is OK)
├─ < 1 week → BALANCE (98%)
└─ > 1 week → QUALITY (100% aim)
```

### G02: Security vs Usability

```
Handles PII / Auth?
├─ YES → SECURITY (no compromise)
└─ NO → User-facing?
         ├─ YES → USABILITY priority
         └─ NO → BALANCED (internal)
```

### G03: Refactor vs Rewrite

```
Age > 5y AND Coverage < 30%?
├─ YES → REWRITE advised
└─ NO → Age > 3y OR TechDebt > 40%?
         ├─ YES → INCREMENTAL_REFACTOR
         └─ NO → MAINTAIN
```

### G04: Undefined Variable

```
Variable source?
├─ User input → Validate + Default + Explicit error
├─ Config file → Schema validation (Pydantic/Zod)
├─ Environment → os.getenv() + require check
└─ Computed → Null guard + log
```

### G05: Testing Mandate

```
Change type?
├─ Bug fix → regression test REQUIRED
├─ New feature → unit + integration test
├─ Refactor → existing tests must pass (no behavior change)
└─ Config change → smoke test
```

### G06: Dependency Decision

```
Existing internal solution?
├─ YES → USE IT (NIH 禁止)
└─ NO → Maintained (1y 以内)?
         ├─ NO → 代替を探す
         └─ YES → License compatible?
                  ├─ NO → REJECT
                  └─ YES → Size < 100KB?
                           ├─ YES → ACCEPT
                           └─ NO → Review needed
```

### G07: Error Handling

```
Error type?
├─ Expected (validation) → return Result/Either
├─ Recoverable (network) → retry with backoff
├─ Fatal (OOM, disk full) → crash fast + alert
└─ Unknown → log + generic error + DON'T swallow
```

### G08: API Versioning

```
Breaking change?
├─ NO → PATCH (no version bump)
└─ YES → Deprecation period set?
          ├─ YES → MINOR version + deprecation header
          └─ NO → MAJOR version + migration guide
```

### G09: Logging Decision

```
Data?
├─ Contains PII → NEVER log (I-2)
├─ Contains secrets → NEVER log (I-3)
├─ Error context → ERROR level + structured
├─ Business event → INFO level + audit trail
└─ Debug → DEBUG level (prod では無効化)
```

### G10: Caching Decision

```
Data freshness?
├─ Real-time required → NO CACHE
├─ Stale OK (< 5min) → TTL cache + staggered
├─ Stale OK (< 1h) → CDN / edge cache
└─ Rarely changes → Long TTL + invalidation hook
```

---

## HGK 固有 Gate (消化時に追加)

### G11: BC 深度選択

```
タスクの重要度?
├─ 単純実行 → L0 Bypass (Always-On BC のみ)
├─ 実装・軽微判断 → L1 Quick
├─ 設計・分析 → L2 Standard
└─ 本質問題 → L3 Deep (全 BC)
```

### G12: 消化 vs 参照

```
外部素材?
├─ HGK の原理と同型 → ABSORB (/eat で消化)
├─ 独立した参照価値 → REFERENCE (reference/ に配置)
└─ HGK と矛盾 → REJECT (理由を記録)
```

### G13: CCL 複雑度判定

```
CCL 式のポイント?
├─ < 15pt → Standard (問題なし)
├─ 15-30pt → Standard (通常)
├─ 30-45pt → Enhanced (注意)
└─ > 60pt → WARNING (分割必要)
```

---

*Logic Gates v1.0 — SKILL v4.0 消化 + HGK 固有 Gate 追加 (2026-02-12)*
