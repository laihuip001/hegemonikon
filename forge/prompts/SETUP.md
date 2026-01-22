# 🎯 Hegemonikón AI設定 セットアップガイド

> **目的**: Claude.ai と パプ君（Perplexity）をHegemonikón原理に基づいて統一設定

---

## 📁 作成済みファイル

| ファイル | 用途 |
|----------|------|
| [`claude-profile.md`](file:///M:/Hegemonikon/forge/prompts/claude-profile.md) | Claude.ai / Desktop 設定 |
| [`perplexity-profile.md`](file:///M:/Hegemonikon/forge/prompts/perplexity-profile.md) | Perplexity Spaces / 調査テンプレート |

---

## 🔧 セットアップ手順

### 1️⃣ Claude.ai Projects 設定

1. [Claude.ai](https://claude.ai) → **Projects** → **新規作成**
2. Project名: `Hegemonikón`
3. **Project Instructions** に `claude-profile.md` の内容をペースト
4. **Knowledge** に追加:
   - `M:\Hegemonikon\STRUCTURE.md`
   - `M:\Hegemonikon\.agent\workflows\` (必要なもの)

### 2️⃣ Perplexity Spaces 設定

1. [Perplexity.ai](https://perplexity.ai) → **Spaces** → **新規作成**
2. Space名: `Hegemonikón Research`
3. **Instructions** に `perplexity-profile.md` のinstructions部分をペースト
4. Focus Areas を設定:
   - AI/LLM
   - Prompt Engineering
   - ソフトウェア開発

### 3️⃣ Claude Desktop MCP（設定済み）

現在の設定:
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx.cmd",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "M:\\"]
    }
  }
}
```

追加推奨MCP:
- `memory` — 長期記憶
- `brave-search` — Web検索

---

## 🔄 Multi-PC同期

Google Drive同期により、`M:\` ドライブの設定は自動的に全PCで共有される:

```
M:\Hegemonikon\forge\prompts\  ← この設定ファイルも同期
```

---

## ✅ 検証チェックリスト

- [ ] Claude.ai Project作成
- [ ] Claude Project Instructionsにプロファイル適用
- [ ] Perplexity Space作成
- [ ] Perplexity Instructionsにプロファイル適用
- [ ] 動作テスト: Claude「Hegemonikónトーンで応答するか」
- [ ] 動作テスト: パプ君「構造化出力で回答するか」

---

*Hegemonikón v3.0 | 2026-01-21*
