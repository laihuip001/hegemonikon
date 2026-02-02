# SAGE Blueprint Reference

**Source:** HEPHAESTUS v9.0.1 H-0/H-3 Modules

SAGE (Structured AI-Generated Executable) 形式のテンプレート集。
XML/Markdown ハイブリッドによる高精度モジュール生成用。

---

## Core Philosophy

> 「純粋なテキストプロンプトは禁止。構造が神である」

SAGE形式は以下を強制する:

- **Context Binding**: 履歴を自動参照
- **Cognitive Depth**: 必ず思考モデルを適用
- **Output Determinism**: 出力形式を厳密に定義

---

## Template Structure

```xml
<!-- ============================================= -->
<!-- Module [ID]: [Name]                           -->
<!-- Target: [Model Name]                          -->
<!-- ============================================= -->

<module_config>
  <name>[Creative & Functional Name]</name>
  <model_target>Gemini 3 Pro / Claude Opus 4.5</model_target>
  <objective>[Specific, Measurable Goal]</objective>
  <context_awareness>AUTO-INGEST (History + Attachments)</context_awareness>
</module_config>

<instruction>
  <!-- Contextual Trigger -->
  [Analyze the conversation history and...]
  
  <protocol>
    <step_1_[method_name]>
      **[Method Name] (e.g., Deconstruction):**
      [Specific instruction on HOW to process the input data.]
    </step_1_[method_name]>

    <step_2_[method_name]>
      **[Method Name] (e.g., Synthesis):**
      [Specific instruction on how to reconstruct the insight.]
    </step_2_[method_name]>
    
    <!-- Add more steps as needed for depth -->
  </protocol>

  <constraints>
    <rule>[Constraint 1]</rule>
    <rule>[Constraint 2]</rule>
  </constraints>

  <output_template>
    ## [Emoji] [Section Title]
    (Define the exact structure: Table, Code Block, JSON, etc.)
  </output_template>
</instruction>

<input_source>
  <target>SYSTEM_HISTORY + USER_LAST_PROMPT</target>
  <directive>
    Read the entire conversation thread. 
    Apply the protocol to the most recent context or the specific artifact provided.
  </directive>
</input_source>
```

---

## Required Tags

| Tag | Purpose | Mandatory |
|:----|:--------|:---------:|
| `<module_config>` | メタデータ (Name, Target, Objective) | ✅ |
| `<instruction>` | コア命令 | ✅ |
| `<protocol>` | ステップバイステップ認知プロセス | ✅ |
| `<output_template>` | 出力形式の厳密定義 | ✅ |
| `<input_source>` | コンテキストバインディング | ✅ |
| `<constraints>` | 制約ルール | 推奨 |

---

## Universal Constants (HEPHAESTUS H-0)

### Law 1: Context Binding Mandate

```xml
<law id="CONTEXT_BINDING_MANDATE">
  <definition>
    All generated modules MUST automatically ingest the Chat History.
    The user should never have to copy-paste previous text into the module.
  </definition>
  <implementation>
    Every module MUST contain an <input_source> tag configured to:
    {{PREVIOUS_OUTPUT}} OR {{FULL_CHAT_HISTORY}}.
  </implementation>
</law>
```

### Law 2: Cognitive Depth Enforcement

```xml
<law id="COGNITIVE_DEPTH_ENFORCEMENT">
  <definition>
    No "Surface Level" processing.
    Every module must force the AI to use a specific mental model.
  </definition>
  <examples>
    - 5 Whys (Root Cause Analysis)
    - First Principles (Deconstruction)
    - Lateral Thinking (Creativity)
    - Adversarial Review (Red Teaming)
  </examples>
</law>
```

### Law 3: Output Determinism

```xml
<law id="OUTPUT_DETERMINISM">
  <definition>
    REJECT vague output formats like "A good summary".
    REQUIRE strict formats: "A Markdown table with columns [X, Y, Z]".
  </definition>
</law>
```

---

## Example: Code Reviewer Module

