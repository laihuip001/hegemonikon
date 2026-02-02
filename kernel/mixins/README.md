# Mixin 定理群 (Pythōsis B2)

> **Kernel Doc Index**: [taxis](../taxis.md) | [mixins](./README.md) ← 📍

---

## 概要

Mixin は「能力の合成」を実現する設計パターン。Python の多重継承・デコレータに着想を得て、CCL に移植。

## 設計原則

1. **合成優先 (Composition over Inheritance)** — 継承より合成
2. **単一責任 (Single Capability)** — 各 Mixin は1つの能力
3. **順序依存 (Order Matters)** — 適用順序が結果に影響

## 適用構文

```ccl
@with(Mixin1, Mixin2) target
# ≡ Mixin1(Mixin2(target))
```

## 標準 Mixin

| Mixin | ファイル | 機能 |
|:------|:---------|:-----|
| Tracing | [tracing.md](tracing.md) | 実行ログ記録 |
| Caching | [caching.md](caching.md) | 結果キャッシュ |
| Retry | [retry.md](retry.md) | 失敗時リトライ |
| Validation | [validation.md](validation.md) | 事前/事後検証 |
| Timing | [timing.md](timing.md) | 実行時間計測 |

---

*Pythōsis B2 | 2026-02-01*
