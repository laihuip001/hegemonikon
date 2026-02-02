# Project Pythōsis: Python Philosophy Ingestion

> **Status**: Phase B (Concept Expansion) Completed
> **Date**: 2026-02-01

---

## 1. 文脈と目的 (Πύθων + ὄσις)

**Project Pythōsis** は、Python の設計思想（Zen of Python）や標準ライブラリの強力な抽象化パターン（Decorators, Iterators, Context Managers）を、Hegemonikón の native な認知代数（CCL）として再構築（消化）する試みである。

## 2. 統合された機能 (Milestones)

### 2.1 Lambda 式 (`L:[]{}`) — Phase 2b
高階マクロへの匿名ワークフローの受け渡しを実現。

```ccl
L:[x]{/noe+{target=x}}
```

### 2.2 Mixin 合成 (`@with(M)`) — Phase B2
横断的関心事（ログ、キャッシュ、リトライ等）を認知操作に合成。

```ccl
@with(Tracing, Caching) /zet+
```

### 2.3 型制約と静的検証 — Phase 3
`Optional (?T)`, `Union (A|B)`, `List ([T])` 等の型記法。`/epi.typed` による GCD 検証。

### 2.4 スコープ管理 (`@scoped`) — Phase 3
`contextlib` 由来の setup/teardown 付実行。

### 2.5 デコレータマクロ (@M) — Phase B3 ⚡NEW
Mixin 合成 (`@with`) をより簡潔に記述するためのマクロ群。
- `@memoize`: `Caching` の糖衣
- `@retry`: `Retry` の糖衣
- `@log`: `Tracing` の糖衣
- `@timed`: `Timing` の糖衣

## 3. 定理階層への再構築 (B1 Paradigm)

外部概念をそのまま使用せず、必ず 6カテゴリ・24定理のどれかにマッピングする：
- **Decorator** → **Mixin 合成 (@with)** (設計軸: Schema)
- **Lambda** → **高階認知操作** (認知軸: Ousia)

---
*Consolidated into cognitive_algebra_system/artifacts/projects/pythosis — 2026-02-01*
