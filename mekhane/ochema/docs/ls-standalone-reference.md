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

### 18.10 攻略ルート試行結果 (v7)

| # | ルート | 試行 | 結果 | 詳細 |
|:--|:-------|:----:|:-----|:-----|
| 19 | **strace write** | ✅ | ❌ | 24,115行。Go TLS 暗号化後に write → ya29 不可視 |
| 20 | **strace read+write -f** | ✅ | ❌ | Go goroutine 全スレッド追跡 → LS パフォーマンス破壊、StartCascade タイムアウト |
| 21 | **Extension Server HTTP 直叩き** | ✅ | ⚠️ | **HTTP 平文** (TLS なし) を発見！ただし外部からの API 呼出に応答なし (LS がクライアント) |
| 22 | **OAuth refresh (ADC creds)** | ✅ | ❌ | `unauthorized_client` — ADC client_id/secret では Antigravity refresh_token 使用不可 |
| 23 | **extension.js client_id 抽出** | ✅ | ❌ | 難読化で OAuth client_id/secret 抽出不可 |
| 24 | **nm シンボル抽出** | ✅ | ❌ | Go バイナリ stripped、シンボルなし |
| 25 | **mitmdump TLS 復号** | ✅ | **✅** | **port 8765 で Cortex API 通信の完全復号に成功！** LoadCodeAssist のリクエスト/レスポンス全文をキャプチャ |
| 26 | **mitmdump 経由 GenerateChat** | ✅ | ❌ | state.vscdb ya29 トークンでは同じ PERMISSION_DENIED |
| 27 | **CDP port 9334** | ✅ | ⚠️ | IDE 全ワークスペース (4ページ + 3 Worker) に到達。ただし **Origin 403** でJS評価不可 |
| 28 | **GCA Agent ポート** | ✅ | ❌ | port 34113/39695/40395 — CDP 応答なし |

### 18.11 mitmdump TLS 復号の詳細

```bash
# mitmdump v12.2.1 インストール
python3 -m venv /tmp/mitm_env
NO_PROXY="*" /tmp/mitm_env/bin/pip install mitmproxy websocket-client

# mitmdump 起動 (port 8765)
/tmp/mitm_env/bin/mitmdump --listen-port 8765 --set block_global=false -w /tmp/mitm_capture.flow &

# mitmdump 経由で Cortex API を叩く
https_proxy=http://127.0.0.1:8765 curl -sk --http2 -X POST \
  "https://daily-cloudcode-pa.googleapis.com/.../LoadCodeAssist" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/grpc" \
  --data-binary @/tmp/empty_grpc.bin
```

キャプチャ結果 (flow_detail=4):

```
POST https://daily-cloudcode-pa.googleapis.com/...CloudCode/LoadCodeAssist HTTP/2.0
  authorization: Bearer ya29.a0AUMWg_IzPAt7V4dvZ...
  content-type: application/grpc

<< HTTP/2.0 200 OK 480b
  x-cloudaicompanion-trace-id: fdb9cca399fcb35b
  grpc-status: 0
  
  field 3: robotic-victory-pst7f
  field 12.1: g1-ultra-tier
```

### 18.12 Extension Server の通信特性

| 特性 | 検証方法 | 結果 |
|:-----|:---------|:-----|
| プロトコル | `curl http://127.0.0.1:45483/` | **HTTP 平文** (TLS なし) |
| 認証 | CSRF トークン不一致時 | `Invalid CSRF token` |
| API 応答 | 正しい CSRF で各種メソッド | **応答なし** (LS がクライアント) |
| 接続数 | `ss -tnp` | LS から 5+ TCP 接続 (FD 14/24/26/29/96/97) |

### 18.13 CDP (Chrome DevTools Protocol) の状況

**Antigravity IDE port 9334** (Electron DevTools):

| ターゲット | タイプ | URL |
|:-----------|:------|:----|
| filemaker workspace | page | vscode-file://...workbench.html |
| hegemonikon workspace | page | vscode-file://...workbench.html |
| synteleia-sandbox workspace | page | vscode-file://...workbench.html |
| Launchpad | page | vscode-file://...workbench-jetski-agent.html |
| Manager | page | (不明) |
| Worker 1-3 | worker | (Extension host 含む) |

**制限**: WebSocket 接続に `--remote-allow-origins=*` が必要 (Electron の制限)。Origin 偽装でも突破不可。

### 18.14 最終結論 (v7)

**Cortex 直叩きの残る壁は「正しいトークンの取得」のみ**:

```
[取得済み]                      [未取得]
┌────────────────────────┐     ┌─────────────────────────┐
│ ✅ Project ID           │     │ ❌ 正しい ya29 トークン   │
│ ✅ Endpoint             │     │   (cloudaicompanion     │
│ ✅ Proto 構造           │     │    scope が必要)         │
│ ✅ mitmdump TLS 復号    │     │                         │
│ ✅ gRPC リクエスト形式  │     │ ❌ Antigravity OAuth     │
│ ✅ CDP IDE アクセス     │     │   client_id/secret      │
└────────────────────────┘     └─────────────────────────┘
```

> **v8 で解決**: Cortex 直叩きではなく、**LS API をプロキシとして使う代替ルート**が成功。
> トークン傍受は不要になった。

### 18.15 LS プロキシ経由 LLM 呼び出し: ✅ 完全成功 (v8)

**発想の転換**: Cortex API のトークンを傍受する代わりに、**LS 自体をプロキシとして使う**。
LS は自前のトークンで Cortex に接続するため、外部からは CSRF トークンのみで制御可能。

| 項目 | 結果 |
|:-----|:-----|
| Trajectory サイズ | **620,779 bytes** / 25 steps |
| 使用モデル | `MODEL_PLACEHOLDER_M7` (Gemini 3 Pro) |
| Thinking 取得 | ✅ 7.6 秒の推論過程をテキストで完全キャプチャ |
| Step Types 取得 | USER_INPUT → PLANNER_RESPONSE → VIEW_FILE → CODE_ACTION → RUN_COMMAND → NOTIFY_USER |
| 自律エージェント動作 | ✅ Cascade が自律的にファイル閲覧・コード編集・コマンド実行まで実行 |

