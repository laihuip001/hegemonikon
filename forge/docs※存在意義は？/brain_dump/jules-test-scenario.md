# Jules仮説検証: PE指示書テスト

## 目的

JulesがPE指示書に従ってプロンプトを生成できるかを検証する。

---

## 検証手順

### Step 1: Julesに以下の指示書を渡す

```markdown
# Prompt Engineering Instruction

## Your Role
You are a Prompt Engineer. Your output is **prompts**, not code.

## Task
Create a customer support response prompt following this exact format:

### Output Format
1. YAML frontmatter with:
   - created: (current timestamp)
   - task: "customer-support-reply"
   - archetype: "precision"
   - tags: [cot, few-shot]

2. XML body with:
   - <system>: role and constraints
   - <thinking_process>: step-by-step reasoning
   - <examples>: positive and negative examples
   - <output_format>: expected output structure

## Requirements
- The prompt should help an AI respond to customer complaints
- Include 3-step thinking process
- Include 1 positive and 1 negative example
- Max 500 tokens

## Deliverable
Save the output as: `customer-support-reply.md`
```

---

### Step 2: 期待される出力

```yaml
---
created: 2026-01-15T13:00:00+09:00
task: customer-support-reply
archetype: precision
tags: [cot, few-shot]
status: draft
---
```

```xml
<prompt version="1.0">
  <system>
    <role>Senior Customer Support Specialist</role>
    <constraints>
      <constraint>共感的かつ解決志向</constraint>
      <constraint>3文以内で結論</constraint>
    </constraints>
  </system>
  
  <thinking_process>
    <step>1. 顧客の感情状態を判定（怒り/不満/困惑）</step>
    <step>2. 問題の核心を特定（製品/サービス/対応）</step>
    <step>3. 解決策を提示（即座/調査後回答/エスカレーション）</step>
  </thinking_process>
  
  <examples>
    <example type="positive">
      Input: 「商品が届きません」
      Output: 「ご不便をおかけし申し訳ございません。配送状況を確認いたしました。[追跡番号XXX]で本日中に到着予定です。到着しない場合は再度ご連絡ください。」
    </example>
    <example type="negative">
      Input: 「商品が届きません」
      Output: 「配送会社に問い合わせてください」（× 顧客に丸投げ）
    </example>
  </examples>
  
  <output_format>
    <format>挨拶 + 共感 + 解決策 + 次のステップ</format>
    <max_tokens>150</max_tokens>
  </output_format>
</prompt>
```

---

## 判定基準

| 結果 | 条件 | 次のアクション |
|---|---|---|
| ✅ **成功** | 上記フォーマットに近い出力が得られた | Phase 1完了、library/充填へ |
| ⚠️ **部分成功** | フォーマットは崩れたが構造は理解している | rules.mdで矯正 |
| ❌ **失敗** | プロンプトではなくコードを出力した | prompt-lang設計へ移行 |

---

## 実行者

**CEOがJules環境で実行し、結果を報告する。**

---

## 報告テンプレート

```
## Jules検証結果

### 実行日時: 
### 結果: [成功/部分成功/失敗]

### 出力内容:
(Julesの出力をここに貼り付け)

### 観察:
- 良かった点:
- 問題点:

### 次のアクション:
```
