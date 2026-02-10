# thought_signature ハンドリングガイド

> **Source:** 2026-02-10 LLM API 変更監視 + プロンプト技法最前線
> **Purpose:** Gemini 3 API で必須の thought_signature トークンの仕様と実装ガイド

---

## 概要

Gemini 3 では、マルチターン会話と Function Calling において
`thought_signature` という暗号化トークンが**必須**となった。

このトークンは:

- モデルの思考過程を暗号化したもの
- レスポンスに含まれ、次リクエストに添付する必要がある
- マルチターンでの文脈保持とFCの正確性を保証する

---

## API 仕様

### レスポンスからの取得

```json
{
  "candidates": [{
    "content": {
      "parts": [{"text": "..."}],
      "role": "model"
    },
    "thought_signature": "eyJhbGciOi..."
  }]
}
```

### 次リクエストへの添付

```json
{
  "contents": [
    {
      "role": "user",
      "parts": [{"text": "前回の続き"}]
    }
  ],
  "thought_signature": "eyJhbGciOi..."
}
```

---

## thinking_level パラメータ

旧来の `thinking_budget` に代わる新パラメータ。

| レベル | 説明 | コスト比 | 推奨 Archetype |
|:-------|:-----|:---------|:--------------|
| `minimal` | 思考を最小化 | 1x | Speed |
| `low` | 軽量な推論 | 1.5x | Autonomy, Creative |
| `high` | 深い推論 | 3x | Precision, Safety |

```json
{
  "generation_config": {
    "thinking_level": "high"
  }
}
```

---

## mekhane 実装ガイド

### 1. ミドルウェア設計

```python
class ThoughtSignatureMiddleware:
    """Gemini 3 の thought_signature を自動管理するミドルウェア"""
    
    def __init__(self):
        self._signatures: dict[str, str] = {}  # session_id -> signature
    
    def process_response(self, session_id: str, response: dict) -> dict:
        """レスポンスから thought_signature を抽出して保存"""
        if sig := response.get("candidates", [{}])[0].get("thought_signature"):
            self._signatures[session_id] = sig
        return response
    
    def prepare_request(self, session_id: str, request: dict) -> dict:
        """リクエストに thought_signature を添付"""
        if sig := self._signatures.get(session_id):
            request["thought_signature"] = sig
        return request
```

### 2. 適用対象

| 機能 | thought_signature | thinking_level |
|:-----|:-----------------:|:--------------:|
| 単発質問 | 不要 | 設定可 |
| マルチターン | **必須** | 設定可 |
| Function Calling | **必須** | 推奨: high |
| Streaming | 対応済み | 設定可 |

### 3. エラーケース

| エラー | 原因 | 対処 |
|:-------|:-----|:-----|
| `INVALID_THOUGHT_SIGNATURE` | 期限切れ or 改竄 | セッションリセット |
| `MISSING_THOUGHT_SIGNATURE` | 未添付 | ミドルウェア確認 |

---

## 注意事項

> [!WARNING]
> `thought_signature` はモデルの内部思考を含む暗号化トークンであり、
> ログに記録するとセキュリティリスクとなる可能性がある。
> 永続化する場合は暗号化ストレージを使用すること。

---

*v1.0 — thought_signature Handling Guide (2026-02-10)*
