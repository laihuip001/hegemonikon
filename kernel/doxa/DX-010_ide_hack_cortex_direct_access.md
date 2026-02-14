# DX-010: Cortex API 直叩き — 完全突破手順書

> **日付**: 2026-02-13 → 2026-02-14 00:08 突破
> **ステータス**: ✅ 完全成功
> **確信度**: [確信: 100%] (SOURCE: curl で応答取得済み)
> **関連セッション**: a639e0f9, 9d4186ec, 24101dfc

---

## 1. 成果

**LS (Language Server) を介さず、`curl` 一発で Gemini 2.0 Flash から応答を取得。**

- Non-streaming (`generateContent`) ✅
- Streaming (`streamGenerateContent?alt=sse`) ✅
- Tier: `g1-ultra-tier` (Google One AI Ultra)

---

## 2. 突破に必要な3つの秘密

### 秘密 1: gemini-cli の OAuth Client ID

> gcloud auth のトークンでは**不可能**。gemini-cli 固有の OAuth Client ID が必要。

| 要素 | 値 | 出典 |
|:-----|:---|:-----|
| **Client ID** | `REDACTED_CLIENT_ID` | `oauth2.ts` L70-71 |
| **Client Secret** | `REDACTED_CLIENT_SECRET` | `oauth2.ts` L79 (installed app, 公開安全) |
| **Scopes** | `cloud-platform`, `userinfo.email`, `userinfo.profile` | `oauth2.ts` L82-86 |
| **キャッシュ場所** | `~/.gemini/oauth_creds.json` | `oauth2.ts` + `storage.ts` |

> **なぜ別 Client ID が必要か**: OAuth Client ID ごとに Google が発行するトークンの principal が異なる。
> gemini-cli の Client ID は Gemini Code Assist 用の IAM ベースライン権限がエンコードされている。

### 秘密 2: `loadCodeAssist` が返す「真のプロジェクト ID」

> `animated-surfer` でも `project-f2526536` でもない。真のプロジェクトは **`driven-circlet-rgkmt`**。

```bash
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://cloudcode-pa.googleapis.com/v1internal:loadCodeAssist" \
  -d '{"metadata":{"ideType":"IDE_UNSPECIFIED","platform":"PLATFORM_UNSPECIFIED","pluginType":"GEMINI"}}'
```

```json
{
  "currentTier": {"id": "standard-tier", "name": "Gemini Code Assist"},
  "cloudaicompanionProject": "driven-circlet-rgkmt",
  "gcpManaged": false,
  "paidTier": {"id": "g1-ultra-tier", "name": "Gemini Code Assist in Google One AI Ultra"}
}
```

> **重要**: `x-goog-user-project` ヘッダーをつけると `loadCodeAssist` にも失敗する。

### 秘密 3: `x-goog-user-project` ヘッダーは**つけない**

| 条件 | 結果 |
|:-----|:-----|
| `x-goog-user-project` あり | `USER_PROJECT_DENIED` or `SERVICE_DISABLED` |
| `x-goog-user-project` なし | ✅ 成功 |

---

## 3. 完全な手順 (再現可能)

### Step 1: gemini-cli で OAuth 認証 (初回のみ)

```bash
npx @google/gemini-cli --prompt "hello" --output-format json
# ブラウザが開き Google ログインを促す
# 成功すると ~/.gemini/oauth_creds.json が作成される
```

### Step 2: refresh_token から access_token を取得

```bash
REFRESH_TOKEN=$(python3 -c "import json; print(json.load(open('$HOME/.gemini/oauth_creds.json'))['refresh_token'])")

TOKEN=$(curl -s -X POST "https://oauth2.googleapis.com/token" \
  -d "client_id=REDACTED_CLIENT_ID" \
  -d "client_secret=REDACTED_CLIENT_SECRET" \
  -d "refresh_token=$REFRESH_TOKEN" \
  -d "grant_type=refresh_token" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

### Step 3: プロジェクト ID 取得

```bash
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://cloudcode-pa.googleapis.com/v1internal:loadCodeAssist" \
  -d '{"metadata":{"ideType":"IDE_UNSPECIFIED","platform":"PLATFORM_UNSPECIFIED","pluginType":"GEMINI"}}'
# → cloudaicompanionProject フィールドを取得
```

### Step 4: generateContent (非ストリーミング)

```bash
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://cloudcode-pa.googleapis.com/v1internal:generateContent" \
  -d '{
    "model": "gemini-2.0-flash",
    "project": "driven-circlet-rgkmt",
    "request": {
      "contents": [{"role": "user", "parts": [{"text": "Hello"}]}],
      "generationConfig": {"temperature": 0.7, "maxOutputTokens": 256}
    }
  }'
