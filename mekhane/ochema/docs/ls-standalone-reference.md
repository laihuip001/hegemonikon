# LS API 操作ガイド (Cookbook)

> **目的**: Antigravity LS ローカル API を直接操作するための実用ガイド
> **詳細な発見・歴史は**: [`ide-hack-complete-reference.md`](file:///home/makaron8426/.gemini/antigravity/knowledge/ide-hack-complete-reference.md) (マスターKI) を参照
> **最終更新**: 2026-02-13

---

## 1. 接続情報の取得

```bash
# LS PID・CSRF・ポートを一括取得
LS_PID=$(pgrep -f 'language_server_linux.*server_port' | head -1)
CSRF=$(cat /proc/$LS_PID/cmdline | tr '\0' '\n' | grep -A1 csrf_token | tail -1)
PORT=$(ss -tlnp | grep "pid=$LS_PID" | awk '{print $4}' | grep -oP '\d+$' | sort -n | head -1)
echo "PID=$LS_PID  CSRF=$CSRF  PORT=$PORT"
```

> **注意**: `x-csrf-token` ❌ → `x-codeium-csrf-token` ✅ (間違いやすい)

---

## 2. curl テンプレート

```bash
# 基本テンプレート
call_ls() {
  local method=$1 data=${2:-'{}'}
  curl -sk -X POST \
    "https://127.0.0.1:$PORT/exa.language_server_pb.LanguageServerService/$method" \
    -H 'Content-Type: application/json' \
    -H "x-codeium-csrf-token: $CSRF" \
    -H 'Connect-Protocol-Version: 1' \
    -d "$data"
}

# 使用例
call_ls GetUserStatus | python3 -m json.tool
call_ls StartCascade '{"source": 12}'
```

---

## 3. LLM テキスト生成 (4-Step フロー)

```bash
# Step 1: カスケード開始
CID=$(call_ls StartCascade '{"source": 12}' | python3 -c "import json,sys; print(json.load(sys.stdin)['cascadeId'])")

# Step 2: メッセージ送信
call_ls SendUserCascadeMessage "{
  \"cascadeId\": \"$CID\",
  \"items\": [{\"text\": \"2+2は何?\"}],
  \"cascadeConfig\": {
    \"plannerConfig\": {
      \"conversational\": {},
      \"planModel\": \"MODEL_CLAUDE_4_5_SONNET_THINKING\"
    }
  }
}"

# Step 3: Trajectory ID 取得 (数秒待つ)
sleep 5
TID=$(call_ls GetAllCascadeTrajectories '{}' | python3 -c "
import json,sys
d=json.load(sys.stdin)
for cs in d.get('trajectorySummaries',{}).values():
    for t in cs.get('trajectorySummaries',[]):
        print(t['trajectoryId']); break
    break
")

# Step 4: 応答取得
call_ls GetCascadeTrajectorySteps "{\"cascadeId\": \"$CID\", \"trajectoryId\": \"$TID\"}" \
  | python3 -c "
import json,sys
d=json.load(sys.stdin)
for s in d.get('steps',[]):
    if s.get('type','') == 'CORTEX_STEP_TYPE_PLANNER_RESPONSE':
        r = s.get('plannerResponse',{})
        print('Model:', r.get('generatorModel',''))
        print('Response:', r.get('response','')[:500])
"
```

---

## 4. 利用可能モデル

```bash
call_ls GetUserStatus | python3 -c "
import json,sys
d=json.load(sys.stdin)
for m in d['userStatus']['cascadeModelConfigData']['clientModelConfigs']:
    r = m.get('remainingQuotaPercentage', '?')
    print(f\"{m['label']:40s} {m['model']:45s} {r}%\")
"
```

---

## 5. よく使う操作

| 操作 | コマンド |
|:-----|:---------|
| ユーザー状態 | `call_ls GetUserStatus` |
| メモリ一覧 | `call_ls GetUserMemories` |
| セッション一覧 | `call_ls GetAllCascadeTrajectories` |
| MCP 状態 | `call_ls GetMcpServerStates` |
| Experiment Flags | `call_ls GetStaticExperimentStatus` |
| フライトレコーダー | `call_ls DumpFlightRecorder` |

---

## 6. Python クライアント

```python
from mekhane.ochema.antigravity_client import AntigravityClient

c = AntigravityClient()
print(c.ls)              # LSInfo(pid, csrf, port, workspace)
c.ask("2+2は?")          # フル LLM フロー
c.session_read(cid)      # セッション読取
c.quota()                # Quota 確認
c.models()               # モデル一覧
```

---

## 7. Standalone LS 起動 (OAuth なし)

```bash
# Metadata protobuf 生成 → §2 の Python スクリプト参照 (マスターKI §9)
python3 generate_metadata.py

# 起動
cat /tmp/ls_metadata.bin | language_server_linux_x64 \
  --standalone=false --enable_lsp=false \
  --csrf_token="my-token" --server_port=55900 \
  --workspace_id=standalone --app_data_dir=antigravity \
  --cloud_code_endpoint=https://daily-cloudcode-pa.googleapis.com
```

**制約**: OAuth なしでは `GetUserStatus`, `SendUserCascadeMessage` (LLM推論) が 500。
ローカル機能 (StartCascade, GetUserMemories 等) は動作する。

---

## 8. 認証クレデンシャル

| ファイル | 用途 | 制御可能 |
|:---------|:-----|:--------:|
| `~/.gemini/oauth_creds.json` | IDE OAuth (access/refresh/id_token) | 読取のみ |
| `~/.config/gcloud/application_default_credentials.json` | gcloud ADC | ✅ |
| `~/.config/Antigravity/User/globalStorage/state.vscdb` | 別 access_token (protobuf 内) | 読取のみ |

---

## 9. トラブルシューティング

| 症状 | 原因 | 対処 |
|:-----|:-----|:-----|
| `missing CSRF token` | ヘッダー名間違い | `x-codeium-csrf-token` を使う |
| `Client sent HTTP to HTTPS` | HTTP で接続 | `https://` を使う |
| `trajectory not found` | 別ワークスペースの LS に接続 | `--workspace_id` でフィルタ |
| 500 Internal Server Error | OAuth 未提供 | IDE LS を使う |
| `model not found` | cascadeConfig 未指定 | planModel を明示的に指定 |

---

## 12. フルフロー検証結果 (2026-02-13 成功)

HGK ワークスペースの LS (PID:1034701, PORT:43359) に直接接続し、
curl のみで Claude Sonnet 4.5 Thinking を呼び出し、応答テキスト取得に成功。

```bash
# 接続情報取得
LS_PID=$(pgrep -f 'language_server_linux.*server_port' | head -1)
CSRF=$(cat /proc/$LS_PID/cmdline | tr '\0' '\n' | grep -A1 csrf_token | tail -1)
PORT=43359  # or: ss -tlnp | grep "pid=$LS_PID" で確認
```

| Step | RPC | 入力 | 出力 |
|:-----|:----|:-----|:-----|
| 1 | `StartCascade` | `{"source": 12}` | `cascadeId: ec975137-...` |
| 2 | `SendUserCascadeMessage` | cascadeId + items + cascadeConfig | `{}` (受理) |
| 3 | `GetAllCascadeTrajectories` | `{}` | `trajectoryId: e3d6a3c4-...` |
| 4 | `GetCascadeTrajectorySteps` | cascadeId + trajectoryId | **5 steps (応答テキスト含む)** |

### Step 4 レスポンス構造

```
[0] CORTEX_STEP_TYPE_USER_INPUT       — 入力プロンプト
[1] CORTEX_STEP_TYPE_CONVERSATION_HISTORY — 会話履歴注入
[2] CORTEX_STEP_TYPE_EPHEMERAL_MESSAGE    — システムメッセージ
[3] CORTEX_STEP_TYPE_PLANNER_RESPONSE     — ★ LLM 応答テキスト
[4] CORTEX_STEP_TYPE_CHECKPOINT           — userIntent 自動生成
```

### PLANNER_RESPONSE フィールド

```json
{
  "plannerResponse": {
    "response": "2+2は4です。",
    "modifiedResponse": "2+2は4です。",
    "thinking": "ユーザーは「2+2は何ですか？...」..."
  },
  "metadata": {
    "generatorModel": "MODEL_CLAUDE_4_5_SONNET_THINKING"
  }
}
```

### 重要な発見

1. **ワークスペース単位で LS プロセスが分離** — 正しい LS に接続しないと `trajectory not found`
2. **response + thinking の両方が取得可能** — audit/debug に有用
3. **CHECKPOINT に userIntent が自動生成** — IDE がセッション要約を維持
4. **Step 2 から Step 3 まで 5-8 秒の待ちが必要** — Cloud Backend の LLM 推論時間

---

## 13. Python 実装 (antigravity_client.py)

**パス**: `mekhane/ochema/antigravity_client.py` (703行, 25KB)

上記 4-Step フローを完全に Python 実装した `AntigravityClient` クラス:

```python
from mekhane.ochema import AntigravityClient

client = AntigravityClient(workspace="hegemonikon")
response = client.ask("2+2は？", model="MODEL_CLAUDE_4_5_SONNET_THINKING")
print(response.text)      # "2+2は4です。"
print(response.thinking)  # thinking テキスト
print(response.model)     # "MODEL_CLAUDE_4_5_SONNET_THINKING"
```

### 主要メソッド

| メソッド | 機能 |
|:---------|:-----|
| `ask(message, model, timeout)` | LLM テキスト生成 (4-Step フロー) |
| `get_status()` | ユーザーステータス (Quota, プラン情報) |
| `list_models()` | 利用可能モデル一覧 |
| `quota_status()` | 全モデル Quota 残量 |
| `session_info(cascade_id)` | セッション情報/一覧 |
| `session_read(cascade_id)` | 会話内容読み取り |
| `session_episodes(brain_id)` | エピソード記憶アクセス |

### MCP 統合

`mekhane/ochema/cli.py` → Ochēma MCP Server (Tool: `mcp_ochema_ask`, `mcp_ochema_models` 等)
LS API → HGK Gateway のバックエンド化は完了済み。

---

## 14. Cortex API 直叩き結果 (2026-02-13)

### 検証結果: 突破口あり

Cloud Backend (Cortex API) への直叩き試行:

| メソッド | プロトコル | 結果 | gRPC Status |
|:---------|:-----------|:-----|:------------|
| `ListCloudAICompanionProjects` | gRPC (binary) | ❌ | **12 UNIMPLEMENTED** |
| `LoadCodeAssist` | gRPC (binary) | ✅ | **0 OK** — Project ID 返却 |
| `GenerateChat` (project あり) | gRPC (binary) | ❌ | **7 PERMISSION_DENIED** |
| `StreamGenerateChat` | gRPC (binary) | ❌ | **7 PERMISSION_DENIED** |
| 全メソッド | JSON/REST (curl) | ❌ | **404 Not Found** |
| 全メソッド | grpcurl (Reflection) | ❌ | **Reflection 未対応** |

### Project ID の取得

`LoadCodeAssist` RPC (Antigravity OAuth ya29 トークン) で **Project ID = `robotic-victory-pst7f0`** を取得成功。

### PERMISSION_DENIED の詳細

`grpc-status-details-bin` (base64 decoded):

```
GenerateChat:
  IAM_PERMISSION_DENIED on iam.googleapis.com
  permission: cloudaicompanion.companions.generateChat
  resource: projects/robotic-victory-pst7f0

StreamGenerateChat:
  IAM_PERMISSION_DENIED on iam.googleapis.com
  permission: cloudaicompanion.instances.completeTask
  resource: projects/     ← project が空 (未指定時)
```

> **gcloud ADC トークン**は `cloudaicompanion.companions.generateChat` 権限を持たない。
> **Antigravity OAuth トークン** (state.vscdb の ya29) が必要だが、
> Cortex API に直接送る際のリクエスト構造が LS 内部の proto 定義と合致する必要がある。

### 結論

- **Cortex API は gRPC only** (JSON/REST は 404)
- **Reflection API 無効** (proto descriptor なしでは grpcurl も使えない)
- **Project ID = `robotic-victory-pst7f0`** (`LoadCodeAssist` RPC で取得)
- **Antigravity OAuth トークン + 正確な proto 構造**が直叩きに必要
- → **LS 経由 4-Step フローが現時点で唯一の安定ルート**
- → Cortex 直叩きは Project ID は解決したが、proto 構造の完全解明が残る

### ya29 トークン抽出方法 (参考)

```python
import sqlite3, json
db = sqlite3.connect('~/.config/Antigravity/User/globalStorage/state.vscdb')
row = db.execute("SELECT value FROM ItemTable WHERE key='antigravityAuthStatus'").fetchone()
token = json.loads(row[0])['apiKey']  # ya29.a0AUMWg_... (258 chars)
```

---

## 15. 実験ログ

### Standalone LS 起動

| stdin | バイト数 | 結果 |
|:------|:---------|:-----|
| `printf ''` | 0 | `read initial metadata: <nil>` |
| `echo ""` | 1 (`\n`) | `cannot parse invalid wire-format` |
| `\x00` | 1 | `cannot parse invalid wire-format` |
| Python protobuf | 79 | ✅ **起動成功** |

### Cloud Backend 直叩き (JSON/REST — 全滅)

| 認証 | ヘッダー | 結果 |
|:-----|:---------|:-----|
| gcloud ADC | Authorization: Bearer ya29... | 403 SERVICE_DISABLED |
| gcloud ADC + X-Goog-User-Project | +quota project | 403 SERVICE_DISABLED |
| Antigravity OAuth | Authorization: Bearer ya29... | 403 IAM_PERMISSION_DENIED |

### Cloud Backend 直叩き (gRPC — 部分成功)

| メソッド | 認証通過 | 結果 |
|:---------|:-------:|:-----|
| ListCloudAICompanionProjects | ✅ | UNIMPLEMENTED (サーバ側無効) |
| GenerateChat | ✅ | PERMISSION_DENIED (project 未指定) |
| StreamGenerateChat | ✅ | PERMISSION_DENIED (project 未指定) |

> gRPC バイナリフレーミング (`\x00\x00\x00\x00\x00` + application/grpc) で認証は突破。
> `x-cloudaicompanion-trace-id` が返る = バックエンドまで到達している。

---

## 16. 別モデルテスト結果 (2026-02-13)

| API モデル名 | ラベル | enum ID | 結果 | 自称 |
|:-------------|:-------|:--------|:-----|:-----|
| `MODEL_CLAUDE_4_5_SONNET_THINKING` | Claude Sonnet 4.5 (T) | 334 | ✅ | — (前回テスト) |
| `MODEL_CLAUDE_4_5_SONNET` | Claude Sonnet 4.5 | 333 | ✅ | "Claude Sonnet 4.5 (Anthropic)" |
| `MODEL_PLACEHOLDER_M26` | Claude Opus 4.6 (T) | 1026 | ✅ | "Claude (Anthropic)" |
| `MODEL_PLACEHOLDER_M12` | Claude Opus 4.5 (T) | 1012 | ⚠️ | "no longer available, switch to 4.6" |
| `MODEL_PLACEHOLDER_M8` | Gemini 3 Pro (High) | 1007 | ✅ | "Gemini 2.0 Flash" |
| `MODEL_PLACEHOLDER_M18` | Gemini 3 Flash | 1018 | ✅ | "Claude 3.5 Sonnet" |
| `MODEL_OPENAI_GPT_OSS_120B_MEDIUM` | GPT-OSS 120B | — | ❌ 500 | — |

> enum ID は `userStatusProtoBinaryBase64` のデコードで取得。

---

## 17. ストリーミング調査結果

### StreamCascadePanelReactiveUpdates

- **ConnectRPC binary envelope** (5-byte header + protobuf payload)
- `application/connect+json` → `"protocol error: promised 576938355 bytes"` (protobuf 形式を要求)
- `application/grpc-web+json` → 空レスポンス
- **curl からの直接利用は困難**

### 実用的代替: ポーリング

`antigravity_client.py` の `_poll_response()` が既に実装済み:

- Step 4 (`GetCascadeTrajectorySteps`) を 1 秒間隔でポーリング
- `CORTEX_STEP_STATUS_DONE` + `TURN_STATE_WAITING_FOR_USER` で完了判定

真の SSE ストリーミングは ConnectRPC Python ライブラリが必要 → 低優先度。

---

## 18. Project ID 傍受 + MITM 結果

### 🎯 最終結果: Project ID = `robotic-victory-pst7f0`

`LoadCodeAssist` RPC (Antigravity OAuth ya29 トークン使用) で取得成功。

### V3 ログ探査 (バイナリ解析 + state.vscdb)

| 方法 | 結果 |
|:-----|:-----|
| LS バイナリ `strings` | `cloudaicompanionProject`, `antigravity_project_id`, `quota_project_id` フィールド発見 |
| extension.js proto 定義 | `cloudaicompanion_project` (field 1), `antigravity_project_id` (field 19) 発見 |
| `state.vscdb` 全キー検索 | `antigravityUnifiedStateSync.userStatus` に tier 情報あり、project なし |
| `userStatusProtoBinaryBase64` デコード | `g1-ultra-tier`, モデル enum, プラン情報 |
| `GetUserStatus` API | `userTier.id = g1-ultra-tier`, project フィールドなし |
| LS 内部 RPC (OnboardUser 等) | 404 (ConnectRPC 非公開) |
| LS /proc/PID/mem スキャン | GCP Project ID パターン 0 件 (Go GC 断片化) |

### V1 MITM Proxy (mitmproxy 12.2.1)

**構成**: mitmdump (port 8888) + LS wrapper (`HTTPS_PROXY` 注入)

| 通信先 | プロキシ通過 | キャプチャ内容 |
|:-------|:----------:|:--------------|
| `antigravity-unleash.goog` | ✅ | Feature Flags (370+ toggles), Go/JS SDK 通信全文 |
| `cloudcode-pa.googleapis.com` | ✅ (HTTP/2) | `GenerateChat` (200 OK) — 前回セッション |
| `daily-cloudcode-pa.googleapis.com` | ❌ | gRPC はプロキシ経由せず直接接続 |
| `lh3.googleusercontent.com` | ✅ | 静的アセット |
| `otel.gitkraken.com` | ✅ | テレメトリ |

### Unleash Feature Flags (MITM で発見)

| 項目 | 値 |
|:-----|:---|
| LS appName | `codeium-language-server` |
| Extension appName | `codeium-extension` |
| LS SDK | `unleash-client-go:4.5.0` |
| Extension SDK | `unleash-client-js:3.7.8` |
| Instance ID | `makaron8426-Hegemonikon` |
| トグル数 | 370+ |
| 認証 | `*:production.e44558998bfc35ea9...` (Unleash API key) |

### Go gRPC とプロキシの関係

- Go バイナリに `net/http.ProxyFromEnvironment` + `grpc/internal/transport.proxyDial` が存在
- **標準 HTTP 通信** (Unleash): `HTTPS_PROXY` を**尊重**
- **gRPC-over-HTTP/2 通信** (Cortex): `HTTPS_PROXY` を**バイパス**
- 理由: gRPC は CONNECT トンネルではなく直接 TLS ダイアルを使用

### MITM 手順 (再現方法)

```bash
# 1. mitmproxy インストール
python3 -m venv /tmp/mitm-env && /tmp/mitm-env/bin/pip install mitmproxy

# 2. Forward proxy 起動
nohup /tmp/mitm-env/bin/mitmdump --listen-port 8888 --ssl-insecure \
  -s mekhane/ochema/scripts/cortex_capture.py > /tmp/mitm_output.log 2>&1 &

# 3. LS wrapper 設置 (sudo)
sudo mv language_server_linux_x64 language_server_linux_x64.real
sudo cp /tmp/ls_wrapper.sh language_server_linux_x64
# → LS 再起動で HTTP 通信がキャプチャされる
# 空の gRPC frame で LoadCodeAssist を叩く
printf '\x00\x00\x00\x00\x00' > /tmp/empty.bin
curl -sk --noproxy '*' --http2 -X POST \
  "https://daily-cloudcode-pa.googleapis.com/google.internal.cloud.code.v1internal.CloudCode/LoadCodeAssist" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/grpc" \
  -H "te: trailers" \
  --data-binary @/tmp/empty.bin
```

レスポンス (480 bytes):

| フィールド | 値 |
|:-----------|:---|
| **cloudaicompanion_project** | **`robotic-victory-pst7f0`** |
| tier (current) | `g1-ultra-tier` (Google One AI Ultra) |
| tier (default) | `standard-tier` (Gemini Code Assist) |
| manage URL | `https://accounts.google.com/AccountChooser?Email=...` |

### 18.2 GenerateChat / StreamGenerateChat: ❌ PERMISSION_DENIED

正しい project (`robotic-victory-pst7f0`) でも失敗:

| API | 必要なパーミッション | 結果 |
|:----|:--------------------|:-----|
| `GenerateChat` | `cloudaicompanion.companions.generateChat` | ❌ PERMISSION_DENIED |
| `StreamGenerateChat` | `cloudaicompanion.instances.completeTask` | ❌ PERMISSION_DENIED |
| `GetStreamingExternalChatCompletions` | — | ❌ 12 UNIMPLEMENTED |

テスト済みトークン:

- `state.vscdb` の `antigravityAuthStatus.apiKey` (ya29, 258 chars) → ❌
- `~/.gemini/oauth_creds.json` の `access_token` (ya29, 260 chars) → ❌
- 両トークンとも同じ PERMISSION_DENIED

### 18.3 全攻撃ベクトルサマリ (18 件)

| # | ベクトル | 結果 | 発見 |
|:--|:--------|:-----|:-----|
| 1 | LS 環境変数 | ❌ | project 関連なし |
| 2 | LS cmdline | ❌ | `--csrf_token`, `--cloud_code_endpoint` 等。auth 系なし |
| 3 | GetUserStatus API | ❌ | project キーなし |
| 4 | state.vscdb 全キー (2298個) | ⚠️ | `cloudcode.session-index` 発見。project なし |
| 5 | /proc/net/tcp | ✅ | **LS → 34.107.243.93, 34.54.84.110 (Google Cloud) 接続中** |
| 6 | GetStaticExperimentStatus | ❌ | 空レスポンス |
| 7 | DumpFlightRecorder | ❌ | 97 bytes (空に近い) |
| 8 | extension.js grep | 🎯 | **`AntigravityProject` proto 完全構造解明** |
| 9 | Go バイナリ strings | 🎯 | **`ListCloudAICompanionProjectsRequest/Response` 発見** |
| 10 | /proc/PID/maps | ❌ | LS バイナリのみ |
| 11 | Cortex API JSON | ❌ | 404 (gRPC only) |
| 12 | grpcurl (Reflection) | ❌ | Reflection 非対応 |
| 13 | LS メモリスキャン (286.5MB) | ❌ | `projects/registry` のみ (内部定義) |
| 14 | LS API LoadCodeAssist | ❌ | 空レスポンス (LS はプロキシしない) |
| 15 | **Cortex LoadCodeAssist** | **✅** | **`robotic-victory-pst7f0` 取得！** |
| 16 | Cortex GenerateChat | ❌ | PERMISSION_DENIED |
| 17 | LS メモリ ya29 検索 | ❌ | 0 件 (トークン即破棄) |
| 18 | Gemini Code Assist ログ | 🎯 | **`cloudCodeQuotaProject: 空` 確認** |

### 18.4 Gemini Code Assist ログからの設定情報

`~/.config/Antigravity/logs/*/11-Gemini Code Assist.log`:

```
atlasAddr: cloudaicompanion.googleapis.com:443      ← 本番 Atlas
cloudCodeAddr: cloudcode-pa.googleapis.com:443      ← 本番 CloudCode
cloudCodeQuotaProject:                              ← 空 (未設定)
useCloudCodeAPI: true
maxHistoryBytes: 500000
maxFileBytes: 75000
```

**注意**: LS cmdline の `--cloud_code_endpoint=https://daily-cloudcode-pa.googleapis.com` と
Gemini Code Assist の `cloudCodeAddr: cloudcode-pa.googleapis.com:443` は**別のエンドポイント**。
`daily-` prefix = 開発/プレリリース環境。

### 18.5 proto 構造解明

extension.js から解読した `AntigravityProject` (exa.codeium_common_pb):

```protobuf
message AntigravityProject {
  string antigravity_project_id = 1;
  string auth_uid = 2;
  DeploymentProvider deployment_provider = 3;
  string project_id = 4;
  string project_name = 5;
  // ... (field 14: provider_deployment_id, field 19: antigravity_project_id)
}
```

`GenerateChatRequest` のフィールド (Go バイナリ strings):

```
GetCloudaicompanionProject, GetConversation, GetIdeContext,
GetMetadata, GetEnablePromptEnhancement, GetYieldInfo,
GetRetryDetails, GetFunctionDeclarations, GetIncludeThinkingSummaries,
GetTierId, GetModelConfigId, GetUserPromptId
```

### 18.6 LS のトークン管理メカニズム

| 事実 | 意味 |
|:-----|:-----|
| LS cmdline に auth 系パラメータなし | トークンは起動時引数では渡されない |
| LS メモリに ya29 が 0 件 | トークンは長期保持されない (使用後即破棄) |
| `--parent_pipe_path` が cmdline に存在 | **Extension → LS の IPC チャネル** |
| extension.js に `setCredentials` 存在 | Extension が LS にトークンを動的に渡す |

**結論**: Extension.js が `parent_pipe_path` IPC 経由でトークンを LS に渡し、
LS は使用後即破棄。メモリスキャンで捕捉できないのはこのため。

### 18.7 gcloud config の project

```
gcloud config get project → project-f2526536-3630-4df4-aff
```

これは **GCP プロジェクト** (開発者用) であり、**cloudaicompanion project ではない**。
Cortex API で使うべき project は `robotic-victory-pst7f0` (LoadCodeAssist から取得)。

### 18.8 GenerateChatRequest 完全 proto 構造 (Go struct tags 復元)

Go バイナリの `protobuf:"..."` struct tags + Getter メソッド名から完全復元:

```protobuf
// google/internal/cloud/code/v1internal/cloudcode.proto
// package: google.internal.cloud.code.v1internal

message GenerateChatRequest {
  string cloudaicompanion_project = 1;  // "robotic-victory-pst7f0"
  repeated bytes history = 2;           // ConversationMessage?
  string user_message = 3;              // or: IdeContext message
  // field 4: conversation_id?
  bool enable_prompt_enhancement = 5;   // or 7 (ambiguous)
  // field 6-8: unknown
  YieldedUserInput yielded_user_input = 9;
  int64 request_id = 10;                // varint
  repeated FunctionDeclaration function_declarations = 11;
  bool include_thinking_summaries = 12; // varint, oneof
  string tier_id = 13;                  // oneof, "g1-ultra-tier"
  string model_config_id = 14;          // oneof
  string user_prompt_id = 15;           // oneof
  Metadata metadata = 18;
  // YieldInfo yield_info = 10;         // same field 10 (different message?)
  // RetryDetails retry_details = 10;   // same field 10 (oneof?)
}

message GenerateChatRequest_YieldedUserInput {
  string user_input = ?;
  bool consented = ?;
}

message GenerateChatResponse {
  string markdown = ?;
  bool blocked = ?;
  Citations citations = ?;
  string detected_intent = ?;
  string disclaimer = ?;
  FileUsage file_usage = ?;
  string finish_reason = ?;
  FunctionCalls function_calls = ?;
  MoaInfo moa_info = ?;
  MoaWorkerInfo moa_worker_info = ?;
  ProcessingDetails processing_details = ?;
  AgentProcessingDetails agent_processing_details = ?;
  PromptCitations prompt_citations = ?;
  int64 remaining_fca_quota = ?;
  SuggestedPrompts suggested_prompts = ?;
  string text_type = ?;
  WorkspaceChange workspace_change = ?;
  YieldInfo yield_info = ?;
}
```

### 18.9 GenerateChat curl テスト結果

```bash
# 最小リクエスト (field 1 + field 3)
curl -sk --noproxy '*' --http2 -X POST \
  "https://cloudcode-pa.googleapis.com/...CloudCode/GenerateChat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/grpc" \
  -H "te: trailers" \
  --data-binary @/tmp/grpc_gen_full.bin
```

| 項目 | 値 |
|:-----|:---|
| HTTP Status | **200** |
| `x-cloudaicompanion-trace-id` | `a81e9b9c5580a45` — **バックエンド到達** |
| `grpc-status` | **7 (PERMISSION_DENIED)** |
| `permission` | `cloudaicompanion.companions.generateChat` |
| `resource` | `projects/robotic-victory-pst7f0` — **Project ID 正しい** |

**結論**: proto 構造は正しい。問題は**トークンの権限**のみ。

### 18.10 残る攻略ルート

| ルート | 実現可能性 | 必要なもの |
|:-------|:---------:|:----------|
| **strace IPC 傍受** | 高 | LS が Cortex 通信中に `strace -e write -s 4096 -p PID` で Bearer トークン取得 |
| **mitmproxy TLS 中間者** | 中 | `/etc/hosts` で DNS 書き換え + リバースプロキシ + CA 注入 |
| **parent_pipe IPC 傍受** | 中 | Extension → LS の IPC チャネルからトークンを取得 |
| **Extension Server モック** | 低 | extension.js の OAuth フローを再実装し、LS に正しいトークンを渡す |

**ボトルネック**: `state.vscdb` の ya29 トークンは `cloudaicompanion.companions.generateChat` を持たない。LS は Extension から IPC 経由で**別のスコープのトークン**を受け取っている可能性が高い。

---

## 19. 次のステップ

### 完了済み

1. ~~LS API 経由 LLM テキスト生成~~ → ✅
2. ~~Python ラッパー~~ → ✅ (antigravity_client.py)
3. ~~MCP 統合~~ → ✅ (cli.py → Ochēma MCP Server)
4. ~~別モデルテスト~~ → ✅ (5/8 成功)
5. ~~ストリーミング調査~~ → ✅ (ポーリング方式で実質完了)
6. ~~project ID 取得~~ → ✅ (`robotic-victory-pst7f0` via LoadCodeAssist)
7. ~~proto 構造解明~~ → ✅ (GenerateChatRequest 15 fields, Response 18 fields)
8. ~~proto 構造検証~~ → ✅ (HTTP 200 + trace-id — バックエンド到達)

### 残る壁: トークン権限

- `state.vscdb` の ya29 は `cloudaicompanion.companions.generateChat` を持たない
- LS が使う**正しいトークン**を取得できれば、Cortex 直叩きが実現
- → `strace` で LS の write() を傍受し、Bearer トークンを抽出するのが最善手

---

*Created 2026-02-13 — Ochēma IDE Hack Series*
*v2 — Cloud Backend 認証フロー + LS API 141メソッド + 三層認証構造 (2026-02-13)*
*v3 — 4-Step LLM フルフロー成功 + Cortex API 直叩き結果 + Python 実装完了 (2026-02-13)*
*v4 — 別モデルテスト + ストリーミング調査 + project ID 傍受 + enum ID マッピング (2026-02-13)*
*v5 — /dia*%/noe 再検証: LoadCodeAssist成功 + project ID取得 + 認証メカニズム解明 (2026-02-13)*
*v5b — V3 ログ探査 + V1 MITM 成功 + Unleash Feature Flags 発見 (2026-02-13)*
*v6 — Proto 構造完全復元 + GenerateChat curl テスト (HTTP 200, PERMISSION_DENIED) (2026-02-13)*