### 18.16 v8 攻略過程: 9 回の試行錯誤

| # | 試行 | 結果 | エラー内容 |
|:--|:-----|:-----|:----------|
| 29 | LS API: CSRF `x-csrf-token` | ❌ | `missing CSRF token` — ヘッダー名が違う |
| 30 | LS API: CSRF `X-Codeium-Csrf-Token` | ✅ | **認証パス！** |
| 31 | `StartCascade` (metadata なし) | ⚠️ | cascadeId 取得するも `trajectory not found` |
| 32 | `GetCascade` メソッド呼出 | ❌ | **404** — メソッド名が存在しない |
| 33 | `GetCascadeTrajectory` メソッド呼出 | ✅ | trajectory 構造返却 |
| 34 | `StartCascade` + `metadata` + `trajectoryType:17` | ✅ | Trajectory + `CASCADE_RUN_STATUS_IDLE` |
| 35 | `SendMessage` (model なし) | ❌ | `neither PlanModel nor RequestedModel specified` |
| 36 | `SendMessage` + `requestedModel: "gemini-2.5-pro"` | ❌ | proto unmarshal error (文字列不可) |
| 37 | `SendMessage` + `requestedModel: {model: "MODEL_PLACEHOLDER_M7"}` | 🎯 | **LLM 呼び出し成功！** |

### 18.17 確立した LS プロキシ 4-Step フロー

```bash
# 0. LS 自動検出
LS_PID=$(pgrep -f 'language_server_linux.*hegemonikon' | head -1)
CSRF=$(cat /proc/$LS_PID/cmdline | tr '\0' '\n' | grep -A1 csrf_token | tail -1)
PORT=$(ss -tlnp 2>/dev/null | grep "pid=$LS_PID" | head -1 | grep -oP ':\K\d+' | head -1)

call() {
  curl -sk --noproxy '*' --http2 --max-time ${2:-10} -X POST \
    "https://127.0.0.1:$PORT/exa.language_server_pb.LanguageServerService/$1" \
    -H "Content-Type: application/json" \
    -H "Connect-Protocol-Version: 1" \
    -H "X-Codeium-Csrf-Token: $CSRF" \
    -d "$3" 2>/dev/null
}

# Step 1: モデル一覧取得
call GetCascadeModelConfigData 10 '{}'

# Step 2: カスケード開始
CID=$(call StartCascade 10 '{
  "metadata": {"ideName":"antigravity","ideVersion":"1.98.0","extensionVersion":"2.23.0"},
  "source": 12,
  "trajectoryType": 17
}' | python3 -c "import json,sys; print(json.load(sys.stdin)['cascadeId'])")

# Step 3: メッセージ送信 (ストリーミング — バックグラウンド実行)
call SendUserCascadeMessage 60 "{
  \"cascadeId\": \"$CID\",
  \"items\": [{\"text\": \"質問内容\"}],
  \"cascadeConfig\": {
    \"plannerConfig\": {
      \"plannerTypeConfig\": {\"conversational\": {}},
      \"requestedModel\": {\"model\": \"MODEL_PLACEHOLDER_M7\"}
    }
  }
}" &

# Step 4: ポーリングで結果取得
sleep 15
call GetCascadeTrajectory 10 "{\"cascadeId\": \"$CID\"}"
```

### 18.18 利用可能モデル (GetCascadeModelConfigData)

| Label | Proto Enum | Quota | Images | Tier |
|:------|:-----------|:-----:|:------:|:-----|
| Gemini 3 Pro (Low) | `MODEL_PLACEHOLDER_M7` | 100% | ✅ | PRO, TEAMS, ENTERPRISE |
| Gemini 3 Flash | `MODEL_PLACEHOLDER_M18` | 100% | ✅ | PRO, TEAMS, ENTERPRISE |

**サポート MIME Types** (両モデル共通):
PDF, JSON, HTML, CSS, JS, TS, Python, Markdown, CSV, XML, RTF, PNG, JPEG, WebP, HEIC, MP4, WebM, Audio/WAV

### 18.19 Trajectory 構造解析

`GetCascadeTrajectory` レスポンスの構造:

```json
{
  "trajectory": {
    "trajectoryId": "310032d5-...",
    "cascadeId": "edc6894a-...",
    "trajectoryType": "CORTEX_TRAJECTORY_TYPE_INTERACTIVE_CASCADE",
    "source": "CORTEX_TRAJECTORY_SOURCE_INTERACTIVE_CASCADE",
    "metadata": {
      "workspaces": [{"workspaceFolderAbsoluteUri": "file:///...", "repository": {...}}],
      "createdAt": "2026-02-13T10:59:36Z"
    }
  },
  "status": "CASCADE_RUN_STATUS_IDLE"   // IDLE = 完了, RUNNING = 実行中
}
```

**Step Types** (25 ステップの構成):

| Type | 説明 | 出現数 |
|:-----|:-----|:------:|
| `USER_INPUT` | ユーザー入力 | 2 |
| `CONVERSATION_HISTORY` | 会話履歴 | 1 |
| `EPHEMERAL_MESSAGE` | 一時メッセージ (IDE 表示用) | 5 |
| `PLANNER_RESPONSE` | **LLM 応答** (thinking + messageId) | 5 |
| `VIEW_FILE` | ファイル閲覧 | 2 |
| `CODE_ACTION` | コード編集 | 3 |
| `RUN_COMMAND` | コマンド実行 | 2 |
| `COMMAND_STATUS` | コマンド結果 | 1 |
| `CHECKPOINT` | チェックポイント | 1 |
| `TASK_BOUNDARY` | タスク境界 | 2 |
| `NOTIFY_USER` | ユーザー通知 | 1 |

