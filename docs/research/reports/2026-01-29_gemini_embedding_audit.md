# Gemini Embedding 監査レポート

## 2026年1月29日 08:50 JST

---

## 監査結論

**✅ 影響なし — Hegemonikón は Gemini text-embedding-004 を使用していません**

---

## 監査結果

### 使用中の Embedding モデル

| モジュール | モデル | プロバイダ | 次元 | 状態 |
|-----------|--------|----------|------|------|
| **mekhane/anamnesis/** | BGE-small (ONNX) | ローカル | 384 | ✅ 正常 |
| **mekhane/symploke/** | all-MiniLM-L6-v2 | ローカル (sentence-transformers) | 384 | ✅ 正常 |
| **mekhane/peira/** | BGE-small (ONNX) | ローカル | 384 | ✅ 正常 |
| **mcp/** | all-MiniLM-L6-v2 | ローカル (sentence-transformers) | 384 | ✅ 正常 |

### 検索対象

```
/home/laihuip001/oikos/hegemonikon/
├── mekhane/anamnesis/    → BGE-small ONNX
├── mekhane/symploke/     → all-MiniLM-L6-v2
├── mekhane/peira/        → BGE-small ONNX
└── mcp/                  → all-MiniLM-L6-v2
```

### 検索クエリ結果

| クエリ | ヒット数 | 結果 |
|--------|---------|------|
| `text-embedding-004` | 0 (レポートファイルのみ) | 使用なし |
| `embedding-004` | 0 (レポートファイルのみ) | 使用なし |
| `gemini.*embed` | 0 (ドキュメントのみ) | 使用なし |
| `EmbeddingModel` | 0 | 使用なし |

---

## 結論

Hegemonikón の設計方針として、**すべての embedding はローカルモデル**（BGE-small ONNX または sentence-transformers）を使用しています。

**Gemini API への依存がないため、2026年1月14日の text-embedding-004 shutdown による影響はありません。**

---

## 推奨事項

1. **現状維持** — ローカル embedding モデルの使用を継続
2. **将来の検討** — より高精度な embedding が必要な場合、以下を検討:
   - `text-embedding-005` (Gemini)
   - `text-embedding-3-small` / `text-embedding-3-large` (OpenAI)
   - ローカル: `nomic-embed-text` (1024 dims, Apache 2.0)

---

**監査者**: Hegemonikón Auditor  
**監査日時**: 2026年1月29日 08:50 JST
