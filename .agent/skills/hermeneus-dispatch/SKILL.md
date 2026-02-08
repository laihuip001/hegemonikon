---
name: Hermēneus CCL Dispatch
description: CCL 式を検出したら Hermēneus パーサーで構造解析する
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
version: "1.0"
---

# Hermēneus CCL Dispatch

> **第零原則**: CCL 式を見たら、手動で分析する前に **必ず** Hermēneus パーサーを通せ。
> これは「ルール」ではなく「手順」である。パーサーが出力した AST に基づいて行動せよ。

## 発動条件

以下のいずれかを検出した場合、このスキルが発動する:

- `/` で始まるワークフロー参照 (例: `/dia+`, `/noe`, `/mek`)
- `~`, `~*`, `~!` — 振動演算子
- `>>` — シーケンス演算子
- `()`, `{}` — グループ化
- `\` — コリミット演算子

## 手順 (必須)

### Step 1: Hermēneus でパース

// turbo

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from hermeneus.src.dispatch import dispatch
result = dispatch('CCL_EXPRESSION_HERE')
import json
print(json.dumps({
    'success': result['success'],
    'tree': result['tree'],
    'workflows': result['workflows'],
    'plan_template': result['plan_template']
}, ensure_ascii=False, indent=2))
"
```

> ⚠️ `CCL_EXPRESSION_HERE` を実際の CCL 式に置換すること。

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

### Step 3: Creator 確認後に実行

AST の構造に従って、左から右、深さ優先で WF を実行する。

## パースエラー時

パーサーがエラーを返した場合:

1. CCL 式の構文を確認
2. 修正案を Creator に提示
3. 決して「パーサーなしで自分で解析する」をしない

## なぜこのスキルが必要か

> LLM は CCL 式を「なんとなく」読めてしまう。
> しかし「なんとなく」は間違いの温床である。
> パーサーは **決定論的に** AST を生成する。
> 確率的な解析 vs 決定論的な解析 — 後者を選べ。

---

*v1.0 — CCL `(/noe+~*/dia+)~*/mek+` の実行結果として設計 (2026-02-08)*
