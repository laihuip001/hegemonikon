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
| 条件分岐 | `if/else` | `I:[cond]{} / E:{}` |
| ループ | `for/while` | `F:[]{}`, `W:[]{}`, `~` (振動) |
| 収束ループ | `while not converged:` | `C:{}` |
| 累積 | `functools.reduce` | `R:{}` |
| キャッシュ | `@cache` | `M:{}` |
| 検証 | `assert` / `@validate` | `V:{}` |
| 再帰 | `f(f(x))` | `*` (融合) |
| マクロ | プリプロセッサ | `@macro` |
| 型 | `int, str` | **定理型 (O, S, H, P, K, A)** |
| ライブラリ | `import` | ワークフロー群 |
| Lambda | `lambda x: ...` | `L:[x]{...}` |

---

## 構文要素

### 演算子

| 演算子 | 意味 | 例 |
|:-------|:-----|:---|
| `/` | ワークフロー呼び出し | `/noe` |
| `+` | 深化 | `/noe+` |
| `-` | 簡略化 | `/noe-` |
| `*` | 融合 | `/noe*dia` |
| `^` | メタレベル | `/noe^` |
| `_` | チェーン (then) | `/noe_/s` |
| `~` | 振動 (oscillation) | `/noe~/s` |
| `~*` | 収束振動 | `/noe~*/s` |
| `~!` | 発散振動 | `/noe~!/s` |
| `>>` | 射 (構造変換) | `/noe >> /dia` |
| `>*` | 変容 (射的融合) | `/noe >* /dia` |
| `\` | 反転 | `\noe` |
| `$` | WM変数定義/参照 | `$goal = /bou` |
| `@` | マクロ参照 | `@proof` |

### 制御構造 — メタ処理統一構文

> **構文パターン**: `X:[対象]{処理内容}` — 全制御構造がこの形式に統一

| 構造 | 構文 | 意味 |
|:-----|:-----|:-----|
| 順次 | `A_B_C` | A → B → C |
| 条件 (IF) | `I:[cond]{A}` | if cond then A |
| 条件 (ELSE) | `E:{A}` | else A |
| 繰り返し (FOR) | `F:[items]{A}` | for item in items: A |
| 繰り返し (N回) | `F:[×N]{A}` | N 回繰り返し |
| ループ (WHILE) | `W:[cond]{A}` | while cond: A |
| 収束ループ | `C:{A}` | converge(A) |
| 累積融合 | `R:{A}` | reduce(A) |
| 記憶 | `M:{A}` | memoize(A) |
| 検証 | `V:{A}` | validate(A) |
| 振動 | `A~B` | A ↔ B (収束まで) |
| Lambda | `L:[x]{A}` | lambda x: A |
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
```

**3層構造** (詳細: `operators.md` §11):

| 層 | 正本 | 内容 |
|:---|:-----|:-----|
| Layer 1: ユーザーマクロ (12) | `.agent/workflows/ccl-*.md` | Creator が直接使う |
| Layer 2: システムマクロ (~8) | `operators.md` §11 | Hub WF 内部使用 |
| Layer 3: 構文プリミティブ (9) | `operators.md` §9.7, §10 | C:/R:/M:/V: + F:/I:/E:/W:/L: |

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
| 条件分岐 | `I:[cond]{}` / `E:{}` |
| ループ | `F:[N]{}`, `W:[]{}`, `~` |
| 収束 | `C:{}` |
| 状態 | 認知コンテキスト |
| メモリ | `/dox` (信念永続化) / `M:{}` (キャッシュ) |

**CCL はチューリング完全になりうる。**

---

## 起源

2026-01-30 セッション — Creator と AI の対話から発見:

> **Creator**: 「CCL は WF を関数とした "思考のプログラム" だ。抽象化すれば、CCL も "プログラミング言語" ではないか？」
>
> **AI**: 「そうだ。CCL はプログラミング言語だ。しかし実行者は CPU ではなく認知エージェントだ。」

---

*CCL は認知を対象としたプログラミング言語である。*
