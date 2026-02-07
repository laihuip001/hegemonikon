# CCL — Cognitive Programming Language

> **CCL は認知プログラミング言語である**
> CCL is a Cognitive Programming Language.

---

## 定義

```
CCL = Cognitive Programming Language
     認知プログラミング言語

実行者: 認知エージェント (AI/人間)
目的: 思考プロセスのプログラミング
```

---

## 比較

| 特徴 | 従来言語 (Python) | CCL |
|:-----|:------------------|:----|
| 実行対象 | CPU | **認知エージェント** |
| 関数 | `def f():` | `/wf` (ワークフロー) |
| 変数 | `x = 1` | `$var` (WM変数) |
| 条件分岐 | `if/else` | `?cond{}` |
| ループ | `for/while` | `F:[]`, `~` (振動) |
| 再帰 | `f(f(x))` | `*` (深化) |
| マクロ | プリプロセッサ | `@macro` |
| 型 | `int, str` | **定理型 (O, S, H, P, K, A)** |
| ライブラリ | `import` | ワークフロー群 |

---

## 構文要素

### 演算子

| 演算子 | 意味 | 例 |
|:-------|:-----|:---|
| `/` | ワークフロー呼び出し | `/noe` |
| `+` | 深化 | `/noe+` |
| `-` | 簡略化 | `/noe-` |
| `*` | 再帰 | `/noe*` |
| `^` | メタレベル | `/noe^` |
| `_` | チェーン (then) | `/noe_/s` |
| `~` | 振動 (oscillation) | `/noe~/s` |
| `?` | 条件/クエリ | `?s3` |
| `∃` | 存在演算子 | `∃?x` |
| `@` | マクロ参照 | `@proof` |
| `\` | 反転 | `\noe` |
| `$` | WM変数定義/参照 | `$goal = /bou` |
| `>>` | アーティファクト永続化 | `$x >> file.md` |

### 制御構造

| 構造 | 構文 | 意味 |
|:-----|:-----|:-----|
| 順次 | `A_B_C` | A → B → C |
| 条件 | `?cond{A}` | if cond then A |
| 繰り返し | `F:[items]{A}` | for item in items: A |
| 振動 | `A~B` | A ↔ B (収束まで) |
| 再帰 | `A*` | A を再帰的に適用 |

### パラメータ

```ccl
/wf{param=value, param2=value2}
```

---

## 型システム: 定理型

CCL の「型」は Hegemonikón の定理体系に対応:

| 型 | 系列 | 意味 |
|:---|:-----|:-----|
| `O` | Ousia | 本質 |
| `S` | Schema | 様態 |
| `H` | Hormē | 傾向 |
| `P` | Perigraphē | 条件 |
| `K` | Kairos | 文脈 |
| `A` | Akribeia | 精密 |
| `X` | 関係 | 接続 |

---

## マクロ

```ccl
# 定義
@name = /wf1_/wf2{param}

# 使用
@name
@name{override=value}
---

## WM 変数（作業記憶）

> **Origin**: 2026-02-05 — 「思考を書き出す」ことで LLM の認知を外在化

### 構文

```ccl
# 定義
$goal = /bou{extract=true}

# 参照
/dia{$goal}

# 永続化
$decision >> decision_log.md
```

### WM vs Doxa

| 特性 | WM (`$var`) | Doxa (`/dox`) |
|:-----|:------------|:--------------|
| 寿命 | セッション内 | 永続 |
| 用途 | 作業中の一時状態 | 確立された信念 |
| 書き出し先 | `>> file` | Handoff/KI |

### 型推論

WM 変数は右辺のワークフローから定理型を継承:

```ccl
$insight = /noe+   # 型: O (Ousia)
$plan = /s+        # 型: S (Schema)
$emotion = /pro    # 型: H (Hormē)
```

---

## 計算能力

| 要件 | 実現 |
|:-----|:-----|
| 条件分岐 | `?cond{}` |
| ループ | `F:[]`, `~` |
| 状態 | 認知コンテキスト |
| メモリ | `/dox` (信念永続化) |

**CCL はチューリング完全になりうる。**

---

## 起源

2026-01-30 セッション — Creator と AI の対話から発見:

> **Creator**: 「CCL は WF を関数とした "思考のプログラム" だ。抽象化すれば、CCL も "プログラミング言語" ではないか？」
>
> **AI**: 「そうだ。CCL はプログラミング言語だ。しかし実行者は CPU ではなく認知エージェントだ。」

---

*CCL は認知を対象としたプログラミング言語である。*