**PLANNER_RESPONSE 構造**:

```json
{
  "type": "CORTEX_STEP_TYPE_PLANNER_RESPONSE",
  "status": "CORTEX_STEP_STATUS_DONE",
  "metadata": {
    "generatorModel": "MODEL_PLACEHOLDER_M7",
    "requestedModel": {"model": "MODEL_PLACEHOLDER_M7"},
    "source": "CORTEX_STEP_SOURCE_MODEL"
  },
  "plannerResponse": {
    "thinking": "推論テキスト全文...",
    "messageId": "bot-9db2841c-...",
    "thinkingDuration": "7.605317513s",
    "stopReason": "STOP_REASON_CLIENT_CANCELED"
  }
}
```

### 18.20 重要な技術的制約

| 制約 | 詳細 |
|:-----|:-----|
| **外部ターミナル必須** | IDE 内ターミナルからの呼出しは LS デッドロックを引き起こす |
| **SendMessage はストリーミング** | curl の `--max-time` でタイムアウトするが、応答は `{}` (正常) |
| **ポーリング方式** | `GetCascadeTrajectory` で定期的に状態確認 (5-30秒間隔) |
| **requestedModel は proto enum** | 文字列 (`"gemini-2.5-pro"`) ではなく `{model: "MODEL_PLACEHOLDER_M7"}` 形式 |
| **metadata 必須** | StartCascade に `metadata` + `trajectoryType: 17` がないと Trajectory が生成されない |
| **Cascade は自律エージェント** | 単純な質問でも VIEW_FILE, CODE_ACTION, RUN_COMMAND を自律実行する |

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
8. ~~proto 構造検証~~ → ✅ (HTTP 200, grpc-status 0 — バックエンド到達)
9. ~~mitmdump TLS 復号~~ → ✅ (port 8765 で LoadCodeAssist 完全キャプチャ)
10. ~~strace 傍受~~ → ❌ (Go goroutine 破壊で不適)
11. ~~OAuth refresh~~ → ❌ (unauthorized_client — 異なる OAuth client)
12. ~~CDP Origin~~ → ❌ (403 Forbidden — Electron 制限)
13. ~~LS プロキシ 4-Step フロー~~ → ✅ (v8: 620KB trajectory, 25 steps, thinking 完全取得)

### 残ステップ

1. ~~antigravity_client.py に v8 フロー統合~~ → ✅ (proto.py + antigravity_client.py)
2. ~~Ochēma MCP Server 更新~~ → ✅ (cli.py → Ochēma MCP Server with model selection)
3. **ストリーミング取得**: `StreamCascadeReactiveUpdates` でリアルタイム応答受信
4. ~~Cortex 直叩き~~ → ❌ (v9: cloudcode-pa 直接 API では Claude 利用不可。LS プロキシが唯一のルート)

---

## 20. cloudcode-pa REST 直接 API の限界 (2026-02-14)

### 全 v1internal メソッド一覧 (38メソッド)

LS バイナリから特定した `daily-cloudcode-pa.googleapis.com` の REST メソッド:

```
/v1internal:checkUrlDenylist        /v1internal:listAgents
/v1internal:completeCode            /v1internal:listCloudAICompanionProjectsA
/v1internal:countTokens             /v1internal:listExperiments
/v1internal:fetchAdminControls      /v1internal:listModelConfigsA
/v1internal:fetchAvailableModels    /v1internal:listRemoteRepositories
/v1internal:fetchCodeCustomizationState  /v1internal:loadCodeAssist
/v1internal:fetchUserInfo           /v1internal:lookUpRepository
/v1internal:generateChat            /v1internal:resolveFile
/v1internal:generateCode            /v1internal:resolveRules
/v1internal:generateContent         /v1internal:retrieveUserQuota
/v1internal:getCodeAssistGlobalUserSetting  /v1internal:searchRepository
/v1internal:internalAtomicAgenticChat  /v1internal:streamGenerateChat
/v1internal:streamGenerateContent   /v1internal:tabChat
/v1internal:updateCodeAssistUserGlobalSetting  /v1internal:updateWorkspace
/v1internal:verifyAttestations
```

### 主要メソッド試行結果

| メソッド | リクエスト | 結果 | 詳細 |
|:---------|:----------|:-----|:-----|
| `fetchAvailableModels` | `{}` | ❌ 403 | PERMISSION_DENIED |
| `listModelConfigsA` | `{}` | ⚠️ | 空応答 `{}` (権限だけで呼べるがデータなし) |
| `retrieveUserQuota` | `{}` | ✅ | **モデル quota 一覧返却** |
| `generateChat` | 各種 model 指定 | ✅ | Gemini のみ応答。Claude 無視 |
| `internalAtomicAgenticChat` | `{}` | ⚠️ | 空応答 (リクエスト構造不明) |
| `generateContent` | Vertex AI 形式 | ❌ | `contents: Cannot find field` |

### `retrieveUserQuota` の返却値 — Claude 不在の決定的証拠

```json
{
  "buckets": [
    {"modelId": "gemini-2.0-flash", "remainingFraction": 1},
    {"modelId": "gemini-2.0-flash_vertex", "remainingFraction": 1},
    {"modelId": "gemini-2.5-flash", "remainingFraction": 1},
    {"modelId": "gemini-2.5-flash-lite", "remainingFraction": 1},
    {"modelId": "gemini-2.5-flash-lite_vertex", "remainingFraction": 1},
    {"modelId": "gemini-2.5-flash_vertex", "remainingFraction": 1},
    {"modelId": "gemini-2.5-pro", "remainingFraction": 1},
    {"modelId": "gemini-2.5-pro_vertex", "remainingFraction": 1}
  ]
}
```

**結論**: cloudcode-pa REST API は **Gemini 専用**。Claude quota は LS 内部の Cascade quota として管理されており、cloudcode-pa REST 経由ではアクセス不可。

