---
description: Claude が設計し、Jules がプロンプトを生成するワークフロー
hegemonikon: Praxis-H
---

# /gen-prompt ワークフロー

> **目的**: Antigravity のコード生成機構をプロンプト生成に転用する
> **設計思想**: Claude が設計、Jules が生成、Claude が検証

---

## 概念

```
従来のコード生成:
  Claude → [設計] → Jules → [コード生成] → ファイル

プロンプト生成に転用:
  Claude → [指示書作成] → Jules → [プロンプト生成] → .prompt ファイル
```

---

## 実行フロー

### Step 1: 指示書作成（Claude）

Claude が以下のフォーマットで **指示書** を作成し、ファイルとして保存:

```markdown
# Prompt Generation Instructions

## 課題
[生成したいプロンプトの目的]

## Phase 0 分析結果
- **Archetype**: [Precision / Speed / Autonomy / Creative / Safety]
- **勝利条件**: [何を最大化するか]
- **許容トレードオフ**: [何を犠牲にできるか]

## 要件
- **@role**: [役割の方向性]
- **@goal**: [目標の方向性]
- **@context**: [必要なリソース種類]
- **@constraints**: [制約の方向性]
- **@rubric**: [評価次元数と方向性]
- **@if 条件**: [分岐が必要な状況]
- **@examples**: [例の方向性]
- **@fallback**: [エッジケースの方向性]

## 出力要件
- ファイルパス: [保存先]
- 言語: [日本語/英語]
- フォーマット: Prompt-Lang v2

## 参考資料
- meta-prompt-generator Skill: `.agent/skills/utils/meta-prompt-generator/SKILL.md`
- Prompt-Lang v2 仕様: `docs/specs/prompt-lang-v2-spec.md`
```

### Step 2: Jules に生成依頼

// turbo
```powershell
# 指示書を作成したら、Jules に以下のメッセージで依頼:
# 「forge/prompt-lang/instructions/[name].md の指示に従って .prompt ファイルを生成してください」
```

### Step 3: 検証（Claude）

// turbo
```powershell
python M:\Hegemonikon\forge\prompt-lang\prompt_lang.py parse [生成されたファイル]
```

### Step 4: 修正があれば反復

- パースエラー → 修正依頼
- 品質不足 → 追加指示

---

## ディレクトリ構造

```
forge/prompt-lang/
├── instructions/          # 指示書ディレクトリ（新規）
│   └── [task_name].md
├── prompts/               # 生成されたプロンプト
│   └── [prompt_name].prompt
└── prompt_lang.py         # パーサー
```

---

## 使用例

```
ユーザー: /gen-prompt セキュリティレビュー用プロンプト

Claude: 
1. 指示書を作成 → instructions/security_review.md
2. Jules に依頼: 「この指示に従って .prompt を生成して」
3. パーサーで検証
4. 修正があれば反復
5. 完了報告
```

---

## 仮説検証ポイント

このワークフローが機能するかどうかは、以下に依存:

1. **Jules がファイルを読める**: instructions/*.md を Jules が読み込めるか
2. **Jules が指示に従える**: Prompt-Lang 形式を理解・生成できるか
3. **Jules が自律的に生成**: 「内容を考えて書く」ができるか

---

## Hegemonikon Status

| Module | Workflow | Status |
|--------|----------|--------|
| M6 Praxis | /gen-prompt | Experimental |
