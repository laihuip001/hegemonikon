---
description: Jules（Gemini）にプロンプト生成を委譲するワークフロー
hegemonikon: Praxis-H
experimental: true
---

# /gen-jules ワークフロー

> **目的**: Runtime のルールを活用して、Jules にプロンプト生成を委譲する
> **実験**: AGENTS.md のルールが Runtime に影響を与えるか検証

---

## 前提条件

- [ ] AGENTS.md がプロジェクトルートに存在
- [ ] jules-pe Skill が `.agent/skills/utils/jules-pe/` に配置済み

---

## 実行手順

### Step 1: 指示書作成（Claude）

Claude が `.ai/JULIUS_TASK.md` に指示書を作成:

```markdown
# Prompt Generation Task

## Task Type: Prompt Engineering (PE)

## Requirements
[プロンプトの要件を記述]

## Output
- **ファイルパス**: forge/prompt-lang/prompts/[name].prompt
- **フォーマット**: Prompt-Lang v2
```

### Step 2: Runtime へのヒント

Runtime が AGENTS.md を読み込み、以下のルールを適用することを期待:

```
タスク種類: Prompt Engineering
→ 推奨エージェント: Gemini 3 Pro (Jules)
```

### Step 3: 検証（Claude）

// turbo
```powershell
python M:\Hegemonikon\forge\prompt-lang\prompt_lang.py parse [生成されたファイル]
```

---

## 実験結果記録

### 試行 1
- 日時: ____
- 指示: ____
- 結果: ____
- Runtime の挙動: ____

### 試行 2
- 日時: ____
- 指示: ____
- 結果: ____
- Runtime の挙動: ____

---

## 期待する挙動

```
Claude → JULIUS_TASK.md → Runtime がルールを解析 → Jules を起動 → 生成
```

## 実際の挙動

```
（実験後に記録）
```

---

## 注意事項

- これは **実験** です。成功する保証はありません。
- Runtime の内部ロジックは非公開であり、AGENTS.md のルールが影響を与えるかは不明。
- 結果に関わらず、学びを記録します。

---

## Hegemonikon Status

| Module | Workflow | Status |
|--------|----------|--------|
| M6 Praxis | /gen-jules | Experimental |
