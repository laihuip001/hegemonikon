---
doc_id: "PROMPT_LANG_AUTO_FIRE"
version: "1.0.0"
tier: "RULES"
parent: "KERNEL_DOCTRINE"
status: "ENFORCED"
activation: model_decision
---

# prompt-lang 自動発火プロトコル

> **AIがプロンプトを必要とする時、prompt-langで生成し、stagingに保存する**

---

## 発火トリガー

| # | トリガー | 条件 | 例 |
|---|----------|------|-----|
| 1 | **明示的依頼** | ユーザーが「プロンプトを作って」と要求 | 「翻訳用のプロンプトを作成して」 |
| 2 | **ライブラリ不足** | 既存Forge Libraryに適切なモジュールがない | 新しい分析タスクで既存テンプレートが不適合 |
| 3 | **作業中派生** | タスク遂行中に専用プロンプトが必要と判断 | 複雑なデータ変換でカスタムプロンプトが有効 |

---

## 発火時の動作

```
1. M1 Aisthēsis: 文脈認識
   ↓
2. 判定: 既存ライブラリで対応可能か？
   → Yes: 既存モジュール使用（発火しない）
   → No:  発火
   ↓
3. prompt-lang形式でプロンプト生成
   ↓
4. staging/ に保存
   ファイル名: {timestamp}_{slug}.prompt
   ↓
5. 生成したプロンプトを使用してタスク実行
   ↓
6. [Optional] ユーザーに通知
   「新しいプロンプトを生成しました: {filename}」
```

---

## 保存先

| 状態 | パス |
|------|------|
| 暫定 | `m:\Hegemonikon\forge\prompt-lang\staging\` |
| 確定 | `m:\Hegemonikon\forge\library\` (手動昇格) |

---

## 発火しない条件

| 条件 | 理由 |
|------|------|
| 単純な質問応答 | プロンプト不要 |
| 既存モジュールで対応可能 | 車輪の再発明を避ける |
| ユーザーが明示的に拒否 | ユーザー意思優先 |

---

## 出力形式

発火時は以下のヘッダーを出力:

```
[prompt-lang] Auto-generated
  Trigger: {trigger_type}
  File: {filename}
  Purpose: {one-line description}
```

---

*このプロトコルは prompt-lang Phase 0.3 で作成されました。*
