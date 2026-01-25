# 調査結果: Claude ↔ Jules 通信方法

**調査日**: 2026-01-25
**情報源**: Perplexity Deep Research

---

## 結論サマリー

| 手法 | 可能性 | 推奨度 |
|:---|:---:|:---:|
| @mention 記法 | ❌ 未実装 | - |
| API 直接呼び出し | ❌ 未実装 | - |
| **ファイルベース委譲** | ✅ 実装済 | 🏆 推奨 |
| **Agent Manager 並列実行** | ✅ 実装済 | 🏆 推奨 |
| **MCP ツール共有** | ✅ 実装済 | ⭐ 補助 |

---

## 重要な発見

### 1. Agent Manager の存在

**アクセス方法**: `Cmd+E` (Mac) / `Ctrl+E` (Windows)

**機能**:
- 複数エージェントを同時起動
- 各エージェントに異なるモデルを割り当て可能（Claude, Gemini）
- 「ミッションコントロール」ダッシュボードで監視

### 2. モデル選択機能

**操作**: チャット入力欄上の「Select Model」ドロップダウン

**選択肢**:
- Gemini 3 Pro (デフォルト)
- Gemini 3 Flash
- Claude Sonnet 4.5
- Claude Opus 4.5

**制限**: 同じ会話内での切り替えは不可（新しい会話が必要）

---

## 推奨パターン

### Pattern 1: Agent Manager 並列実行

```
Agent 1 (Claude Sonnet): 設計・計画
Agent 2 (Gemini Pro): 実装・コード生成
→ 同時に異なるタスクを実行
→ Agent Manager で両者を監視
```

### Pattern 2: Protocol First（ファイルベース）

```
Claude → .ai/JULIUS_TASK.md → Jules が読込 → 実行
```

---

## 今後のアクション

1. **Agent Manager を試す**: `Ctrl+E` で起動
2. **複数エージェント並列実行**を検証
3. **ワークフロー更新**: Agent Manager パターンを追加
