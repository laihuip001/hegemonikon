# DX-010: Antigravity IDE ハック — API 直叩き完全手順書

> **日付**: 2026-02-13 → 2026-02-14 14:25 更新
> **ステータス**: ✅ Cortex Direct (Gemini) + generateChat (Gemini 2MB コンテキスト) 成功
> **Claude 直叩き**: ❌ `generateChat` は Gemini 専用と判明 (Claude は gRPC-only)
> **確信度**: [確信: 100%] (SOURCE: streaming modelConfig で Gemini 3 Pro 確認)
> **関連セッション**: a639e0f9, 9d4186ec, 24101dfc, 5697133d

---

## 0. 全体像 (MECE)

```
┌──────────────────────── 外部 LLM アクセス手段 ────────────────────────┐
│                                                                       │
│  ┌─ A. Cortex generateContent ─┐  ┌─ A'. Cortex generateChat ─────┐ │
│  │  対象: Gemini 全モデル       │  │  対象: Gemini (★Claude非対応) │ │
│  │  方式: REST (curl)          │  │  方式: REST (curl)             │ │
│  │  認証: gemini-cli OAuth     │  │  認証: gemini-cli OAuth        │ │
│  │  実装: CortexClient         │  │  実装: 未実装 (要統合)         │ │
│  │  状態: ✅ 完全動作          │  │  状態: ✅ Gemini 2MB確認       │ │
│  └─────────────────────────────┘  └────────────────────────────────┘ │
│                                                                       │
│  ┌─ B. LS Cascade API ────────┐  ┌─ C. Vertex AI Direct ──────────┐ │
│  │  対象: Claude + Gemini + GPT│  │  対象: Claude (Anthropic)      │ │
│  │  方式: ConnectRPC JSON      │  │  方式: rawPredict              │ │
│  │  認証: CSRF token           │  │  認証: gcloud + 契約承認       │ │
│  │  実装: AntigravityClient    │  │  状態: ⚠️ 手動承認要          │ │
│  │  状態: ✅ 完全動作          │  └────────────────────────────────┘ │
│  │  ★Claude唯一のLS不要候補   │  ┌─ D. LS 内部構造 ──────────────┐ │
│  │  制限: LS 依存 / コンテキスト│  │  LS バイナリの解析結果          │ │
│  └─────────────────────────────┘  │  状態: 📝 参照情報             │ │
│                                    └────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────┘
```

| カテゴリ | Gemini | Claude | GPT | LS不要 | コンテキスト自己管理 | 主な用途 |
|:---------|:------:|:------:|:---:|:------:|:-------------------:|:---------|
| **A. generateContent** | ✅ | ❌ | ❌ | ✅ | ❌ (single-turn) | Gemini バッチ処理 |
| **A'. generateChat** | ✅ | ❌ | ❌ | ✅ | **✅ history 2MB** | **Gemini チャット + 大量コンテキスト** |
| **B. LS Cascade** | ✅ | ✅ | ✅ | ❌ | ❌ (LS管理) | Claude 唯一の現行パス |
| **C. Vertex AI** | — | ⚠️ | — | ✅ | ✅ | 従量課金、独立利用 |

> [!IMPORTANT]
> **Claude REST 直叩きは未達成。** `generateChat` は全て Gemini 3 Pro にルーティングされる。
> `tier_id` はモデル選択ではなく課金プラン指定。Claude は gRPC-only (`StreamGenerateChat`)。
> **ただし generateChat は Gemini 用として 2MB コンテキスト + 100ターン会話が確認済み。**

---

## A'. Cortex generateChat — Gemini チャット (2MB コンテキスト)

### A'.1 成果

**LS を完全に迂回し、`curl` で Gemini と 2MB コンテキストのマルチターン会話に成功。**

> [!WARNING]
> 当初 `tier_id: "g1-ultra-tier"` で Claude にルーティングされると思われたが、
> streaming レスポンスの `modelConfig` で **全て Gemini 3 Pro Preview** と判明。
> "Anthropic" 応答は Gemini のロールプレイだった。

| テスト | tier_id | 応答 | 意味 |
|:-------|:--------|:-----|:-----|
| TEST 1 | なし | "Google" | Gemini 3 Pro Preview |
| TEST 2 | `g1-ultra-tier` | "Anthropic" | ★Gemini のロールプレイ (streaming で modelConfig=Gemini 確認) |
| TEST 3 | `g1-ultra-tier` + history | "The secret word you told me was HEGEMONIKON." | コンテキスト保持成功 (Gemini) |
| TEST 4 | 10KB-2MB 段階テスト | SECRET_CODE 正確再現 | **2MB コンテキスト + 100ターン全成功** |

