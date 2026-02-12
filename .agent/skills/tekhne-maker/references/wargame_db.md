# Wargame DB: 失敗シナリオ参照

> **消化元**: files.zip → wargame-db.md (SKILL v4.0 参照)
> **消化日**: 2026-02-12
> **第一原理**: 「歴史の失敗から学ぶ決定木」 = /dia Pre-Mortem の具体的チェックリスト
> **HGK 対応**: /dia, Synteleia WBC, Safety Invariants

---

## 使い方

`/dia` 実行時の Pre-Mortem フェーズで、設計/実装が以下のシナリオに該当しないか検証する。

---

## シナリオ一覧

| # | 名称 | 重大度 | 症状 | 根本原因 |
|:--|:-----|:-------|:-----|:---------|
| W01 | **Thundering Herd** | P0 | レイテンシ急騰、Backend CPU 飽和 | キャッシュ同時失効 + 即リトライ |
| W02 | **Distributed Race** | P1 | 間欠的データ破損 | ロック不在の並行更新 |
| W03 | **N+1 Query** | P2 | DB CPU スパイク | ORM の lazy loading |
| W04 | **Supply Chain Poison** | P0 | 異常な外部通信、env 漏洩 | 未固定依存 + typosquatting |
| W05 | **Unbounded Queue** | P1 | メモリ膨張、OOM Kill | 上限なしバッファ + 遅い消費者 |
| W06 | **Cascade Failure** | P0 | 連鎖タイムアウト | Circuit breaker なし |
| W07 | **Cold Start Amp** | P2 | 起動直後のレイテンシ | 空キャッシュ + Eager loading |
| W08 | **Secret Sprawl** | P1 | 複数箇所の秘密散在 | Secret rotation 自動化なし |
| W09 | **Time Zone Hell** | P3 | 地域依存の計算エラー | UTC 標準化なし |
| W10 | **Config Drift** | P2 | 「うちでは動く」 | IaC ギャップ + 手動変更 |

---

## 予防策早見表

| シナリオ | 予防策 TOP 3 |
|:---------|:------------|
| W01 | ① Staggered TTL ② Circuit breaker ③ Exponential backoff |
| W02 | ① 分散ロック ② 冪等性 ③ 楽観的ロック |
| W03 | ① Eager loading ② DataLoader ③ SQL EXPLAIN |
| W04 | ① Lockfile ② Dependabot ③ Private registry |
| W05 | ① Bounded channel ② Backpressure ③ DLQ |
| W06 | ① Circuit breaker ② Bulkhead ③ Timeout budget |
| W07 | ① Pre-warm ② Stale-while-revalidate ③ Connection pool |
| W08 | ① Secret Manager ② Auto-rotation ③ Pod identity |
| W09 | ① UTC 内部統一 ② TZ-aware datetime ③ Global library |
| W10 | ① IaC 強制 ② Drift detection ③ Immutable infra |

---

## HGK 固有シナリオ (消化時に追加)

| # | 名称 | 重大度 | 症状 | 根本原因 |
|:--|:-----|:-------|:-----|:---------|
| W11 | **Context Rot** | P1 | 同じファイルの繰返し参照、命名不一致 | 長セッションによるコンテキスト劣化 |
| W12 | **Skill Skeleton** | P2 | WF 実行後に「何も起きてない」 | description だけで実体未読 (BC-3 違反) |
| W13 | **Confidence Mask** | P1 | 断言したが実は未検証 | TAINT/SOURCE 追跡なし (BC-6 違反) |
| W14 | **Macro Ghost** | P2 | CCL マクロが展開されない | 定義の不同期 (macros.py ↔ ccl-*.md) |

---

## Python 統合

```python
def wargame_check(design: dict) -> list[str]:
    """Pre-Mortem: Wargame DB シナリオとの照合"""
    warnings = []
    if design.get("uses_cache") and not design.get("staggered_ttl"):
        warnings.append("W01: Thundering Herd — staggered TTL なし")
    if design.get("concurrent_writes") and not design.get("distributed_lock"):
        warnings.append("W02: Distributed Race — 分散ロックなし")
    if design.get("orm_lazy") and not design.get("eager_loading"):
        warnings.append("W03: N+1 Query — eager loading なし")
    if design.get("external_deps") and not design.get("lockfile"):
        warnings.append("W04: Supply Chain — lockfile なし")
    if design.get("queue") and not design.get("bounded"):
        warnings.append("W05: Unbounded Queue — 上限なし")
    return warnings
```

---

*Wargame DB v1.0 — SKILL v4.0 消化 + HGK 固有シナリオ追加 (2026-02-12)*
