# Antigravity IDE MCP サポート調査結果

> **調査日**: 2026-01-24
> **調査者**: パプ君 (Perplexity)
> **結論**: ✅ **完全サポート実装済み**

---

## 結論サマリー

| 項目 | 状態 | 信頼度 |
|------|------|--------|
| MCP クライアント機能 | ✅ 完全実装 | 本番OK |
| Agent Skills 統合 | ✅ AAIF標準準拠 | 本番OK |
| カスタム MCP サーバー | ✅ Python/Node.js | 本番OK |
| GUI 設定 | ✅ MCP Servers パネル | 安定 |
| プロジェクトレベル設定 | ⚠️ グローバルのみ | 2026年対応予定 |
| モデル切り替え通知 | ⚠️ 未実装 | 手動対応 |

---

## 設定ファイルの場所

- **Windows**: `%APPDATA%\Antigravity\mcp_config.json`
- **Mac/Linux**: `~/.antigravity/mcp_config.json`

---

## mcp_config.json フォーマット

```json
{
  "mcpServers": {
    "hegemonik": {
      "command": "python",
      "args": ["M:/Hegemonikon/mcp/hegemonik_model_info.py"]
    }
  }
}
```

---

## 推奨実装ロードマップ

| 週 | 内容 | 成果物 |
|----|------|--------|
| 1 | MCP ストアから事前構築サーバーを試す | 動作確認 |
| 2 | 自作 MCP（モデル情報プロバイダー）実装 | hegemonik_model_info.py |
| 3 | Agent Skills と統合 | SKILL.md + @mcp:hegemonik |
| 4 | Hegemonikón v2.0 完成・検証 | Agent Identifier 自動化 |

---

## 主要参考文献

1. Google Codelab: Authoring Google Antigravity Skills (2026-01-18)
2. Google Cloud Blog: 企業データをAntigravity IDEに接続 (2025-12-24)
3. Atlassian Blog: Google AntigravityでのJiraアプリ構築 (2026-01-20)

---

*Full report available from Perplexity research*