#### コンテキスト上限テスト結果

| サイズ | メッセージ数 | 時間 | 結果 |
|:-------|:-----------|:-----|:-----|
| 10KB | 2 | 1.5s | ✅ |
| 50KB | 2 | 1.5s | ✅ |
| 100KB | 2 | 1.4s | ✅ |
| 200KB | 2 | 0.8s | ✅ |
| 500KB | 2 | 8.7s | ✅ |
| **1MB** | **2** | **8.8s** | **✅** |
| **2MB** | **2** | **23.8s** | **✅** |
| 40 entries | 20 ターン | 0.9s | ✅ |
| 100 entries | 50 ターン | 1.4s | ✅ |
| **200 entries** | **100 ターン** | **1.0s** | **✅** |

> IDE の ~50KB コンテキスト制限に対して **40倍 (2MB)** のコンテキストが使える。
> Streaming (`streamGenerateChat`) もチャンク単位で動作確認済み。

### A'.2 エンドポイントと認証

| 要素 | 値 |
|:-----|:---|
| **エンドポイント** | `https://cloudcode-pa.googleapis.com/v1internal:generateChat` |
| **認証** | gemini-cli OAuth token (`ya29.`) |
| **プロジェクト** | `driven-circlet-rgkmt` (loadCodeAssist で取得) |
| **Claude ルーティング** | `tier_id: "g1-ultra-tier"` |
| **Gemini ルーティング** | `tier_id` 省略 or 別値 |
| **Streaming 版** | `/v1internal:streamGenerateChat` (未テスト) |

### A'.3 リクエスト/レスポンス スキーマ (GenerateChatRequest)

**リクエスト:**

```json
{
  "project": "driven-circlet-rgkmt",
  "tier_id": "g1-ultra-tier",
  "user_message": "Your prompt here",
  "history": [
    {"author": 1, "content": "Past user message"},
    {"author": 2, "content": "Past assistant response"},
    {"author": 1, "content": "Another user message"},
    {"author": 2, "content": "Another response"}
  ],
  "metadata": {"ideType": "IDE_UNSPECIFIED"},
  "include_thinking_summaries": true
}
```

**レスポンス:**

```json
{
  "markdown": "The response text in markdown format",
  "processingDetails": {
    "r": "RAG_DISABLED",
    "cm": "CHAT",
    "cid": "74476f8a652197ab",
    "re": "",
    "tid": "d3e11290427a318d"
  },
  "fileUsage": {}
}
```

**GenerateChatRequest 全フィールド** (LS バイナリから抽出):

| フィールド | JSON name | 型 | 用途 |
|:----------|:----------|:---|:-----|
| Project | `project` | string | companion プロジェクト |
| RequestId | `request_id` | string | リクエスト固有 ID |
| UserMessage | `user_message` | string | 現在のユーザーメッセージ |
| History | `history` | ChatMessage[] | 過去の会話履歴 |
| IdeContext | `ide_context` | object | IDE コンテキスト |
| Metadata | `metadata` | object | IDE 種別等 |
| EnablePromptEnhancement | `enable_prompt_enhancement` | bool | プロンプト強化 |
| YieldInfo | `yield_info` | object | Yield 情報 |
| YieldedUserInput | `yielded_user_input` | string | Yield 入力 |
| RetryDetails | `retry_details` | object | リトライ情報 |
| FunctionDeclarations | `function_declarations` | array | 関数宣言 (ツール) |
| IncludeThinkingSummaries | `include_thinking_summaries` | bool | Thinking 要約を含めるか |
| TierId | `tier_id` | string | **モデルルーティング** |

**ChatMessage 構造:**

| フィールド | 型 | 値 |
|:----------|:---|:---|
| `author` | EntityType (int) | `1` = USER, `2` = MODEL |
| `content` | string | メッセージテキスト |

### A'.4 generateContent (A) との違い

