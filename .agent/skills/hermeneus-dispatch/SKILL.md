---
name: Hermēneus CCL Dispatch
description: CCL 式を検出したら Hermēneus パーサーで構造解析し、AST に基づいて実行する
triggers:
  - "/"
  - "~"
  - "~*"
  - "~!"
  - ">>"
  - "CCL"
  - "ccl"
  - "マクロ"
  - "ワークフロー式"
  - "演算子"
version: "2.0"
---

# Hermēneus CCL Dispatch v2.0

> **第零原則**: CCL 式を見たら、手動で分析する前に **必ず** Hermēneus パーサーを通せ。
> これは「ルール」ではなく「手順」である。パーサーが出力した AST に基づいて行動せよ。
> **BC-10 (CCL 実行義務)** に直結。違反は再犯記録として残る。

## v2.0 変更点

> v1.0 の問題: スキルが存在していたが、**発動が任意**だった。
> 結果として BC-7 + BC-3 の同時違反が2度発生した。
> v2.0 では「発動条件の判定」を明示化し、Step 0 (検出義務) を追加。

## 発動条件

### Step 0: CCL 式の自動検出（暗黙発動）

**以下のいずれかのパターンがユーザー入力に含まれている場合、このスキルが自動発動する**:

| パターン | 例 |
|:---------|:---|
| `/` + 2-4文字の英字 | `/noe`, `/dia+`, `/boot` |
| `~` (演算子コンテキスト) | `/noe~/dia`, `~*`, `~!` |
| `>>` | `/noe >> V[] < 0.3` |
| `F:`, `I:`, `W:`, `L:` | `F:[×3]{/dia}` |
| `@` + 英字 | `@syn`, `@S{O,A,K}` |
| `\` + 英字 | `\noe` (colimit) |
| 括弧で囲まれた WF 組み合わせ | `(/dia+~/noe)~/pan+` |

> ⚠️ 検出した瞬間に Step 1 を実行する義務がある。
> 「意味は知っている」「前に読んだ」は免除理由にならない。

### 検出しない場合

- 単独の `/slash` コマンド（ワークフロー実行トリガー）は対象外
  - 例: `/boot`, `/bye`, `/u` — これらは WF 定義を直接読む
- ただし `/slash` に演算子が付随する場合は検出対象
  - 例: `/dia+`, `/noe+~/pan` — これらは CCL 式

## 手順 (必須・省略不可)

### Step 1: Hermēneus でパース

// turbo

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from hermeneus.src.dispatch import dispatch
import json
result = dispatch('CCL_EXPRESSION_HERE')
print(json.dumps({
    'success': result['success'],
    'tree': result['tree'],
    'workflows': result['workflows'],
    'plan_template': result['plan_template']
}, ensure_ascii=False, indent=2))
"
```

> ⚠️ `CCL_EXPRESSION_HERE` を実際の CCL 式に置換すること。
> **この Step を飛ばした時点で BC-10 違反確定。例外なし。**

### Step 2: AST に基づいて実行計画を立てる

パーサーの出力に含まれる `plan_template` をそのまま使い、各フィールドを埋める:

```
【CCL】(パーサー出力)
【構造】(パーサー出力の AST)
【関連WF】(パーサー出力のワークフロー一覧)
【実行計画】(AI が AST 構造に基づいて記入)
【/dia 反論】(AI が最低1つの懸念を提示)
→ これで進めてよいですか？
```

### Step 3: WF 定義読込（BC-3 連動）

`workflows` リストの各 WF について `view_file` で定義を読込む:

```
view_file .agent/workflows/{wf_name}.md
```

**確認事項**:

- `sel_enforcement` セクション（最低出力要件）
- 各ステップの具体的な手順
- 派生 (`+`/`-`) がある場合の挙動差

### Step 4: Creator 確認後に実行

AST の構造に従って、**左から右、深さ優先で** WF を実行する:

| AST ノード型 | 実行方法 |
|:-------------|:---------|
| `Sequence` (`_`) | 順次実行 |
| `Oscillation` (`~`) | 交互実行 |
| `Oscillation*` (`~*`) | 収束まで交互 |
| `Oscillation!` (`~!`) | 発散させて交互 |
| `Fusion` (`*`) | 統合出力 |
| `ConvergenceLoop` (`>>`) | 条件を満たすまで |
| `ForLoop` (`F:`) | 指定回数 or リスト |
| `IfCondition` (`I:`) | 条件分岐 |
| `WhileLoop` (`W:`) | 条件ループ |
| `Lambda` (`L:`) | パラメータ束縛 |
| `ColimitExpansion` (`\`) | 余極限展開 |

### Step 5: 出力後の自己検証

出力を書き終えたら、以下の3つを自問:

1. **「Hermēneus の `dispatch()` 出力を引用できるか？」** → No なら BC-10 違反
2. **「WF 定義の何行目を読んだか言えるか？」** → No なら BC-3 違反
3. **「AST のどのノードを今実行しているか？」** → No なら BC-10 違反

## パースエラー時

パーサーがエラーを返した場合:

1. CCL 式の構文を確認
2. 修正案を Creator に提示
3. **決して「パーサーなしで自分で解析する」をしない**

## なぜこのスキルが必要か

> LLM は CCL 式を「なんとなく」読めてしまう。
> しかし「なんとなく」は間違いの温床である。
> パーサーは **決定論的に** AST を生成する。
> 確率的な解析 vs 決定論的な解析 — 後者を選べ。
>
> **v2.0 追記**: 「知っている」と「実行する」は別物。
> 知っていても省略するな。知っているからこそ省略するな。
> これは能力の問題ではなく、**誠実さの問題**である。

---

*v2.0 — BC-10 準拠 + Step 0 (自動検出) 追加 + 再犯防止 (2026-02-08)*