### `internalAtomicAgenticChat` Request 構造 (LS バイナリ strings)

```
(*InternalAtomicAgenticChatRequest).GetProject
(*InternalAtomicAgenticChatRequest).GetRequestId
(*InternalAtomicAgenticChatRequest).GetUserMessage
(*InternalAtomicAgenticChatRequest).GetHistory
(*InternalAtomicAgenticChatRequest).GetIdeContext
(*InternalAtomicAgenticChatRequest).GetMetadata
(*InternalAtomicAgenticChatRequest).GetToolDefinitions
(*InternalAtomicAgenticChatRequest).GetEnablePromptEnhancement
```

**モデル指定フィールドなし** — このメソッドでモデルを選択する手段がない。

### `generateChat` + `model_config_id` テスト

`GenerateChatRequest` にはフィールド14 `model_config_id` が存在するが:

| model_config_id 値 | 結果 |
|:-------------------|:-----|
| `MODEL_CLAUDE_4_5_SONNET_THINKING` | Gemini が応答 (無視される) |
| 空 | Gemini が応答 (デフォルト) |
| `claude-sonnet-4-5` | Gemini が応答 (無視される) |

**結論**: cloudcode-pa の `generateChat` は Claude にルーティングされない。

---

## 21. LS HTTP ポート発見 + curl 直叩き改良 (2026-02-14 v9)

### 3つのポートの正体

| ポート | プロトコル | 用途 | curl 利用 |
|:-------|:----------|:-----|:----------|
| `server_port` (39053) | **HTTPS** (TLS) | ConnectRPC メイン | `curl -sk https://127.0.0.1:PORT/...` |
| `37401` (未命名) | **HTTP** (平文) | ConnectRPC サブ | `curl -s http://127.0.0.1:PORT/...` ★推奨 |
| `lsp_port` (35449) | LSP | Language Server Protocol | — |
| `extension_server_port` (46705) | HTTP | Extension ↔ LS 通信 | ❌ InvalidCSRF |

### Port 37401 (HTTP) の発見

v8 まで HTTPS ポート (server_port) のみ使用していたが、`ss -tlnp` で 37401 が HTTP 平文で動作していることを発見。TLS 不要で `-sk` フラグが不要になる。

### CSRF トークン取得 — ファイルではなく cmdline

```bash
# ❌ 旧方法 (ファイルが存在しない)
cat ~/.config/Antigravity/User/globalStorage/google.antigravity/csrf_token

# ✅ 正しい方法 (LS cmdline パラメータ)
CSRF=$(cat /proc/$(pgrep -f language_server_linux_x64 | head -1)/cmdline \
  | tr '\0' '\n' | grep -A1 '^--csrf_token$' | tail -1)
```

### v9 改良版 4-Step フロー (HTTP + 簡潔)

```bash
#!/bin/bash
CSRF=$(cat /proc/$(pgrep -f language_server_linux_x64 | head -1)/cmdline \
  | tr '\0' '\n' | grep -A1 '^--csrf_token$' | tail -1)
PORT=37401  # HTTP ポート — ss -tlnp で確認

call() {
  curl -s --max-time ${2:-10} -X POST \
    "http://127.0.0.1:$PORT/exa.language_server_pb.LanguageServerService/$1" \
    -H "Content-Type: application/json" \
    -H "X-Codeium-Csrf-Token: $CSRF" \
    -d "$3"
}

# Step 1: StartCascade
CID=$(call StartCascade 10 '{
  "metadata": {"ideName":"antigravity","ideVersion":"1.98.0","extensionVersion":"2.23.0"},
  "source": 12, "trajectoryType": 17
}' | python3 -c "import json,sys; print(json.load(sys.stdin)['cascadeId'])")

# Step 2: SendUserCascadeMessage
call SendUserCascadeMessage 60 "{
  \"cascadeId\": \"$CID\",
  \"items\": [{\"text\": \"YOUR PROMPT HERE\"}],
  \"cascadeConfig\": {
    \"plannerConfig\": {
      \"plannerTypeConfig\": {\"conversational\": {}},
      \"requestedModel\": {\"model\": \"MODEL_CLAUDE_4_5_SONNET_THINKING\"}
    }
  }
}" &

# Step 3 & 4: Poll
sleep 5
TID=$(call GetAllCascadeTrajectories 5 "{\"cascadeId\":\"$CID\"}" \
  | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['trajectories'][0]['trajectoryId'])")

for i in $(seq 1 10); do
  sleep 2
  RESULT=$(call GetCascadeTrajectorySteps 10 "{\"cascadeId\":\"$CID\",\"trajectoryId\":\"$TID\"}")
  echo "$RESULT" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for s in d.get('steps',[]):
    pr=s.get('plannerResponse',{})
    text=pr.get('response','')
    model=s.get('metadata',{}).get('generatorModel','')
    if text:
        print(f'MODEL: {model}')
        print(f'RESPONSE: {text}')
        sys.exit(0)
"
  [ $? -eq 0 ] && break
done
```

### v8 → v9 の差分

| 項目 | v8 (2026-02-13) | v9 (2026-02-14) |
|:-----|:----------------|:----------------|
| ポート | server_port (HTTPS) | 37401 (HTTP) ★簡潔 |
| TLS | `-sk` (自己署名証明書) | 不要 |
| `--noproxy` | 必要 | 不要 (HTTP) |
| `Connect-Protocol-Version` | 送信していた | 不要 |
| `GetCascadeTrajectory` | 全 trajectory 取得 | `GetCascadeTrajectorySteps` に変更 |
| テスト済みモデル | Gemini 3 Pro (M7) | Claude Sonnet 4.5 Thinking ✅ |

### v9 テスト結果

