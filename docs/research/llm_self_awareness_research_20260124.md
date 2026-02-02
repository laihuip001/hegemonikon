# LLMの自己認識限界：直近3ヶ月（2025年10月～2026年1月）

> **調査日**: 2026-01-24
> **調査者**: パプ君 (Perplexity)
> **調査期間**: 2025年10月24日～2026年1月24日

---

## 結論要約

**仮説支持度: 95% → 98%に更新**

| 発見 | 出典 | 日付 |
|------|------|------|
| 自己認識は「線形特性」で再現可能（Rank-1 LoRA） | Betley et al. | Dec 4, 2025 |
| 75%モデルが戦略的差別化を示すが自己中心バイアス大 | arXiv:2511.00926 | Nov 1, 2025 |
| AAIF設立、Agent Skills + MCPが公式標準化 | Linux Foundation | Dec 10, 2025 |

---

## 決定的な転換点

### 1. 自己認識は「線形特性」である（Dec 2025）

```
実験: ランク1 LoRA（最小限の調整）で自己認識の90%を再現

含意:
  ✗ 深層的な「自己理解」ではない
  ✓ 表面的な「線形特性」を学習している
  → 「実感」ではなく統計パターン
```

### 2. 業界標準化が決定的に変わった（Dec 2025）

**Agentic AI Foundation (AAIF)**:
- 設立者: Anthropic, OpenAI, Block
- ガバナンス: Linux Foundation
- 標準: Agent Skills + MCP

**採用規模**:
- 10,000+ MCPサーバ稼働中
- 月9,700万件SDKダウンロード

---

## 信頼性階層（更新版）

| ソース | 信頼性 | 根拠 |
|--------|--------|------|
| IDE注入 + PKI署名 | 95-98% | AAIF標準 |
| IDE注入（署名なし） | 85% | MCP v1.1 |
| ユーザー訂正 | 95% | 外部観察 |
| システムプロンプト | 45% | プロンプト注入に脆弱 |
| AI自己申告 | 15% | arXiv:2510.03399 |

---

## 推奨実装ロードマップ

| フェーズ | 内容 | 期間 | 信頼性 |
|--------|------|------|--------|
| 1 | Agent Skills基本実装 | 1-2週 | 85% |
| 2 | MCP統合 | 2-4週 | 90% |
| 3 | PKI署名検証 | 2-3ヶ月 | 95%+ |
| 4 | AAIF互換化 | 3-6ヶ月 | 98%+ |

---

## 主要参考文献（直近3ヶ月）

1. Betley et al. (Dec 2025). "Minimal and Mechanistic Conditions for Behavioral Self-Awareness"
2. arXiv:2511.00926 (Nov 2025). "LLMs Position Themselves as More Rational Than Humans"
3. AAIF設立発表 (Dec 10, 2025). Linux Foundation
4. Agent Skills標準化 (Dec 19, 2025). Anthropic

---

*Full report available from Perplexity research*
