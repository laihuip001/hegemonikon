# Lambda 式導入設計計画

> **Date**: 2026-01-31
> **CCL**: `/s+*^/noe`

---

## 1. 背景

`@partial` マクロを設計する過程で「匿名 WF」の概念が浮上。
Python の `lambda` に相当する機能を CCL に導入すべきか検討する。

---

## 2. Python Lambda との対応

```python
# Python
f = lambda x: x + 1
result = f(5)  # 6

# 高階関数への適用
sorted(items, key=lambda x: x.name)
```

### CCL への写像案

```ccl
# 案1: λ 記法
λ(x): /noe+{target=x}

# 案2: fn 記法
fn(x) /noe+{target=x}

# 案3: ブロック記法
{x -> /noe+{target=x}}
```

---

## 3. 導入の是非

### 3.1 メリット

| メリット | 説明 |
|:---------|:-----|
| **アドホック認知** | 一時的な認知操作を即座に定義 |
| **高階マクロ** | マクロに渡す「操作」を柔軟に指定 |
| **コード再利用** | 名前をつけずに操作を再利用 |
| **Python 親和性** | Pythōsis の自然な拡張 |

### 3.2 デメリット

| デメリット | 説明 |
|:---------|:-----|
| **複雑化** | CCL の freeze threshold (15演算子) に影響 |
| **可読性低下** | 匿名性が可読性を損なう可能性 |
| **@partial との重複** | 部分適用で代替可能なケースあり |
| **実装コスト** | パーサー拡張が必要 |

### 3.3 判定

| 判定 | **条件付き採用** ⚠️ |
|:-----|:--------------------|
| **成立条件** | `@partial` では表現できないユースケースが明確な場合 |
| **段階的導入** | まず `@partial` を活用し、不足が明らかになってから Lambda を導入 |

---

## 4. ユースケース分析

### 4.1 @partial で代替可能

```ccl
# 文脈固定
@partial(context="Hegemonikón") /zet+
```

### 4.2 Lambda が必要

```ccl
# 動的な操作の指定
@chain(
  λ(x): /noe+{target=x},
  λ(x): /dia{check=x}
)

# 高階マクロ
@retry(3, on_fail=λ: /dia^)
```

---

## 5. 構文候補

### 案1: λ (Lambda) 記法

```ccl
λ(x): /noe+{target=x}
λ: /bou~zet          # 引数なし
```

**Pros**: Python/数学との親和性
**Cons**: λ の入力が面倒

### 案2: fn 記法

```ccl
fn(x) /noe+{target=x}
fn() /bou~zet
```

**Pros**: 入力しやすい、Rust 風
**Cons**: CCL の簡潔さを損なう

### 案3: ブロック記法

```ccl
{x -> /noe+{target=x}}
{-> /bou~zet}
```

**Pros**: 最も簡潔
**Cons**: `{}` の多重使用で混乱

### 推奨: 案1 (λ 記法)

- CCL はギリシャ語由来の記号を多用している
- λ は「匿名関数」の普遍的記号
- 一貫性を優先

---

## 6. 実装方針

### Phase 1: @partial 活用強化 (推奨)

```ccl
# 既存の @partial で表現
@hege_zet := @partial(context="Hegemonikón") /zet+
```

### Phase 2: Lambda 構文検証 (将来)

1. λ 記法をドキュメントに追加
2. 手動実行でユースケースを検証
3. パーサー実装を検討

---

## 7. 次のステップ

```ccl
I: Phase 1 採用 → @partial の活用例を拡充
I: Phase 2 着手 → λ 記法をドキュメント化し検証
```

---

## 8. 検証計画

### マニュアル検証

1. `@partial` で Lambda 相当のユースケースを試行
2. `@partial` で表現できないケースを収集
3. Lambda 導入の必要性を再評価

---

*Lambda Design | Project Pythōsis Phase 5*
