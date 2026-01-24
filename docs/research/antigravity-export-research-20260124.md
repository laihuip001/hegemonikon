# Antigravity チャット履歴エクスポート技術調査報告書

> **Source**: Perplexity 調査 2026-01-24
> **結論**: Playwright DOM 抽出が最も現実的

---

## エグゼクティブサマリー

| 方法 | 実現可能性 | 推奨度 |
|:---|:---|:---|
| **🥇 Playwright DOM 抽出** | ✅ 70% | ⭐⭐⭐⭐⭐ |
| 手動 UI エクスポート | ✅ 100% | ⭐⭐⭐ |
| Gemini CLI + API | ⚪ 30% | ⭐⭐ |
| Google Takeout | ❌ 5% | ☆ |
| .pb デコード | ❌ 5% | ☆ |
| VS Code API | ⚪ 40% | ⭐ |

---

## 技術的発見

### .pb ファイルの暗号化

| 項目 | 値 |
|:---|:---|
| 暗号化アルゴリズム | AES-256-GCM |
| キー長 | 256 ビット |
| IV 長 | 12 バイト |
| キー保存場所 | GNOME Libsecret / Windows Credential Manager |
| 結論 | **復号化は実質不可能** |

### 公式エクスポート機能

- ❌ 存在しない
- Feature Request として Google AI Developer Forum に投稿されている
- ユーザーは `.pb` の直接バックアップを推奨している

---

## 推奨アーキテクチャ

```
Antigravity IDE
    ↓ (Playwright CDP 接続)
    ↓
DOM 抽出スクリプト (export_antigravity_chats.py)
    ├─ Markdown 出力
    ├─ JSON 出力
    └─ SQLite DB
    ↓
M:\Brain\.hegemonikon\sessions\
    ↓
LanceDB ベクトルインデックス
    ↓
M8 Anamnēsis (エピソード記憶)
```

---

## 実装ポイント

### CDP 接続

```python
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.connect_over_cdp("ws://localhost:9222")
```

### DOM セレクタ（要調整）

```python
# 会話リスト
conversations = await page.query_selector_all('[role="button"]')

# メッセージ
messages = await page.query_selector_all('div[role="log"] > div')
```

---

## 参考リンク

- [Google Antigravity Codelab](https://codelabs.developers.google.com/getting-started-google-antigravity)
- [Google AI Developer Forum - Bug Report](https://discuss.ai.google.dev/t/bug-report-undo-function-deletes-conversation-from-google-antigravity-agent-manager/111708)
- [Reddit r/google_antigravity](https://www.reddit.com/r/google_antigravity/comments/1qk7ldb/fix_corrupted_pb_conversation_file/)

---

*調査完了: 2026-01-24*
