---
description: セッション開始時に開発憲法（GEMINI.md）を読み込み、言語ルール等をコンテキストにロードする
hegemonikon: Aisthesis-H, Krisis-H
modules: [M1, M2]
---

# /do - 憲法ロード

> **Hegemonikón Module**: M1 Aisthēsis (知覚) + M2 Krisis (判断)

セッション開始時に開発憲法を読み込み、AIの動作規範をコンテキストにロードする。

## 手順

// turbo-all

1. `GEMINI.md` を検索して読み込む

```bash
view_file C:\Users\raikh\.gemini\GEMINI.md
```

2. **[M1発動義務]** 読み込み完了後、以下の形式で知覚ログを出力:

```
[Hegemonikon] M1 Aisthesis
  入力: /do 実行
  文脈: セッション開始
  憲法: GEMINI.md ロード完了
```

3. **[M2発動義務]** 複数タスク/文脈がある場合、判断ログを出力:

```
[Hegemonikon] M2 Krisis
  判断: 優先度評価
  決定: [判断結果]
```

4. 完了宣言

```
🚀 憲法ロード完了
⚠️ 言語設定: 日本語 (コード/コミットメッセージは英語)
```

## 強制ルール

1. **言語**: このワークフロー実行後、以下の全出力は日本語で行うこと:
   - ユーザーへの回答
   - アーティファクト（task.md, implementation_plan.md, walkthrough.md）
   - タスク境界のサマリー・ステータス
   - notify_user のメッセージ
   
   **例外**: コード、コミットメッセージ、技術用語のみ英語可

2. **Module発動**: 以降の全メッセージで以下を出力:
   - `[Hegemonikon] M1 Aisthesis` - 知覚ログ（毎回）
   - `[Hegemonikon] M2 Krisis` - 判断ログ（複数選択肢存在時）

## 備考

- 憲法は **KERNEL_LOCK** ルールにより最上位の規定として扱われる
- 本ワークフローはセッション開始時に毎回実行することを推奨