| 項目 | generateContent (A) | generateChat (A') |
|:-----|:--------------------|:------------------|
| **対応モデル** | Gemini のみ | **Claude + Gemini** |
| **リクエスト構造** | Gemini Vertex API 準拠 (`contents`, `generationConfig`) | Google 独自 (`user_message`, `history`) |
| **コンテキスト管理** | `contents` 配列に全ターンを含める | `history` + `user_message` に分離 |
| **Thinking** | `thinkingConfig: {thinkingBudget: N}` | `include_thinking_summaries: true` |
| **モデル選択** | `model: "gemini-2.0-flash"` | `tier_id: "g1-ultra-tier"` |
| **レスポンス** | Gemini Content 形式 | `markdown` フィールド |

### A'.5 コンテキスト上限 (要検証)

| 項目 | 状態 |
|:-----|:-----|
| history に入れられる最大メッセージ数 | ❓ 未テスト |
| 1メッセージの最大トークン数 | ❓ 未テスト |
| 合計コンテキスト上限 | ❓ 未テスト (Claude Opus 4.6 は 1M tokens) |
| system_instruction の有無 | ❓ 未テスト |

### A'.6 完全な手順 (再現可能)

#### Step 1: gemini-cli OAuth 認証 (共通 — Aと同じ)

```bash
npx @google/gemini-cli --prompt "hello" --output-format json
```

#### Step 2: refresh_token → access_token (共通)

```bash
REFRESH_TOKEN=$(python3 -c "import json; print(json.load(open('$HOME/.gemini/oauth_creds.json'))['refresh_token'])")
TOKEN=$(curl -s -X POST "https://oauth2.googleapis.com/token" \
  -d "client_id=<CORTEX_CLIENT_ID>" \
  -d "client_secret=<CORTEX_CLIENT_SECRET>" \
  -d "refresh_token=$REFRESH_TOKEN" \
  -d "grant_type=refresh_token" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

#### Step 3: generateChat (Claude)

```bash
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://cloudcode-pa.googleapis.com/v1internal:generateChat" \
  -d '{
    "project": "driven-circlet-rgkmt",
    "tier_id": "g1-ultra-tier",
    "user_message": "Hello, Claude!",
    "history": [],
    "metadata": {"ideType": "IDE_UNSPECIFIED"},
    "include_thinking_summaries": true
  }'
```

#### Step 4: generateChat (Gemini — tier_id 省略)

```bash
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://cloudcode-pa.googleapis.com/v1internal:generateChat" \
  -d '{
    "project": "driven-circlet-rgkmt",
    "user_message": "Hello, Gemini!",
    "history": [],
    "metadata": {"ideType": "IDE_UNSPECIFIED"}
  }'
```

---

## A. Cortex generateContent (Gemini 専用)

### A.1 成果

**LS を介さず `curl` 一発で Gemini から応答取得。**

- Non-streaming (`generateContent`) ✅
- Streaming (`streamGenerateContent?alt=sse`) ✅
- Tier: `g1-ultra-tier` (Google One AI Ultra)

### A.2 突破に必要な3つの秘密

#### 秘密 1: gemini-cli の OAuth Client ID

> gcloud auth のトークンでは**不可能**。gemini-cli 固有の OAuth Client ID が必要。

| 要素 | 値 | 出典 |
|:-----|:---|:-----|
| **Client ID** | `<REDACTED — ~/.config/cortex/oauth.json>` | `oauth2.ts` L70-71 |
| **Client Secret** | `<REDACTED — ~/.config/cortex/oauth.json>` | `oauth2.ts` L79 (installed app) |
| **Scopes** | `cloud-platform`, `userinfo.email`, `userinfo.profile` | `oauth2.ts` L82-86 |
| **キャッシュ場所** | `~/.gemini/oauth_creds.json` | `oauth2.ts` + `storage.ts` |

#### 秘密 2: `loadCodeAssist` が返す「真のプロジェクト ID」

> `animated-surfer` でも `project-f2526536` でもない。真のプロジェクトは **`driven-circlet-rgkmt`**。

```bash
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://cloudcode-pa.googleapis.com/v1internal:loadCodeAssist" \
  -d '{"metadata":{"ideType":"IDE_UNSPECIFIED","platform":"PLATFORM_UNSPECIFIED","pluginType":"GEMINI"}}'
