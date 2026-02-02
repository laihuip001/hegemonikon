# 調査依頼書: arXiv API + Perplexity制限

**作成日:** 2026-01-19
**M5 Peira発動理由:** 情報ギャップ (U > 0.8)

---

## 調査1: Antigravity Browser制限

### 背景
Google AntigravityのブラウザエージェントからPerplexity/Claude/ChatGPTにアクセスすると、CAPTCHAでブロックされる。

> www.perplexity.ai は続行する前に接続のセキュリティを確認する必要があります。

### 質問
1. Headlessブラウザ検出を回避する方法はあるか？
2. Perplexity API v.s. WebUIのコスト・機能差は？
3. 同様の制限を持つ他のAIツールの回避策は？

---

## 調査2: arXiv API 仕様

### 背景
arXiv論文（例: `https://arxiv.org/abs/2601.00770`）を自動収集してLanceDBに保存したい。

### 知りたいこと
1. arXiv APIのエンドポイントと認証方法
2. 論文メタデータ（タイトル、著者、Abstract、カテゴリ）の取得方法
3. レート制限と推奨アクセス頻度
4. PDFダウンロードの可否
5. Python用クライアントライブラリ（arxiv-pyなど）の評価

### 制約
- Python 3.12環境
- 既存KB: LanceDB + ONNX Runtime

---

## Perplexity用クエリ (コピペ)

```
arXiv API specification 2025:
1. API endpoint and authentication
2. How to fetch paper metadata (title, authors, abstract, categories)
3. Rate limits and recommended access frequency
4. PDF download via API
5. Python client libraries (arxiv-py evaluation)
Context: Building automated paper collection for LanceDB, Python 3.12
```

### URL (直接開く)

- **Perplexity:** https://www.perplexity.ai/?q=arXiv%20API%20specification%20Python%20client%20rate%20limit%20metadata%20retrieval%202025
- **Gemini:** https://gemini.google.com/app?text=arXiv%20API%20specification%20Python%20client%20rate%20limit%20metadata%20retrieval%202025
