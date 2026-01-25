# Antigravity アーキテクチャ調査 — 最終レポート

**調査日**: 2026-01-25
**情報源**: Perplexity Deep Research（複数回）

---

## 1. 最終結論

### Claude ↔ Jules の関係

| 質問 | 答え |
|:---|:---|
| Jules は暗黙的に介在しているか？ | **いいえ** |
| Claude のツール実行者は誰か？ | **Antigravity Runtime** |
| Jules と Claude の関係は？ | **完全に独立** |
| Claude から Jules を直接呼べるか？ | **いいえ**（Runtime が仲介） |

### アーキテクチャ

```
Claude → ツール提案 → Antigravity Runtime → 実行
                              ↓ 必要に応じて
                          Jules（Agent Manager 経由）
                              ↓
                          Google Cloud VM
```

---

## 2. Pro vs Ultra の差異

| プラン | Jules 同時実行 | 倍率 |
|:---|:---:|:---:|
| **Pro** | 1〜3タスク | 基準値 |
| **Ultra** | 最大20タスク | **20倍** |

**出典**: https://support.google.com/googleone/answer/16286513?hl=ja-JP

---

## 3. UI に「Jules」が表示されない理由

- 「Jules」は **製品名/ブランド名**
- UI のモデル選択には「Gemini 3 Pro」として表示
- Agent Manager で起動するエージェントが「Jules」と呼ばれる
- 公式ドキュメントには「Jules」の正式定義がない

---

## 4. 確認済み事項

| 項目 | 状態 |
|:---|:---:|
| Antigravity は Agent-First IDE | ✅ 公式 |
| Editor View（同期）と Agent Manager（非同期）| ✅ 公式 |
| Browser Sub-Agent が別モデルで実行 | ✅ 公式 |
| Rules / Workflows / Skills でカスタマイズ可能 | ✅ 公式 |
| Pro/Ultra で同時実行数が異なる | ✅ 公式 |

---

## 5. 未確認/不透明な事項

| 項目 | 状態 |
|:---|:---:|
| Google Cloud VM の使用 | ❓ 公式未記載 |
| 「Jules」の正式定義 | ❓ 公式未記載 |
| モデル置き換わり現象の原因 | ❓ Reddit 報告のみ |
| Browser Sub-Agent のモデル選択 | ❓ ユーザー制御不可 |

---

## 6. 参考URL

| 情報源 | 信頼度 |
|:---|:---:|
| Google Antigravity Codelab | ⭐⭐⭐⭐⭐ |
| Google One ヘルプ（Pro/Ultra） | ⭐⭐⭐⭐⭐ |
| 9to5Google（Pro vs Ultra 比較） | ⭐⭐⭐⭐ |
| Reddit（ユーザー報告） | ⭐⭐⭐ |