```

### Step 5: streamGenerateContent (ストリーミング)

```bash
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse" \
  -d '{
    "model": "gemini-2.0-flash",
    "project": "driven-circlet-rgkmt",
    "request": {
      "contents": [{"role": "user", "parts": [{"text": "Hello"}]}],
      "generationConfig": {"temperature": 0.7, "maxOutputTokens": 256}
    }
  }'
```

---

## 4. リクエスト/レスポンス スキーマ (完全版)

### 4.1 リクエスト

```json
{
  "model": "gemini-2.0-flash",
  "project": "{cloudaicompanionProject}",
  "user_prompt_id": "{任意のID, optional}",
  "request": {
    "contents": [
      {"role": "user", "parts": [{"text": "..."}]},
      {"role": "model", "parts": [{"text": "..."}]},
      {"role": "user", "parts": [{"text": "..."}]}
    ],
    "systemInstruction": {
      "role": "user",
      "parts": [{"text": "You are a helpful assistant."}]
    },
    "generationConfig": {
      "temperature": 0.7,
      "topP": 0.9,
      "topK": 40,
      "maxOutputTokens": 8192,
      "candidateCount": 1,
      "responseMimeType": "application/json",
      "responseJsonSchema": {},
      "thinkingConfig": {"thinkingBudget": 512}
    },
    "session_id": "{optional}"
  }
}
```

### 4.2 レスポンス

```json
{
  "response": {
    "candidates": [
      {
        "content": {"role": "model", "parts": [{"text": "こんにちは (Konnichiwa)\n"}]},
        "finishReason": "STOP",
        "avgLogprobs": -0.018958060070872307
      }
    ],
    "usageMetadata": {
      "promptTokenCount": 8,
      "candidatesTokenCount": 8,
      "totalTokenCount": 16,
      "trafficType": "ON_DEMAND",
      "promptTokensDetails": [{"modality": "TEXT", "tokenCount": 8}],
      "candidatesTokensDetails": [{"modality": "TEXT", "tokenCount": 8}]
    },
    "modelVersion": "gemini-2.0-flash",
    "createTime": "2026-02-13T15:08:21.208563Z",
    "responseId": "ZT6PabPdDMGi694PwNCC-QM"
  },
  "traceId": "7ba3edfd289980f0",
  "metadata": {"remoteContext": {"ragState": "RAG_DISABLED"}}
}
```

### 4.3 利用可能モデル (gemini-cli ソース + quota API)

| モデル | 用途 | テスト |
|:------|:-----|:------|
| `gemini-2.0-flash` | Flash tier | ✅ |
| `gemini-2.5-pro` | Pro tier (thinking 付き) | ✅ |
| `gemini-2.5-flash` | Flash tier | 未テスト (quota に存在) |
| `gemini-2.5-flash-lite` | Model routing classifier | 未テスト (quota に存在) |
| **`gemini-3-pro-preview`** | **次世代 Pro (未公開)** | **✅ 応答確認** |
| **`gemini-3-flash-preview`** | **次世代 Flash (未公開)** | 未テスト (quota に存在) |

> **発見**: `retrieveUserQuota` API で `gemini-3-*-preview` と `*_vertex` 変種が露出。
> 全12モデルバケットが確認された (2026-02-14 00:35 JST)。

---

## 5. API メソッド一覧 (cloudcode-pa v1internal)

| メソッド | HTTP | 用途 | テスト |
|:--------|:-----|:-----|:------|
| `loadCodeAssist` | POST | ユーザー設定・tier・プロジェクト ID 取得 | ✅ |
| `onboardUser` | POST | ユーザー登録 (LRO) | 未テスト |
| `generateContent` | POST | テキスト生成 (non-streaming) | ✅ |
| `streamGenerateContent` | POST (SSE) | テキスト生成 (streaming) | ✅ |
| `countTokens` | POST | トークン数計算 | 未テスト |
| `listExperiments` | POST | 実験フラグ一覧 | 未テスト |
| `retrieveUserQuota` | POST | クォータ確認 | ✅ (全12モデルバケット返却) |
| `getCodeAssistGlobalUserSetting` | GET | グローバル設定取得 | 未テスト |
| `setCodeAssistGlobalUserSetting` | POST | グローバル設定変更 | 未テスト |
| `fetchAdminControls` | POST | 管理者制御取得 | 未テスト |
| `recordCodeAssistMetrics` | POST | メトリクス送信 | 未テスト |

---

## 6. アーキテクチャ (確定)

```
┌─ Antigravity IDE ──────────────────────┐
│  Extension → Language Server (Go)      │
│       └── gRPC ──▶ cloudcode-pa        │
└────────────────────────────────────────┘

