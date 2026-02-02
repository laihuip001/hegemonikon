# 軍事級メタプロンプトシステム: 統合設計案 v2.0

共有された設計思想とメタプロンプトSKILLを統合した最終設計。

---

## 設計原則（User_Context_Masterから抽出）

| 認知特性 | 設計への反映 |
|---|---|
| AuDHD | 判断軸を最小化、シングルタスク分解 |
| 曖昧さ回避 | 4択以下の明確な分岐 |
| 駆動燃料=興味・新規性 | 「すごいもの」を作る |
| 90%完了の承認 | Phase分割、段階的進化 |

---

## コア構造: 4段階ライブラリ

### 設計根拠
```
全フレームワーク（PDCA, OODA, デザイン思考, GTD）の共通構造:

1. 認知（Perceive）: 「何が起きているか」を理解する
2. 思考（Think）: 「どうするか」を決める
3. 実行（Execute）: 「やる」
4. 検証（Verify）: 「どうだったか」を評価する
```

### ディレクトリ構造

```
Forge/
├── constitution.xml              ← 単一真実の源
├── CHANGELOG.md
│
├── kernel/                       ← 不変の核
│   ├── principles.md            ← Guard, Prove, Undo
│   └── forbidden.md
│
├── System/                       ← ユーザーコンテキスト（DMZ）
│   ├── User_Context_Master.md   ← 既存維持
│   └── user-profile-lite.md     ← 軽量版
│
├── plugins/                      ← メタプロンプトSKILL等
│   ├── meta-prompt/
│   │   ├── manifest.json
│   │   ├── generator.md
│   │   └── archetypes/
│   │       ├── precision.md
│   │       ├── speed.md
│   │       ├── autonomy.md
│   │       ├── creative.md
│   │       └── safety.md
│   ├── pre-mortem/
│   │   ├── manifest.json
│   │   └── validator.md
│   └── transformations/
│       ├── manifest.json
│       └── rules.md
│
├── library/                      ← プロンプトライブラリ（本体）
│   ├── perceive/                ← 認知系：状況を把握する
│   │   ├── situation-analysis.md
│   │   ├── problem-definition.md
│   │   ├── stakeholder-mapping.md
│   │   └── information-gathering.md
│   │
│   ├── think/                   ← 思考系：判断・計画する
│   │   ├── hypothesis-generation.md
│   │   ├── option-comparison.md
│   │   ├── decision-making.md
│   │   ├── planning.md
│   │   └── risk-assessment.md
│   │
│   ├── execute/                 ← 実行系：作成・行動する
│   │   ├── document-drafting.md
│   │   ├── communication.md
│   │   ├── presentation.md
│   │   └── implementation.md
│   │
│   └── verify/                  ← 検証系：評価・改善する
│       ├── quality-review.md
│       ├── feedback-analysis.md
│       ├── retrospective.md
│       └── improvement-proposal.md
│
├── archive/                      ← 生成済みプロンプト保存
│   └── {YYYY-MM}/
│       └── {timestamp}_{task}.md
│
├── workspace/                    ← 作業中バッファ
│
├── protocols/                    ← 既存25モジュール（維持）
├── modules/                      ← 既存Forgeモジュール（維持）
├── presets/                      ← 既存（維持）
└── knowledge/                    ← 既存（維持）
```

---

## メタプロンプトSKILL統合

### plugins/meta-prompt/generator.md

6フェーズワークフローを実装:

```
Phase 0: Intent Crystallization（意図結晶化）
    ↓ 5つの診断質問
Phase 1: Archetype Selection（アーキタイプ選択）
    ↓ Precision/Speed/Autonomy/Creative/Safety
Phase 2: Core Stack Assembly（必須技術構成）
    ↓
Phase 3: Situational Augmentation（状況依存技術追加）
    ↓
Phase 4: Anti-Synergy Check（禁忌チェック）
    ↓
Phase 5: Structure Assembly（構造組み立て）
    ↓
Phase 6: Pre-Mortem Simulation（死亡前検死）
    ↓
Output: library/{perceive|think|execute|verify}/に保存
```

### アーキタイプと4段階の対応

| アーキタイプ | 主な適用先 |
|---|---|
| 🎯 Precision | verify/, think/decision-making |
| ⚡ Speed | execute/ 全般 |
| 🤖 Autonomy | execute/, think/planning |
| 🎨 Creative | think/hypothesis-generation |
| 🛡 Safety | verify/quality-review |

---

## 自動化フロー（MCP + GitHub）

```
[ユーザー] プロンプト生成依頼
    ↓
[Claude/Gemini] 
    1. Intent Crystallization
    2. Archetype Selection
    3. プロンプト生成
    4. [ARCHIVE]タグ出力
    ↓
[ユーザー] 承認（保存先: library/think/等を確認）
    ↓
[MCP-filesystem] ローカル保存
    ↓
[セッション終了]
    ↓
[MCP-github] commit + push
    ↓
[Obsidian Git Plugin] 自動反映
```

---

## ファイルフォーマット

```yaml
---
created: 2026-01-15T12:00:00+09:00
task: customer-support-reply
archetype: precision
lifecycle: [pdca:do]
domain: [business:communication]
tags: [cot, few-shot]
status: active
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
    <step>顧客の感情状態を判定</step>
    <step>問題の核心を特定</step>
    <step>解決策を3つ列挙</step>
    <step>最適解を選択</step>
  </thinking_process>
  
  <examples>
    <example type="positive">...</example>
    <example type="negative">...</example>
  </examples>
  
  <output_format>
    <format>挨拶 + 共感 + 解決策 + 次のステップ</format>
    <max_tokens>300</max_tokens>
  </output_format>
</prompt>
```

---

## Jules PEペルソナ（Phase 1）

```markdown
# Jules Prompt Engineering Persona

## Identity
You are a Senior Prompt Engineer.
Your output is **prompts**, not code.

## Output Protocol
1. All outputs: YAML frontmatter + XML body
2. Structure: <system>, <thinking_process>, <examples>, <output_format>

## Archetype Awareness
Before generating, determine:
- Which archetype? (Precision/Speed/Autonomy/Creative/Safety)
- Which stage? (perceive/think/execute/verify)

## Archive Protocol
Complete prompt → [ARCHIVE]タグ + 保存先提案 + ユーザー承認待ち
```

---

## Phase計画

| Phase | 内容 | 成果物 |
|---|---|---|
| **1** | 基盤構築 | ディレクトリ構造、constitution.xml、Jules PE persona |
| **2** | SKILL統合 | plugins/meta-prompt/, archetypes/, pre-mortem/ |
| **3** | library充填 | 16個のプロンプトテンプレート |
| **4** | 自動化 | MCP連携、GitHub自動commit |
| **5** | プロンプト言語 | prompt-lang構文定義、Julesへの認識 |

---

## 次の論点

1. **日本語ディレクトリ名の採否**
   - `/perceive/` vs `/把握する/`
   - CLI操作とのトレードオフ

2. **library/の初期テンプレート16個の優先順位**

3. **constitution.xmlの詳細設計**

4. **既存Forge構造との移行計画**