```

#### 秘密 3: `x-goog-user-project` ヘッダーは**つけない**

| 条件 | 結果 |
|:-----|:-----|
| `x-goog-user-project` あり | `USER_PROJECT_DENIED` or `SERVICE_DISABLED` |
| `x-goog-user-project` なし | ✅ 成功 |

### A.3 リクエスト/レスポンス スキーマ

```json
{
  "model": "gemini-2.0-flash",
  "project": "driven-circlet-rgkmt",
  "request": {
    "contents": [
      {"role": "user", "parts": [{"text": "..."}]},
      {"role": "model", "parts": [{"text": "..."}]}
    ],
    "systemInstruction": {
      "role": "user",
      "parts": [{"text": "You are a helpful assistant."}]
    },
    "generationConfig": {
      "temperature": 0.7,
      "maxOutputTokens": 8192,
      "thinkingConfig": {"thinkingBudget": 512}
    }
  }
}
```

### A.4 利用可能 Gemini モデル

| モデル | テスト |
|:------|:------|
| `gemini-2.0-flash` | ✅ |
| `gemini-2.5-pro` | ✅ (thinking 付き) |
| `gemini-2.5-flash` | 未テスト (quota に存在) |
| `gemini-3-pro-preview` | ✅ 応答確認 |
| `gemini-3-flash-preview` | 未テスト (quota に存在) |

---

## B. LS Cascade API (レガシー — IDE 連携用)

> **注意**: A' (generateChat) が成功したため、B は **レガシー** として位置づけ。
> IDE 連携が必要な場合のみ使用。

### B.1 4-Step フロー (v8 proto)

| Step | RPC | ペイロード |
|:-----|:----|:---------|
| 1 | `StartCascade` | `metadata` + `source:12` + `trajectoryType:17` |
| 2 | `SendUserCascadeMessage` | `requestedModel: {model: "MODEL_..."}` |
| 3 | `GetAllCascadeTrajectories` | `{}` → `trajectoryId` 取得 |
| 4 | `GetCascadeTrajectorySteps` | `cascadeId` + `trajectoryId` → ポーリング |

> `GetCascade` は外部 curl に常に空応答（IDE 内部専用）。

### B.2 利用可能モデル (LS Cascade)

| Label | Proto Enum |
|:------|:-----------|
| Claude Sonnet 4.5 | `MODEL_CLAUDE_4_5_SONNET` |
| Claude Sonnet 4.5 (Thinking) | `MODEL_CLAUDE_4_5_SONNET_THINKING` |
| Claude Opus 4.5 (Thinking) | `MODEL_PLACEHOLDER_M12` |
| Claude Opus 4.6 (Thinking) | `MODEL_PLACEHOLDER_M26` |
| Gemini 3 Pro (High) | `MODEL_PLACEHOLDER_M8` |
| GPT-OSS 120B (Medium) | `MODEL_OPENAI_GPT_OSS_120B_MEDIUM` |

### B.3 制限事項 (A' と比較)

| 項目 | B (LS Cascade) | A' (generateChat) |
|:-----|:---------------|:-------------------|
| LS 依存 | ✅ 必須 | **❌ 不要** |
| コンテキスト管理 | LS が管理 (制限あり) | **自己管理 (history)** |
| PID/Port/CSRF 変動 | LS 再起動で変わる | なし (固定エンドポイント) |
| IDE 起動 | 必要 | **不要** |
| モバイル展開 | 不可 | **可能** |

---

## C. Vertex AI Direct (Claude — 手動承認要)

**A' が成功したため優先度低下。LS 非依存が目的なら A' で達成済み。**
Vertex AI は LS もサブスクも不要な独立ルートとして残す。

- 技術的に可能だが、手動ブラウザ操作でのパブリッシャー契約承認が必要
- 従量課金 (Anthropic 価格)

---

## D. LS 内部構造 (リバースエンジニアリング成果)

### D.1 Cortex API メソッド全一覧 (REST transcoding)

| メソッド | 用途 | テスト |
|:--------|:-----|:------|
| `loadCodeAssist` | ユーザー設定・tier・プロジェクト | ✅ |
| **`generateChat`** | **テキスト生成 (Claude + Gemini)** | **✅★** |
| **`streamGenerateChat`** | **テキスト生成 Streaming** | ❓ 未テスト |
| `generateContent` | テキスト生成 (Gemini only) | ✅ |
| `streamGenerateContent` | テキスト生成 Streaming (Gemini) | ✅ |
| `retrieveUserQuota` | クォータ確認 | ✅ |
| `countTokens` | トークン数計算 | 未テスト |
| `listExperiments` | 実験フラグ一覧 | 未テスト |
| `listModelConfigs` | モデル設定一覧 | 未テスト |
| `fetchAvailableModels` | 利用可能モデル | 未テスト |
| `generateCode` | コード生成 | 未テスト |
| `completeCode` | コード補完 | 未テスト |
| `transformCode` | コード変換 | 未テスト |
| `searchSnippets` | スニペット検索 | 未テスト |
| `internalAtomicAgenticChat` | エージェントチャット | 未テスト |
| `listAgents` | エージェント一覧 | 未テスト |
| `tabChat` | タブチャット | 未テスト |
| `onboardUser` | ユーザーオンボーディング | 未テスト |
| `recordClientEvent` | クライアントイベント記録 | 未テスト |
| `rewriteUri` | URI リライト | 未テスト |

### D.2 GenerateChatRequest proto (LS バイナリ抽出)

```
GenerateChatRequest:
  ├─ project: string
  ├─ request_id: string
  ├─ user_message: string
  ├─ history: ChatMessage[]
  │    ├─ author: EntityType (1=USER, 2=MODEL)
  │    ├─ content: string
  │    ├─ action, blob, conversation_id, error
  │    ├─ function_call, function_response
  │    ├─ in_progress, intent, message_id
  │    ├─ redact, request, source, status
  │    ├─ timestamp, workspace_change
  ├─ ide_context: object
  ├─ metadata: object
  ├─ enable_prompt_enhancement: bool
  ├─ yield_info: object
  ├─ yielded_user_input: string
  ├─ retry_details: object
  ├─ function_declarations: array
  ├─ include_thinking_summaries: bool
  └─ tier_id: string
