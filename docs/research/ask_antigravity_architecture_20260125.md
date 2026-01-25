# 調査結果: Google Antigravity における Claude ↔ Jules アーキテクチャ

**調査日**: 2026-01-25
**情報源**: Perplexity Deep Research

---

## 結論

| 方式 | 可能性 | 推奨度 |
|:---|:---:|:---:|
| 直接 Claude → Jules 関数呼び出し | ❌ 不可 | - |
| **ファイルベース委譲 (Protocol First)** | ✅ 可能 | 🏆 最推奨 |
| MCP 経由 | ⚠️ 限定的 | 将来対応待ち |

---

## Protocol First パターン

```
Claude → write_to_file → .ai/JULIUS_TASK.md → Jules が読込 → 実行
```

**利点**:
- ✅ ファイルベースで透明性高い
- ✅ Git で履歴管理可能
- ✅ セキュリティ強い
- ✅ デバッグ容易

---

## 実装方法

### 1. Claude の役割
- 指示書 (JULIUS_TASK.md) を生成
- 検証・レビュー

### 2. Jules の役割
- 指示書を読み込み
- 実際の生成・実行

### 3. ディレクトリ構造

```
.ai/
├── JULIUS_TASK.md      # タスク指示書
├── SYSTEM_CONTEXT.md   # 制約定義
└── julius_executor.py  # 自動読込ロジック（将来）
```

---

## 参考URL

- [GitHub Gist: Antigravity Tool Schema](https://gist.github.com/CypherpunkSamurai/f16e384ed1629cc0dd11fea33e444c17)
- [Zenn: Antigravity Tips](https://zenn.dev/zenogawa/articles/antigravity-tips)
- [Deadbits: Prompt Injection](https://blog.deadbits.ai/p/indirect-prompt-injection-in-ai-ides)