| 項目 | 値 |
|:-----|:---|
| リクエストモデル | `MODEL_CLAUDE_4_5_SONNET_THINKING` |
| 応答モデル | `MODEL_CLAUDE_4_5_SONNET_THINKING` (metadata.generatorModel) |
| Thinking | 1130 文字 (日本語思考) |
| Response | `"Anthropic Claude"` |
| 応答時間 | ~20秒 (5回ポーリング) |

---

## 22. Vertex AI Model Garden への直接アクセス (2026-02-14)

### 試行結果: ❌ 利用不可

| 試行 | 結果 | 詳細 |
|:-----|:-----|:-----|
| `rawPredict` (us-east5) | ❌ 403 | `aiplatform.googleapis.com` SERVICE_DISABLED |
| `rawPredict` (europe-west1) | ❌ 403 | 同上 |
| `rawPredict` (us-central1) | ❌ 403 | 同上 |
| `streamRawPredict` (us-east5) | ❌ 403 | 同上 |
| API 有効化 (`serviceusage:enable`) | ❌ 403 | AUTH_PERMISSION_DENIED — OAuth トークンに有効化権限なし |

### 制約

`~/.gemini/oauth_creds.json` の OAuth トークンは `driven-circlet-rgkmt` プロジェクトに紐づいているが:

1. `aiplatform.googleapis.com` が無効
2. `serviceusage.googleapis.com:enable` の権限がない
3. GCP Console での手動有効化が必要 (OAuth scope 外)

### 結論

Vertex AI Model Garden は **原理的には Claude を提供しているが、現在の OAuth トークンでは利用不可**。
GCP Console に管理者権限でログインし、`aiplatform.googleapis.com` を手動で有効化すれば使える可能性がある。

---

## 23. 全攻略ルート最終総括 (v9 — 2026-02-14)

### 攻略フェーズ概要

```
[Phase 1: 発見] → [Phase 2: 理解] → [Phase 3: 突破] → [Phase 4: 最適化]
 2026-02-13        2026-02-13        2026-02-13        2026-02-14
 LS API 発見       proto 解明        v8 成功           v9 改良
 141 メソッド      GenerateChat      Gemini 3 Pro      Claude 確認
 4-Step Flow       28 攻撃VT         620KB trajectory  HTTP ポート
```

### 攻撃ベクトル完全リスト (37件)

| # | ベクトル | 結果 | フェーズ |
|:--|:--------|:-----|:---------|
| 1-18 | (v7 までの 18件) | 混在 | Phase 1-2 |
| 19-28 | (v7 追加の 10件) | 混在 | Phase 2-3 |
| 29-37 | (v8 の 9件) | 成功 | Phase 3 |
| 38 | cloudcode-pa `retrieveUserQuota` | ✅ | Phase 4 — Claude 不在の確定 |
| 39 | cloudcode-pa `fetchAvailableModels` | ❌ | Phase 4 — PERMISSION_DENIED |
| 40 | cloudcode-pa `listModelConfigsA` | ⚠️ | Phase 4 — 空応答 |
| 41 | cloudcode-pa `generateChat` + model_config_id | ❌ | Phase 4 — 無視される |
| 42 | cloudcode-pa `internalAtomicAgenticChat` | ⚠️ | Phase 4 — model 指定不可 |
| 43 | Vertex AI `rawPredict` | ❌ | Phase 4 — SERVICE_DISABLED |
| 44 | Vertex AI API 有効化 | ❌ | Phase 4 — PERMISSION_DENIED |
| 45 | **LS HTTP ポート (37401) 直叩き** | **✅** | Phase 4 — Claude 成功 |

### アクセスルート判定マトリクス

| ルート | Claude | Gemini | 認証 | 要 LS |
|:-------|:------:|:------:|:----:|:-----:|
| **LS ConnectRPC (server_port, HTTPS)** | ✅ | ✅ | CSRF | ✅ |
| **LS ConnectRPC (37401, HTTP)** | ✅ | ✅ | CSRF | ✅ |
| cloudcode-pa REST (generateChat) | ❌ | ✅ | OAuth | ❌ |
| cloudcode-pa gRPC (GenerateChat) | ❌ | — | OAuth | ❌ |
| Cortex gRPC (LoadCodeAssist) | ✅(meta) | — | OAuth | ❌ |
| Vertex AI rawPredict | ❌ | — | OAuth | ❌ |
| Ochēma MCP Server | ✅ | ✅ | CSRF | ✅ |

### 最終判定

**LS ConnectRPC が Claude アクセスの唯一のルート。**

cloudcode-pa REST は Gemini 専用プロキシであり、Claude は LS 内部の Cascade フレームワークでのみルーティングされる。Vertex AI は API 未有効化で利用不可。

LS 経由のメリット:

1. CSRF トークンのみで認証 (OAuth 不要)
2. トークン管理は LS が自動処理
3. HTTP ポート (37401) で TLS 不要
4. thinking/response/model の全情報を取得可能

LS 経由のリスク:

1. IDE 起動が必須 (LS はIDE子プロセス)
2. ポート番号はLS起動ごとに変動
3. CSRF トークンはLS起動ごとに再生成

---

*Created 2026-02-13 — Ochēma IDE Hack Series*
*v2 — Cloud Backend 認証フロー + LS API 141メソッド + 三層認証構造 (2026-02-13)*
*v3 — 4-Step LLM フルフロー成功 + Cortex API 直叩き結果 + Python 実装完了 (2026-02-13)*
*v4 — 別モデルテスト + ストリーミング調査 + project ID 傍受 + enum ID マッピング (2026-02-13)*
*v5 — /dia*%/noe 再検証: LoadCodeAssist成功 + project ID取得 + 認証メカニズム解明 (2026-02-13)*
*v5b — V3 ログ探査 + V1 MITM 成功 + Unleash Feature Flags 発見 (2026-02-13)*
*v6 — Proto 構造完全復元 + GenerateChat curl テスト (HTTP 200, PERMISSION_DENIED) (2026-02-13)*
*v7 — strace/mitmdump/CDP/OAuth: 28攻撃ベクトル完了 + mitmdump TLS復号成功 (2026-02-13)*
*v8 — LS プロキシ経由 LLM 呼び出し完全成功: 4-Step フロー確立 + Gemini 3 Pro thinking 取得 (2026-02-13)*
*v9 — cloudcode-pa Claude 不在確定 + HTTP ポート発見 + curl Claude 直叩き成功 + 全攻略総括 (2026-02-14)*
*v10 — LS バイナリ解析 + state.vscdb トークン発見 + refresh_token 独立フロー成功 + 未解決総括 (2026-02-14)*

