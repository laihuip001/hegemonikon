# Antigravity でのプロンプト生成（PE）戦略

**作成日**: 2026-01-25
**目的**: Antigravity (Google AI Ultra) を用いてプロンプトを生成する最適な方法を整理

---

## 1. 現状の結論

### 質問: Jules にプロンプト生成を指示できるか?

| 方式 | 可能性 | 推奨度 |
|:---|:---:|:---:|
| Claude から直接 Jules を呼ぶ | ❌ 不可 | - |
| Agent Manager で Jules を起動 | ✅ 可能 | ⭐⭐ |
| Claude が設計 → 別タブで Gemini が生成 | ✅ 可能 | ⭐⭐⭐ |
| Claude が全て実行（現状） | ✅ 可能 | ⭐⭐⭐⭐ |

---

## 2. 各方式の詳細

### 方式 A: Claude が全て実行（現状・最もシンプル）

```
Claude → 設計 → 生成 → Claude → 検証
```

**長所**:
- ✅ 追加操作不要
- ✅ コンテキストが途切れない
- ✅ 一貫した品質管理

**短所**:
- ❌ Claude の特性に依存（Gemini の強みを活かせない）

---

### 方式 B: Agent Manager で並列実行

```
Agent 1 (Claude): 設計・レビュー
Agent 2 (Gemini): 生成
```

**操作**:
1. `Ctrl+E` で Agent Manager を開く
2. Agent 1 に「プロンプト設計」を割り当て（Claude）
3. Agent 2 に「プロンプト生成」を割り当て（Gemini）
4. 両者が並行して動作

**長所**:
- ✅ 各モデルの強みを活用
- ✅ Ultra なら最大20並列

**短所**:
- ❌ 操作が複雑
- ❌ コンテキスト共有が難しい

---

### 方式 C: Protocol First（ファイルベース委譲）

```
Claude → .ai/JULIUS_TASK.md → (手動切替) → Gemini が読んで生成
```

**操作**:
1. Claude が指示書を生成（`.ai/JULIUS_TASK.md`）
2. 別タブで Gemini を選択
3. 「指示書を読んで実行」と依頼
4. Claude で検証

**長所**:
- ✅ 指示が劣化しない
- ✅ Git で履歴管理可能

**短所**:
- ❌ 手動切替が必要
- ❌ リアルタイムではない

---

## 3. Google AI Ultra の活用方法

### Ultra の特典

| 項目 | Pro | Ultra |
|:---|:---:|:---:|
| Jules 同時実行 | 1〜3 | 最大20 |
| 優先モデルアクセス | 制限あり | あり |
| 使用量上限 | 高い | 最大 |

### Ultra で可能になること

```
Agent Manager で複数プロンプトを同時生成:

Task 1: セキュリティレビュー.prompt → Agent 1
Task 2: API ドキュメント.prompt → Agent 2
Task 3: コードコメント.prompt → Agent 3
...
（最大20並列）
```

---

## 4. 私の推奨（/u）

### 現時点での最適解

**方式 A（Claude が全て実行）が最もシンプルで効率的。**

理由:
1. コンテキストが途切れない
2. meta-prompt-generator Skill を活用できる
3. パーサーで即座に検証できる
4. 追加操作が不要

### Ultra を活かす場合

**大量のプロンプトを一括生成する場合のみ、Agent Manager を使う価値がある。**

例:
- 10種類のプロンプトを同時生成
- 複数の Archetype でバリエーション生成
- A/B テスト用に複数候補を並列生成

---

## 5. 実装ワークフロー

### シンプル版（推奨）

```
1. Claude に「セキュリティレビュープロンプトを生成して」と依頼
2. Claude が meta-prompt-generator Skill を使用
3. Claude が Prompt-Lang v2 形式で生成
4. パーサーで検証
5. 必要なら修正
```

### Ultra 活用版

```
1. Agent Manager を開く（Ctrl+E）
2. 複数の Agent を起動（各々異なるプロンプト課題）
3. 各 Agent が独立して生成
4. 結果を Claude でレビュー・統合
5. パーサーで一括検証
```

---

## 6. まとめ

| 状況 | 推奨方式 |
|:---|:---|
| 単発のプロンプト生成 | **Claude 単独** |
| 複数プロンプトの一括生成 | **Agent Manager（Ultra）** |
| 厳密な品質管理が必要 | **Protocol First** |
| 探索的な生成 | **Agent Manager 並列** |

**現状の最適解は「Claude 単独」であり、これを今後も継続して問題ない。**