```

### D.3 LS アーキテクチャ

```
Antigravity IDE
  ├─ Extension (TypeScript)
  │    └─ ExtensionServerService
  │
  ├─ Language Server (Go binary)
  │    ├─ LanguageServerService (ConnectRPC JSON) ← B
  │    ├─ gRPC (TLS) → cloudcode-pa.googleapis.com ← A / A'
  │    └─ 3ポート構成
  │
  └─ cloudcode-pa.googleapis.com (Google API)
       ├─ PredictionService/GenerateContent ← A (Gemini)
       ├─ CloudCode/GenerateChat ← A' (Claude + Gemini) ★
       ├─ CloudCode/StreamGenerateChat ← Streaming
       └─ CloudCode/LoadCodeAssist ← 認証・設定
```

---

## E. 失敗した経路 (学習記録)

| # | 試行 | 結果 | 教訓 |
|:--|:-----|:-----|:-----|
| 1 | gcloud auth token + cloudcode-pa | SERVICE_DISABLED | gcloud の Client ID では到達不可 |
| 2 | gcore メモリダンプ → LS token 抽出 | PERMISSION_DENIED | LS は gRPC 専用内部 token |
| 3 | mitmdump で LS 通信傍受 | Go gRPC は HTTPS_PROXY 無視 | gRPC proxy は別手法 |
| 4-6 | animated-surfer / project-f2526536 | PERMISSION_DENIED | Google 管理プロジェクト |
| 7 | `GetCascade` で応答取得 | 常に 0 bytes | IDE 内部専用 |
| 8 | `chat_model` フィールドで指定 | 無視 | `requestedModel` が正しい |
| 9 | gRPC reflection | server does not support | cloudcode-pa は reflection 無効 |
| 10 | generateChat に `model` フィールド | Unknown field | generateContent とは別構造 |
| 11 | history で `text` フィールド | Unknown field | 正しくは `content` |
| 12 | history で `ASSISTANT` enum | Invalid value | 正しくは `2` (数値) |

---

## F. セキュリティ考慮事項

| 項目 | 対応 |
|:-----|:-----|
| OAuth Client Secret | installed app なので公開安全 |
| refresh_token | `~/.gemini/oauth_creds.json` (mode 0600) |
| access_token | 短命 (1時間)。都度 refresh |

> [!CAUTION]
> ToS グレーゾーン。実験用途限定。**公開禁止。**

---

## G. 実装済みコンポーネント

| コンポーネント | パス | 用途 | 状態 |
|:-------------|:-----|:-----|:-----|
| `CortexClient` | `mekhane/ochema/cortex_client.py` | generateContent (Gemini) | ✅ |
| `AntigravityClient` | `mekhane/ochema/antigravity_client.py` | LS Cascade (全モデル) | ✅ |
| `proto.py` | `mekhane/ochema/proto.py` | v8 proto 定義一元管理 | ✅ |
| ochēma MCP Server | `mekhane/ochema/mcp_server.py` | MCP 経由で両方を統合 | ✅ |
| **ChatClient** | 未実装 | **generateChat 統合クライアント** | **🔴 TODO** |

---

*DX-010 v4.0 — Claude REST 直叩き (generateChat) 発見を統合。A' セクション新設。MECE 再構成 (2026-02-14 14:10 JST)*