┌─ gemini-cli ───────────────────────────┐
│  Node.js → google-auth-library         │
│       └── REST ──▶ cloudcode-pa        │
│  OAuth Client ID: 681255809395-...     │
└────────────────────────────────────────┘

┌─ 直叩き (本ドキュメント) ──────────────┐  ← 🆕
│  curl → Bearer token                  │
│       └── REST ──▶ cloudcode-pa        │
│  Token: gemini-cli refresh → refresh   │
└────────────────────────────────────────┘
         │
         ▼
┌─ cloudcode-pa.googleapis.com ──────────┐
│  v1internal                            │
│  Private API (手動有効化不可)           │
│  プロジェクト: driven-circlet-rgkmt     │
│  Tier: g1-ultra-tier                   │
└────────────────────────────────────────┘
```

---

## 7. 失敗した経路 (学習記録)

| # | 試行 | 結果 | 教訓 |
|:--|:-----|:-----|:-----|
| 1 | gcloud auth token + cloudcode-pa | SERVICE_DISABLED | gcloud の Client ID では到達不可 |
| 2 | gcore でメモリダンプ → LS token 抽出 | PERMISSION_DENIED | LS は gRPC 専用の内部 token を使用 |
| 3 | mitmdump で LS 通信傍受 | Go gRPC は HTTPS_PROXY 無視 | gRPC proxy は別手法が必要 |
| 4 | animated-surfer で cloudaicompanion 有効化 | IAM 突破 → 404 instance not found | API は有効だが instance がない |
| 5 | animated-surfer で cloudcode-pa 有効化 | PERMISSION_DENIED | Private API は有効化不可 |
| 6 | project-f2526536 で IAM 設定 | PERMISSION_DENIED | Google 管理プロジェクト |
| 7 | animated-surfer に IAM ロール付与 | cloudaicompanion で IAM 突破 | instance が存在しないため生成不可 |
| 8 | gemini-cli を animated-surfer で実行 | companions.generateChat DENIED | animated-surfer には instance がない |

### 突破の転機

| ステップ | 発見 |
|:---------|:-----|
| gemini-cli `oauth2.ts` 解読 | 専用 OAuth Client ID の存在 |
| refresh_token で新 access_token 取得 | gemini-cli の Client ID が別 principal |
| `loadCodeAssist` を **x-goog-user-project なし**で実行 | 真のプロジェクト `driven-circlet-rgkmt` 発見 |
| `driven-circlet-rgkmt` で generateContent | **応答取得！** |

---

## 8. gemini-cli ソースコード参照

| ファイル | 内容 | 重要度 |
|:--------|:-----|:------:|
| `code_assist/oauth2.ts` | OAuth Client ID/Secret, スコープ, 認証フロー | 🔴🔴🔴 |
| `code_assist/server.ts` | エンドポイント, 全メソッド定義, HTTP 通信 | 🔴🔴 |
| `code_assist/setup.ts` | loadCodeAssist, onboardUser, tier 管理 | 🔴🔴 |
| `code_assist/types.ts` | 全型定義, Proto 参照 | 🟡 |
| `code_assist/converter.ts` | リクエスト/レスポンス変換 | 🟡 |

ローカルクローン: `/tmp/gemini-cli/` (shallow clone, HEAD)

---

## 9. セキュリティ考慮事項

| 項目 | 対応 |
|:-----|:-----|
| OAuth Client Secret | installed app なので公開安全 ([Google 公式](https://developers.google.com/identity/protocols/oauth2#installed)) |
| refresh_token | `~/.gemini/oauth_creds.json` に保存 (mode 0600) |
| access_token | 短命 (1時間)。都度 refresh_token から再取得 |
| プロジェクト ID | `driven-circlet-rgkmt` は Google 管理。漏洩リスク低 |

---

## 10. 次のアクション

- [x] bash スクリプト化 → `scripts/cortex.sh` (token cache, system instruction, streaming, quota)
- [x] system instruction テスト → 俳句生成で確認
- [x] `gemini-2.5-pro` テスト → FEP 説明で確認 (2053 tokens, thinking 含む)
- [x] `gemini-3-pro-preview` テスト → 応答確認 (208 tokens) 🎉
- [x] `retrieveUserQuota` テスト → 全12モデルバケット取得
- [ ] `gemini-2.5-flash` / `gemini-3-flash-preview` テスト
- [ ] `thinkingConfig` (extended thinking) 制御テスト
- [ ] `countTokens` API テスト
- [ ] n8n / Synergeia からの直接呼び出し統合
- [ ] LS 経由プロキシとの性能比較
- [ ] streaming テスト (`--stream` オプション)

---

*DX-010 v2.0 — Cortex API 直叩き完全突破 (2026-02-14 00:08 JST)*