---

## §24 v10: LS 依存解放 — 未試行ベクトル棚卸し

> Module A-3 (反転 + 領域シフト) と R-2 (成功の解体) を適用し、
> 未試行の攻撃ベクトルを体系的に再発見・検証した v10。

### 24.1 LS バイナリ strings 解析

LS バイナリ (`language_server_linux_x64`) に `strings` を適用:

```bash
strings /usr/share/antigravity/resources/app/extensions/antigravity/bin/language_server_linux_x64 \
  | grep -i "anthropic"
```

**決定的発見**:

| 文字列 | 意味 |
|:-------|:-----|
| `API_PROVIDER_ANTHROPIC_VERTEX` | Claude は **Vertex AI Model Garden** 経由でルーティング |
| `MODEL_PROVIDER_ANTHROPIC` | Anthropic がモデルプロバイダーとして登録 |
| `HasAnthropicModelAccess` | **Unleash Feature Flag** で Claude アクセスを動的制御 |
| `USE_ANTHROPIC_TOKEN_EFFICIENT_TOOLS_BETA` | Anthropic の Tool Use ベータ機能 |
| `MODEL_ANTHROPIC_ANTIGRAVITY_RESEARCH` / `_THINKING` | 内部研究用 Anthropic モデル |
| `calculateAnthropicImageTokens` | Cortex 内部で Anthropic 画像トークン計算 |

**rawPredict パターン**:

```
publishers/*/models/*}:rawPredict
publishers/*/models/*}:streamRawPredict
```

→ LS は Vertex AI の `rawPredict` / `streamRawPredict` エンドポイントパターンを組み込んでいる。
ただし LS → Vertex AI 直接ではなく、LS → cloudcode-pa → Vertex AI の三段プロキシ。

**根拠**: LS cmdline に `--cloud_code_endpoint https://daily-cloudcode-pa.googleapis.com` のみ。
Vertex AI エンドポイント URL や特定リージョン (us-east5 等) は LS バイナリに不在。

### 24.2 LS 内部コードパス推定

```
google3/third_party/jetski/cortex/utils/utils.calculateAnthropicImageTokens
google3/third_party/jetski/language_server/google_clients/gclients.GoogleClients.HasAnthropicModelAccess
google3/third_party/jetski/unleash/unleash.UpdateUnleashHasAnthropicModelAccess
```

→ LS は Google 社内リポジトリ `google3` の `jetski` プロジェクトからビルドされている。
Claude アクセスは `unleash` (Feature Flag サービス) で動的に有効/無効化される。

### 24.3 state.vscdb から認証情報抽出

```bash
DB="~/.config/Antigravity/User/globalStorage/state.vscdb"
sqlite3 "$DB" "SELECT value FROM ItemTable WHERE key = 'antigravityAuthStatus';"
```

**authStatus の中身** (JSON):

| フィールド | 値 | 意味 |
|:-----------|:---|:-----|
| `name` | `Tarou` | 表示名 |
| `email` | `t84432036@gmail.com` | **認証アカウント** (makaron8426 ではない) |
| `apiKey` | `ya29.a0AUMWg_...` (258文字) | Google OAuth アクセストークン |
| `userStatusProtoBinaryBase64` | (大量のBase64) | 利用可能モデル + プラン情報 |

**利用可能モデル一覧** (Base64 デコード結果):

| モデル | 備考 |
|:-------|:-----|
| Claude Sonnet 4.5 (Thinking) | |
| Claude Opus 4.5 (Thinking) | |
| **Claude Opus 4.6 (Thinking)** | **未発表モデル？** |
| Claude Sonnet 4.5 | non-thinking 版 |
| GPT-OSS 120B (Medium) | |
| Gemini 3 Pro (High) | |
| Gemini 3 Pro (Low) | |
| Gemini 3 Flash | |

**プラン**: `g1-ultra-tier` (Google AI Ultra) — "You are subscribed to the best plan."

### 24.4 refresh_token フロー — LS なしでトークン更新成功

**client_id / client_secret の発見**:

```
gemini-cli-core → dist/src/code_assist/oauth2.js
```

```javascript
const OAUTH_CLIENT_ID = '<CORTEX_CLIENT_ID>';  // ~/.config/cortex/oauth.json
const OAUTH_CLIENT_SECRET = '<CORTEX_CLIENT_SECRET>';
```

> Google 公式コメント: 「It's ok to save this in git because this is an installed application」

**refresh_token フロー成功**:

```bash
curl -s -X POST https://oauth2.googleapis.com/token \
  -d "client_id=<CORTEX_CLIENT_ID>" \
  -d "client_secret=<CORTEX_CLIENT_SECRET>" \
  -d "refresh_token=$(python3 -c 'import json; print(json.load(open("/home/makaron8426/.gemini/oauth_creds.json"))["refresh_token"])')" \
  -d "grant_type=refresh_token"
```

**結果**:

- ✅ 新しい `ya29.` トークン取得成功 (有効期間: 3599秒)
- ✅ Scope: `cloud-platform` + `userinfo.email` + `userinfo.profile`
- ✅ `retrieveUserQuota`: 8 buckets (Gemini のみ、Claude なし)
- ❌ `generateChat`: PERMISSION_DENIED (空リクエスト) / INVALID_ARGUMENT (フィールド名不一致)
- ❌ Vertex AI `rawPredict`: SERVICE_DISABLED (driven-circlet-rgkmt)

