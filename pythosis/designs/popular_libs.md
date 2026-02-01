# 人気ライブラリ消化設計

> **CCL**: `/eat[python.popular]+`
> **Date**: 2026-02-01
> **Phase**: 3 (人気ライブラリ)
> **精緻化**: `/bou.akra+ _/kho.scope+ _/sta.done _/chr.dead _/epi.reference_class`

---

## 📋 計画サマリー

| 項目 | 値 |
|:-----|:---|
| **期限** | 2026-02-08 (1週間) |
| **工数見積もり** | 3-5 セッション |
| **完了条件** | 10 チェック項目 |
| **スコープ** | 4 ライブラリ (typing, dataclasses, contextlib, asyncio) |

---

## ⚠️ 失敗対策 (Premortem)

| リスク | 対策 |
|:-------|:-----|
| 「消化」が「模倣」になる | 各派生に「定理との対応」を必須化 |
| 派生が使われない | 実用例先行で設計 |
| asyncio が Synergeia を壊す | インターフェースとして設計、内部は触らない |
| スコープ肥大化 | 4ライブラリに厳格限定、追加は Phase 4 へ |

---

## ✅ 完了条件 (Definition of Done)

### [1] typing → /epi.typed ✅

- [x] 派生が `epi.md` に追加
- [x] 使用例 2 つ以上 (5例)
- [x] `?T` 構文が `operators.md` に記載

### [2] dataclasses → /dox.structured ✅

- [x] 派生が `dox.md` に追加
- [x] スキーマ定義構文が決定 (`schema:`, `default:`, `immutable:`, `validate:`)
- [x] 使用例 1 つ以上 (3例)

### [3] contextlib → @scoped v2 ✅

- [x] マクロが `operators.md` (11.14) に追加
- [x] setup/teardown パラメータが定義済み

### [4] asyncio → パイプ記法 ✅

- [x] `||`, `|>` が `operators.md` (1.6 分散実行演算子) に記載
- [x] Synergeia 経由で並列実行が動作可能 (既存アーキテクチャ)

---

## 🚫 スコープ外 (Out of Scope)

- Python 実行時型チェック (mypy 連携)
- dataclasses の継承
- asyncio 低レベル API (gather, wait)
- pathlib (Phase 4 へ)

---

## 消化対象

| # | ライブラリ | 対応定理 | 消化形態 | 優先度 |
|:-:|:-----------|:---------|:---------|:------:|
| 1 | `typing` | A4 Epistēmē | `/epi.typed` 派生 | ★★★ |
| 2 | `dataclasses` | H4 Doxa | `/dox.structured` 派生 | ★★★ |
| 3 | `contextlib` | P1 Khōra | `@scoped` マクロ精緻化 | ★★☆ |
| 4 | `pathlib` | P2 Hodos | `/hod.path` 派生 | ★★☆ |
| 5 | `asyncio` | Synergeia | 分散実行統合 | ★★☆ |

---

## 1. typing → /epi.typed

### Python 概念

```python
from typing import Optional, List, TypeVar, Generic

def process(data: List[str]) -> Optional[int]:
    ...
```

### CCL 翻訳

| Python | CCL | 意味 |
|:-------|:----|:-----|
| `Optional[T]` | `?T` | 不確実な型 |
| `List[T]` | `[T]` | 複数要素 |
| `Union[A, B]` | `A\|B` | 選択型 |
| `TypeVar` | `@generic` | 汎用パラメータ |

### 派生設計: `/epi.typed`

```yaml
derivative: typed
parent: A4 Epistēmē
purpose: 型制約による知識の厳密化
parameters:
  constraint: type expression
output:
  verified: true/false
  violations: list
```

### 使用例

```ccl
/epi.typed{output: "string"} /noe+
# → /noe+ の出力が string であることを検証
```

---

## 2. dataclasses → /dox.structured

### Python 概念

```python
from dataclasses import dataclass, field

@dataclass
class Belief:
    content: str
    confidence: float = 0.5
    source: str = field(default="unknown")
```

### CCL 翻訳

| Python | CCL | 意味 |
|:-------|:----|:-----|
| `@dataclass` | `/dox.structured` | 構造化信念 |
| `field(default=)` | `default:` | デフォルト値 |
| `frozen=True` | `immutable: true` | 不変信念 |
| `__post_init__` | `@validate` | 事後検証 |

### 派生設計: `/dox.structured`

```yaml
derivative: structured
parent: H4 Doxa
purpose: 信念を構造化して永続化
parameters:
  schema: field definitions
  immutable: bool (default: false)
output:
  belief_record: structured object
```

### 使用例

```ccl
/dox.structured{
  schema: {
    topic: string,
    confidence: float,
    evidence: [string]
  }
}
# → 構造化された信念レコードを生成
```

---

## 3. contextlib → @scoped 精緻化

### Python 概念

```python
from contextlib import contextmanager

@contextmanager
def managed_resource():
    setup()
    try:
        yield resource
    finally:
        teardown()
```

### CCL 翻訳

| Python | CCL | 意味 |
|:-------|:----|:-----|
| `@contextmanager` | `@scoped` | スコープ限定実行 |
| `__enter__` | `setup:` | 事前処理 |
| `__exit__` | `teardown:` | 事後処理 |
| `suppress()` | `@suppress` | エラー抑制 |

### マクロ精緻化: @scoped v2

```yaml
macro: @scoped
version: 2.0
parameters:
  setup: CCL expression (optional)
  teardown: CCL expression (optional)
  suppress: error types to suppress
definition: |
  スコープ内での実行を保証
  teardown は例外時も実行
```

### 使用例

```ccl
@scoped(
  setup: /kho.scope{domain: "Pythōsis"},
  teardown: /bye-
) {
  /noe+ _/s+ _/dia
}
```

---

## 4. asyncio → Synergeia 統合

> **後続検討**: freeze threshold 廃止済みのため、CCL レベルでの非同期記述を検討

### 統合案

```ccl
# 案1: @async マクロ
@async /sop+{query: "..."}

# 案2: Synergeia 直接呼び出し
@synergeia.parallel(
  /sop+{query: "A"},
  /sop+{query: "B"}
)

# 案3: パイプ記法
/sop+{A} || /sop+{B}  # 並列実行
/sop+{A} |> /sop+{B}  # パイプライン
```

### 実装場所

- `synergeia/coordinator.py` に CCL インターフェース追加
- マクロライブラリに `@async`, `@parallel` 追加

---

## 実装ロードマップ

| Week | タスク | 成果物 |
|:----:|:-------|:-------|
| 1 | `/epi.typed` 設計・実装 | `workflows/epi.md` 更新 |
| 2 | `/dox.structured` 設計・実装 | `workflows/dox.md` 更新 |
| 3 | `@scoped` v2 実装 | `macros/scoped.md` |
| 4 | asyncio 統合検討 | `synergeia/ccl_interface.md` |

---

*Project Pythōsis Phase 3 | `/eat[python.popular]+`*
