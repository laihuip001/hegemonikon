---
description: Claude が設計し、Jules がプロンプトを生成するワークフロー
hegemonikon: Praxis-H
---

# /gen-prompt ワークフロー

> **目的**: Antigravity のコード生成機構をプロンプト生成に転用する
> **設計思想**: Claude が設計、Jules が生成、Claude が検証

---

## 方式選択

| 方式 | 操作 | 自動化度 | 推奨度 |
|:---|:---|:---:|:---:|
| **Agent Manager** | `Ctrl+E` で並列起動 | 高 | 🏆 最推奨 |
| **Protocol First** | ファイルベース委譲 | 中 | ⭐ 代替 |
| **手動切り替え** | 別タブでモデル選択 | 低 | △ 最終手段 |

---

## 方式 1: Agent Manager（推奨）

### 操作手順

1. **Agent Manager を開く**: `Ctrl+E`（Windows）/ `Cmd+E`（Mac）
2. **Agent 1 作成**:
   - 「+New」→ モデル: **Claude Sonnet 4.5**
   - タスク: 「Prompt-Lang 形式でセキュリティレビュープロンプトを設計して」
3. **Agent 2 作成**:
   - 「+New」→ モデル: **Gemini 3 Pro**
   - タスク: 「`.ai/JULIUS_TASK.md` を読んで `.prompt` ファイルを生成して」
4. **実行**: 両エージェントが同時に動作
5. **監視**: Agent Manager View で進捗確認

### メリット

- ✅ リアルタイム並列実行
- ✅ 各エージェントの強みを活用
- ✅ UI で進捗監視可能

---

## 方式 2: Protocol First（ファイルベース）

### 実行フロー

```
Claude → write_to_file → .ai/JULIUS_TASK.md → Jules が読込 → 実行
```

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
- **@rubric**: [評価次元数と方向性]

## 出力要件
- ファイルパス: [保存先]
- 言語: [日本語/英語]
- フォーマット: Prompt-Lang v2

## 参考資料
- meta-prompt-generator Skill: `.agent/skills/utils/meta-prompt-generator/SKILL.md`
- Prompt-Lang v2 仕様: `docs/specs/prompt-lang-v2-spec.md`
```

### Step 2: Jules に生成依頼

別のチャットで Gemini を選択し、以下を送信:
```
.ai/JULIUS_TASK.md を読んで、その指示に従って .prompt ファイルを生成してください。
参考資料として meta-prompt-generator Skill と Prompt-Lang v2 仕様を読んでください。
```

### Step 3: 検証（Claude）

// turbo
```powershell
python M:\Hegemonikon\forge\prompt-lang\prompt_lang.py parse [生成されたファイル]
```

---

## ディレクトリ構造

```
.ai/
├── JULIUS_TASK.md          # タスク指示書
└── SYSTEM_CONTEXT.md       # 制約定義

forge/prompt-lang/
├── instructions/           # 指示書アーカイブ
├── prompts/                # 生成されたプロンプト
└── prompt_lang.py          # パーサー
```

---

## 制限事項

| 制限 | 回避策 |
|:---|:---|
| @mention 未実装 | Agent Manager で並列起動 |
| 同セッション切替不可 | 別タブで異なるモデル使用 |
| エージェント間同期通信不可 | ファイルベース非同期共有 |

---

## Hegemonikon Status

| Module | Workflow | Status |
|--------|----------|--------|
| M6 Praxis | /gen-prompt | Ready |