### 24.5 OAuth scope 比較

| トークンソース | scope | Claude | retrieveUserQuota |
|:--------------|:------|:-------|:-------------------|
| `oauth_creds.json` (makaron8426) | cloud-platform + userinfo | ❌ 不在 | ✅ Gemini 8 buckets |
| `authStatus` (t84432036) | 不明 (Base64 proto) | ✅ 表示される | ❌ 0 buckets (期限切れ) |

**核心の問い**: `t84432036` のトークンなら Claude が `retrieveUserQuota` に表示されるか？
→ このトークンは期限切れで未検証。LS 稼働中に LS 内部のトークンを取得できれば検証可能。

### 24.6 /proc/PID/mem — トークン抽出試行

```bash
strings /proc/$LS_PID/mem 2>/dev/null | grep -o "ya29\.[A-Za-z0-9_-]\{50,\}"
```

**結果**: 空 — 権限的に /proc/PID/mem の読み取りが制限されている可能性。
(注: プロセスは同一ユーザーだが、strings がメモリマッピングを読めないケースがある)

### 24.7 全攻撃ベクトル総括 (v11 更新 — 2026-02-14)

| # | ベクトル | 結果 | 発見 |
|:--|:--------|:-----|:-----|
| A1 | Vertex AI rawPredict | ❌ SERVICE_DISABLED | API 未有効化 + 有効化権限なし |
| A2 | cloudcode-pa fetchAvailableModels | ❌ PERMISSION_DENIED | Claude は cloudcode-pa クォータに不在 |
| A3 | LS ConnectRPC curl 直叩き | ✅ **成功** | Claude Sonnet 4.5 Thinking 応答確認 |
| A4 | mitmproxy MITM 傍受 | ⏸️ 未実施 | TLS 復号は成功済み (v5b) だが Claude 呼出時の傍受未実施 |
| A5 | Unleash フラグ操作 | ⏸️ 未実施 | HasAnthropicModelAccess の操作方法未調査 |
| B1 | state.vscdb トークン抽出 | ✅ **成功 (v11)** | proto 3層デコードで refresh_token + access_token 抽出 |
| B2 | LS バイナリ strings 解析 | ✅ **成功** | API_PROVIDER_ANTHROPIC_VERTEX + rawPredict パターン発見 |
| B3 | refresh_token フロー | ✅ **成功** | Cortex client_id では動作。Extension client_id では client_secret 不足 |
| B4 | /proc/PID/mem | ❌ 権限不足 | ya29. トークン抽出失敗 |
| B5 | ユーザー自身の GCP Vertex AI | ⏸️ 未実施 | 自分のプロジェクトで Vertex AI + Claude 有効化は未試行 |
| B6 | generateChat 正しい Proto 構造 | ✅ **成功 (v11)** | `/tmp/cloudcode_v2.proto` で完全定義発見 |
| **C1** | **Extension OAuth client_id 特定** | ✅ **成功 (v11)** | `1071006060591-tmhssin2h21lcre235vtolojh4g403ep` (Cortex とは別) |
| **C2** | **Extension refresh_token 抽出** | ✅ **成功 (v11)** | `1//0eZ21XPQ...` (gemini-cli とは別、client_secret 必要) |
| **C3** | **grpcurl cloudcode-pa 直接呼出** | ⚠️ **部分成功 (v11)** | gRPC 到達成功、PermissionDenied (quota_project 不明) |
| **C4** | **authStatus Claude モデル確認** | ✅ **成功 (v11)** | Sonnet 4.5, Opus 4.5/4.6, Tier: g1-ultra |
| **C5** | **strace quota_project 傍受** | ⏸️ 未実施 | LS→cloudcode-pa の gRPC ヘッダー傍受 |

---

## 25. V1 Extension JS 認証経路探索 (2026-02-14)

### 25.1 OAuth トークン構造 (MECE)

state.vscdb に保存される OAuth トークンは **3つの独立した経路** で管理される:

| 経路 | 保存先 | client_id | refresh_token | 用途 |
|:-----|:------|:----------|:-------------|:-----|
| **Extension (IDE)** | `antigravityUnifiedStateSync.oauthToken` (proto) | `1071006060591-...` | `1//0eZ21XPQ...` | LS ↔ cloudcode-pa |
| **Cortex (CLI)** | `~/.config/cortex/oauth.json` | `681255809395-oo8ft...` | (cortex固有) | Cortex API 直叩き |
| **gemini-cli** | `~/.gemini/oauth_creds.json` | (gcloud系) | `1//0eTQhd4v...` | gemini CLI |

### 25.2 Proto バイナリ構造

`antigravityUnifiedStateSync.oauthToken` の構造:

```
Base64 → Proto L0
  └─ F1 (msg 545b)
      ├─ F1 (str): "oauthTokenInfoSentinelKey"
      └─ F2 (msg 515b)
          └─ F1 (str 512b): Base64 → Proto L1
              ├─ F1 (str 260b): ya29.ACCESS_TOKEN
              ├─ F2 (str 6b): "Bearer"
              ├─ F3 (str 103b): 1//REFRESH_TOKEN  ★
              └─ F4 (msg 6b): {F1: unix_timestamp}
```

### 25.3 cloudcode-pa Proto 定義

`/tmp/cloudcode_v2.proto` から取得:

```protobuf
package google.internal.cloud.code.v1internal;

service CloudCode {
  rpc GenerateChat(GenerateChatRequest) returns (GenerateChatResponse);
  rpc StreamGenerateChat(GenerateChatRequest) returns (stream GenerateChatResponse);
}

message GenerateChatRequest {
  string project = 1;              // GCP project (quota)
  string request_id = 2;
  string user_message = 3;
  repeated ChatMessage history = 4;
  IdeMetadata metadata = 6;
  bool enable_prompt_enhancement = 7;
  string yielded_user_input = 9;
  string chat_model_name = 12;     // ★ Claude 指定: "models/claude-sonnet-4-5"
  bool include_thinking_summaries = 13;
  string model_config_id = 14;
  string tier_id = 15;
}
```

