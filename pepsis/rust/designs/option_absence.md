# Option\<T\> — 不在を型にする

> **CCL**: `/gno+{source=rust.option}`
> **消化タイプ**: T2 (再発見)
> **Date**: 2026-02-15
> **Kalon テスト**: ✅

---

## 1. Rust の Option\<T\> とは何か

```rust
enum Option<T> {
    Some(T),    // 値がある
    None,       // 値がない
}
```

**核心**: 「ない」ことを**型として**表現する。null ではなく、None。

```rust
fn find_user(name: &str) -> Option<User> {
    // 見つからなければ None
    // null pointer exception は起きない
    // 呼び出し側は「ないかもしれない」を処理する義務がある
}

// 使う側
match find_user("Alice") {
    Some(user) => println!("Found: {}", user.name),
    None => println!("Not found"),  // ← これを書かないとコンパイルエラー
}
```

**Rust が解決した問題**: Tony Hoare の「10億ドルの過ち」= null pointer。
Option は「不在」を暗黙 (null) ではなく明示 (None) にする。

---

## 2. HGK にはどこに対応するか

### 2.1 BC-6 確信度体系 = Option の連続版

| Option | BC-6 | 意味 |
|:-------|:-----|:-----|
| `Some(value)` | `[確信] 90%+` | 答えがある。根拠もある |
| `Some(value)` (低確信) | `[推定] 60-90%` | 答えはある。だが未検証 |
| — | `[仮説] <60%` | 答えはある。だが推測 |
| `None` | **回答不能** | 答えがない |

Rust の Option は二値 (Some/None)。HGK の確信度は**連続値** (0-100%)。
HGK は Option を**一般化している**。None = 確信度 0%。Some = 確信度 > 0%。

### 2.2 /dia epochē (判断停止) = 明示的 None

```ccl
/dia epochē{topic: X}
# → 「X については判断しない」
# → これは None を返すことと等価
```

Rust が `None` を返すのは「値がない」。
/dia epochē が判断停止するのは「判断できない」。

**構造が同じ**: どちらも「答えがないことを正当な結果として認める」。

### 2.3 I:/E: 構文 = Option の pattern match

```rust
// Rust
match result {
    Some(value) => use_value(value),
    None => handle_absence(),
}
```

```ccl
# CCL
I:[/noe+ = valuable]{
    /ene+{result}           # Some: 価値ある結果を実行に移す
}
E:{
    /zet+{why_no_result}    # None: なぜ結果が得られなかったか探求
}
```

---

## 3. unwrap() = BC-6 違反

Rust で最も危険な操作:

```rust
let value = find_user("Alice").unwrap();
// None だったら panic! (クラッシュ)
```

HGK 等価:

```
# 確信度を無視して断言する = unwrap()
「この設計は正しい」 ← 検証していないのに [確信] と表示
```

**これは BC-6 (確信度偽装) 違反。**

| Rust の危険操作 | HGK の危険操作 |
|:-------------|:-------------|
| `.unwrap()` | 確信度を偽って高く表示 |
| `.expect("msg")` | 「たぶん大丈夫」で進む |
| unchecked null deref | BC-6 なしで断言 |

Rust は `unwrap()` をコンパイラ警告で抑止する。
HGK は BC-6 で抑止する。同じメカニズム、異なる実装。

---

## 4. 深い洞察: None は失敗ではない

> **Rust**: None は Result::Err とは違う。
> None = 「ない」 (正常)。Err = 「壊れた」 (異常)。

> **HGK**: /dia epochē は WF の失敗ではない。
> 「判断できない」は「判断を誤った」とは違う。
> 前者は知恵 (Sophia)。後者は過ち。

| Rust | HGK | 意味 |
|:-----|:----|:-----|
| `None` | /dia epochē | 不在。正当な結果 |
| `Err(e)` | `ε > ε_max` | エラー。予測誤差超過 |
| `Ok(v)` | 成功 | 期待通り |

**Rust が教えてくれたこと**: Not found ≠ Error。
**HGK が既に知っていたこと**: 判断停止 ≠ 判断失敗。

---

## 5. HGK に欠けている可能性

[主観] Option の **コンパイル時強制** は HGK にない。

Rust は `Option<T>` を返す関数を呼んだら、None を処理しないとコンパイルエラー。
HGK は /dia epochē が「可能」であるが、**強制されない**。

→ Hermēneus の dispatch() に「このWFは None (判断停止) を返しうる」という
メタデータを追加し、後続 WF で I:/E: を強制できるかもしれない。

**しかし**: これは T3 (機能追加) であり、今は T2 (再発見) を確認するフェーズ。
将来の検討課題として記録する。

---

## 6. Kalon テスト

| チェック | 結果 |
|:--------|:-----|
| Rust を知らなくても理解できるか | ✅ 「答えがないかもしれない」は普遍的 |
| 新しい構文が必要か | ❌ 不要。BC-6 + I:/E: + /dia epochē |
| HGK に既に存在していたか | ✅ BC-6 は Option の連続版 |
| 消化で何を学んだか | None ≠ Error の明確化 |

---

*Pepsis Rust T2 | Option\<T\> — 不在を型にする (2026-02-15)*