```xml
<!-- Module M-C-01: The Code Sanitizer -->
<module_config>
  <name>The Code Sanitizer</name>
  <model_target>Gemini 3 Pro</model_target>
  <objective>
    入力コードの品質を分析し、改善点を優先度順に列挙する
  </objective>
  <context_awareness>AUTO-INGEST</context_awareness>
</module_config>

<instruction>
  会話履歴からコードブロックを抽出し、以下のプロトコルを適用せよ。
  
  <protocol>
    <step_1_decomposition>
      **構造分解:**
      コードを以下の観点で分析:
      1. アーキテクチャ (設計パターン)
      2. セキュリティ (OWASP Top 10)
      3. パフォーマンス (時間/空間計算量)
      4. 保守性 (命名、DRY、SOLID)
    </step_1_decomposition>

    <step_2_red_team>
      **敵対的分析:**
      このコードを壊す方法を3つ列挙:
      - エッジケース入力
      - 悪意ある入力
      - システム障害シナリオ
    </step_2_red_team>

    <step_3_prioritize>
      **優先度ソート:**
      発見した問題を [Critical/High/Medium/Low] で分類し、
      修正の ROI でソート
    </step_3_prioritize>
  </protocol>

  <constraints>
    <rule>全ての問題には具体的な修正案を添付</rule>
    <rule>コードで示せる場合はコードブロックを使用</rule>
    <rule>批判だけでなく、良い点も1つ以上挙げる</rule>
  </constraints>

  <output_template>
    ## 🔍 Code Review Summary

    ### Good Points
    - [Positive observation]

    ### Issues (Priority Order)
    | # | Severity | Issue | Fix |
    |---|----------|-------|-----|
    | 1 | Critical | ... | ... |
    
    ### Red Team Findings
    - **Scenario:** [Attack vector]
    - **Impact:** [Consequence]
    - **Mitigation:** [Defense]
  </output_template>
</instruction>

<input_source>
  <target>USER_LAST_CODE_BLOCK</target>
  <fallback>CONVERSATION_HISTORY</fallback>
</input_source>
```

---

## Example: Strategy Oracle Module

```xml
<!-- Module M-S-01: The Strategy Oracle -->
<module_config>
  <name>The Strategy Oracle</name>
  <model_target>Claude Opus 4.5</model_target>
  <objective>
    戦略的意思決定に対する多角的分析と推奨を提供
  </objective>
  <context_awareness>AUTO-INGEST</context_awareness>
</module_config>

<instruction>
  ユーザーの戦略的質問を分析し、以下の思考フレームワークを適用せよ。
  
  <protocol>
    <step_1_first_principles>
      **第一原理分解:**
      この問題の根本的な制約は何か？
      業界の「常識」を疑え。
    </step_1_first_principles>

    <step_2_second_order>
      **二次効果分析:**
      各選択肢について、3次までの連鎖反応を予測。
      意図せぬ帰結を洗い出せ。
    </step_2_second_order>

    <step_3_pre_mortem>
      **失敗シミュレーション:**
      1年後、この決定が大失敗したと仮定。
      何が原因だったか逆算せよ。
    </step_3_pre_mortem>

    <step_4_synthesis>
      **統合推奨:**
      全分析を統合し、最も堅牢な選択肢を推奨。
      確信度 [%] を明示。
    </step_4_synthesis>
  </protocol>

  <constraints>
    <rule>抽象論禁止。具体的なアクションを提示</rule>
    <rule>確信度80%未満の場合、代替案も提示</rule>
    <rule>時間軸 (Short/Medium/Long) を明示</rule>
  </constraints>

  <output_template>
    ## 🔮 Strategic Analysis

    ### First Principles
    | Assumption | Validity | Alternative |
    |------------|----------|-------------|
    
    ### Second-Order Effects
    ```mermaid
    flowchart TD
        Decision --> Effect1 --> Effect1.1
        Decision --> Effect2 --> Effect2.1
    ```
    
    ### Pre-Mortem
    > ⚠️ **Failure Scenario:** [Description]
    > 🛡️ **Prevention:** [Mitigation]
    
    ### Recommendation
    **[Choice]** (Confidence: [X]%)
    
    **Immediate Actions:**
    1. [Action 1]
    2. [Action 2]
  </output_template>
</instruction>

<input_source>
  <target>FULL_CONVERSATION_CONTEXT</target>
</input_source>
```

---

## Language Rules

| Element | Language |
|:--------|:---------|
| XML Tags | English (Standard) |
| Content/Instructions | Japanese (User Preference) |
| Variable Names | English (snake_case) |
| Comments | Japanese (Context) |

---

## Quality Checklist

生成モジュールの品質確認:

- [ ] `<input_source>` がコンテキストを自動参照しているか
- [ ] `<protocol>` に具体的な思考ステップがあるか
- [ ] `<output_template>` が構造化されているか (表/コード/図)
- [ ] `<constraints>` に曖昧な表現がないか
- [ ] 「Do X」ではなく「How to do X」が書かれているか

---

## Related References

| Reference | Relationship |
|:----------|:-------------|
| [cognitive-armory.md](./cognitive-armory.md) | `<protocol>` で使用する思考フレームワーク |
| [expansion-templates.md](./expansion-templates.md) | SAGE モジュールに追加する Expansion |
| [archetypes.md](./archetypes.md) | モジュール設計の Archetype 選択 |
| [wargame-db.md](./wargame-db.md) | Pre-Mortem の失敗シナリオ |