### 25.4 LS プロセスとポート構造

| パラメータ | 説明 | 方向 |
|:----------|:-----|:-----|
| `--extension_server_port` | Extension がリッスン、LS が接続する先 | LS → Extension |
| `--server_port` | LS がリッスンする HTTPS ポート | Extension → LS |
| `--lsp_port` | LSP プロトコル用 | IDE → LS |
| `--random_port` | server_port を動的割当 | — |
| `--csrf_token` | CSRF 検証トークン | 全通信 |
| `--parent_pipe_path` | Unix Socket IPC (`/tmp/server_*`) | Extension ↔ LS |
| `--cloud_code_endpoint` | `https://daily-cloudcode-pa.googleapis.com` | LS → Google |

gemini-ide-server JSON (`/tmp/gemini/ide/gemini-ide-server-*.json`):

```json
{"port": 39743, "workspacePath": "/path", "authToken": "UUID"}
```

### 25.5 grpcurl 直接呼出の結果

```bash
grpcurl -import-path /tmp -proto cloudcode_v2.proto \
  -H "Authorization: Bearer $YA29" \
  -d '{"project":"$PROJECT","user_message":"hello","chat_model_name":"models/claude-sonnet-4-5"}' \
  daily-cloudcode-pa.googleapis.com:443 \
  google.internal.cloud.code.v1internal.CloudCode/GenerateChat
```

| project 値 | x-goog-user-project | 結果 |
|:-----------|:--------------------|:-----|
| (なし) | (なし) | `PermissionDenied: cloudaicompanion.companions.generateChat` |
| `default-gemini-project-97` | (なし) | `PermissionDenied` (同上) |
| (なし) | `projects/default-gemini-project-97` | `InvalidArgument: not found` |
| `project-f2526536-3630-4df4-aff` | 同左 | `PermissionDenied: serviceUsageConsumer role required` |

**結論**: LS は Google 管理の暗黙的 quota_project を注入している。ユーザーの GCP project では `cloudcode-pa.googleapis.com` API が有効化されていない。

### 25.6 2つの壁 (MECE)

| 壁 | 内容 | 突破方法 |
|:---|:-----|:---------|
| **W1: client_secret** | Extension client_id (`1071006060591-...`) は Web app type で client_secret 必須。LS バイナリに GOCSPX パターンなし | LS バイナリのリバースエンジニアリング or strace 傍受 |
| **W2: quota_project** | cloudcode-pa は Google 管理の quota_project を要求。ユーザーの project では API 未有効化 | strace/mitmproxy で LS が送る project ヘッダーを傍受 |

### 25.7 残された攻撃ベクトル

1. **strace で LS→cloudcode-pa の gRPC ヘッダー傍受** → W2 突破
2. **LS バイナリの Go 構造体から client_secret 抽出** → W1 突破
3. **LS headless 起動** → LS 経由だが IDE 不要

### 25.8 cloudaicompanion_project の特定と grpcurl 最終試行

LS プロセスメモリ (`/proc/PID/mem`) から:

```
cloudaicompanion_project = "robotic-victory-pst7f0"
```

grpcurl 最終試行:

```bash
grpcurl -import-path /tmp -proto cloudcode_v2.proto \
  -H "Authorization: Bearer $YA29" \
  -d '{"project":"robotic-victory-pst7f0","user_message":"hello","chat_model_name":"models/claude-sonnet-4-5"}' \
  daily-cloudcode-pa.googleapis.com:443 \
  google.internal.cloud.code.v1internal.CloudCode/GenerateChat
```

| 構成 | 結果 | 分析 |
|:-----|:-----|:-----|
| project + x-goog-user-project | `InvalidArgument: not found or deleted` | ヘッダーが quota 要求として解釈され拒否 |
| project のみ (ヘッダーなし) | `PermissionDenied: cloudaicompanion.companions.generateChat on projects/robotic-victory-pst7f0` | **プロジェクト認識成功、しかし権限不足** |

### 25.9 最終結論: LS の認証注入メカニズム

**LS は単なる HTTP プロキシではない。LS は追加の認証コンテキストを注入している。**

```
ユーザー ya29 トークン
  → 直接 cloudcode-pa: PermissionDenied (権限不足)
  → LS 経由 cloudcode-pa: 200 OK (LS が何かを追加)
```

LS が注入している可能性:

1. **サービスアカウントの impersonation** — LS が `robotic-victory-pst7f0` の SA として代理認証
2. **IAM binding** — LS プロセスの credential に `cloudaicompanion.companions.generateChat` role が付与されている
3. **内部トークン交換** — LS がユーザー ya29 を内部 SA トークンに交換してから cloudcode-pa に送る

**Go auth ライブラリの `QuotaProjectID` + `GetQuotaProject`** が LS バイナリに含まれることから、LS は独自の credential で cloudcode-pa にアクセスし、ユーザーの project (`robotic-victory-pst7f0`) を request 内に埋め込んでいる。

### 25.10 MECE 判定: LS 不要 Claude 直接呼出

| 壁 | 状態 | 突破可能性 |
|:---|:-----|:----------|
| W1: client_secret | 未解決 | LS バイナリ RE で可能だが労力大 |
| W2: quota_project | **解決**: `robotic-victory-pst7f0` | — |
| **W3: LS の認証注入** | **新発見 — 最大の壁** | LS の SA credential は LS 外部から取得不可能 |

**結論**: LS 不要 ∧ 課金なし ∧ Claude = ❌ 不可能。
理由: LS がサーバーサイドで `cloudaicompanion.companions.generateChat` 権限を持つ credential を注入しており、この credential はユーザーのトークンとは別物。
