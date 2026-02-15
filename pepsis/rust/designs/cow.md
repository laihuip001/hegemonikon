# Cow — 触るまで借りておく

> **CCL**: `/gno+{source=rust.cow}`
> **消化タイプ**: T2 (再発見)
> **Date**: 2026-02-15
> **Kalon テスト**: ✅

---

## 1. Rust の Cow とは何か

```rust
use std::borrow::Cow;

fn process(input: &str) -> Cow<str> {
    if input.contains("bad") {
        // 変更が必要 → 所有権を取得 (clone)
        Cow::Owned(input.replace("bad", "good"))
    } else {
        // 変更不要 → 借用のまま
        Cow::Borrowed(input)
    }
}
```

**核心**: **変更が必要になるまでコピーしない**。

| 状態 | Cow | メモリ | コスト |
|:-----|:----|:------|:------|
| 読むだけ | `Borrowed(&T)` | 元データを参照 | ゼロ |
| 変更が必要 | `Owned(T)` | コピーして所有 | clone のコスト |

**遅延最適化**: 「たぶん変更しないだろう」ケースでコピーコストを回避する。

---

## 2. CCL の `-` → `+` 遷移 = Cow

### HGK の操作パターン

```ccl
# Phase 1: まず借りて読む (Cow::Borrowed)
/dia-{ctx: codebase}
# → codebase を読み取り分析。変更しない。コスト低。

# Phase 2: 変更が必要と判明 (Cow::Owned へ遷移)
I:[needs_fix]{
    /ene+{ctx: codebase}
    # → codebase を変更。所有権を取得。コスト高。
}
E:{
    # 変更不要。借用のまま終了。
    /pis{result: "問題なし"}
}
```

| Cow | CCL | 認知操作 |
|:----|:----|:--------|
| `Borrowed` (読むだけ) | `-` (読取) | 分析。コンテキストを変えない |
| 変更が必要と判明 | `I:[condition]{}` | 条件分岐。変更が必要か判定 |
| `Owned` (コピーして変更) | `+` (変更) | 実装。コンテキストを変える |
| 変更不要で終了 | `E:{}` | 報告のみ。コンテキストは借りたまま返す |

---

## 3. 深い洞察: BC-14 FaR = Cow パターン

BC-14 (Fact-and-Reflection) は Cow と同じパターン:

```
# F (Fact): 事実を集める = Borrowed (読むだけ)
[F] codebase を grep して調査。変更しない。

# R (Reflection): 反省する = 変更が必要か判定
[R] このコードは本当に問題か？ 変更すべきか？

# C (Confidence): 確信度
→ 確信度 > 閾値 → 変更する (Owned)
→ 確信度 < 閾値 → 変更しない (Borrowed のまま)
```

| BC-14 Phase | Cow 状態 | 操作 |
|:-----------|:---------|:-----|
| F (事実収集) | Borrowed | 読むだけ。安全 |
| R (反省) | 判定中 | 変更が必要かどうか |
| C > 閾値 | → Owned | 変更を実行 |
| C < 閾値 | → Borrowed 維持 | 変更しない |

> **Cow が教えてくれたこと**:
> 「確認してから変更する」は最適化ではなく、**認知の自然なパターン**。
> BC-14 (FaR) は Cow を認知に適用した設計だった。

---

## 4. to_mut() — 借用から所有への明示的変換

```rust
let mut cow = Cow::Borrowed("hello");
// to_mut() で Borrowed → Owned に変換
let mutable: &mut String = cow.to_mut();
// ← ここで clone が発生
mutable.push_str(" world");
```

CCL では: **`-` → `+` の明示的切り替え**

```ccl
# /dia- で分析 (Borrowed)
/dia-{ctx: design}

# 問題発見 → /ene+ で修正 (to_mut() = Borrowed → Owned)
_ /ene+{ctx: design}
# ← ここで design のコンテキストが「読取」から「変更可能」に遷移
```

**`_` が Cow の `to_mut()` に相当する**:
前の WF で読んだものを、次の WF で変更する。
遷移点が明示的 (CCL の `_`) であること = 安全。

---

## 5. Kalon テスト

| チェック | 結果 |
|:--------|:-----|
| Rust を知らなくても理解できるか | ✅ 「必要になるまでコピーしない」は直感的 |
| 新しい構文が必要か | ❌ 不要。- → + の遷移 |
| HGK に既に存在していたか | ✅ BC-14 FaR は Cow パターン |
| 消化で何を学んだか | 「確認してから変更」は最適化ではなく認知の自然なパターン |

---

*Pepsis Rust T2 | Cow — 触るまで借りておく (2026-02-15)*
