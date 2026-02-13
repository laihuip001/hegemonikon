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

### 検証結果: 行き止まり

Cloud Backend (Cortex API) への直叩きは、3 ルート全て失敗:

| メソッド | プロトコル | 結果 | gRPC Status |
|:---------|:-----------|:-----|:------------|
| `ListCloudAICompanionProjects` | gRPC (binary) | ❌ | **12 UNIMPLEMENTED** |
| `GenerateChat` | gRPC (binary) | ❌ | **7 PERMISSION_DENIED** |
| `StreamGenerateChat` | gRPC (binary) | ❌ | **7 PERMISSION_DENIED** |
| 全メソッド | JSON/REST (curl) | ❌ | **404 Not Found** |
| 全メソッド | grpcurl (Reflection) | ❌ | **Reflection 未対応** |

### PERMISSION_DENIED の詳細

`grpc-status-details-bin` (base64 decoded):

```
GenerateChat:
  IAM_PERMISSION_DENIED on iam.googleapis.com
  permission: cloudaicompanion.companions.generateChat
  resource: projects/     ← project が空!

StreamGenerateChat:
  IAM_PERMISSION_DENIED on iam.googleapis.com
  permission: cloudaicompanion.instances.completeTask
  resource: projects/     ← project が空!
```

### 結論

- **Cortex API は gRPC only** (JSON/REST は 404)
- **Reflection API 無効** (proto descriptor なしでは grpcurl も使えない)
- **project ID が必須** だが、`ListCloudAICompanionProjects` は UNIMPLEMENTED
- **project ID は LS 内部の OAuth フローでのみ取得可能**
- → **LS 経由 4-Step フローが唯一の実用ルート**

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

## 16. 次のステップ

### 確定 (LS 経由ルート)

1. ~~LS API 経由で LLM テキスト生成~~ → **✅ 完了** (antigravity_client.py)
2. ~~Python ラッパースクリプト化~~ → **✅ 完了** (AntigravityClient)
3. ~~Ochēma MCP Backend 統合~~ → **✅ 完了** (cli.py → MCP Server)

### 未着手

1. **別モデルテスト**: Opus 4.6 (`MODEL_PLACEHOLDER_M26`), Gemini 3 Pro で動作確認
2. **ストリーミング対応**: `StreamCascadeReactiveUpdates` でリアルタイム応答取得
3. **Extension Server モック**: 最小 HTTP OAuth → Standalone LS の認証解決
4. **project ID 特定**: LS の OAuth フローを strace/mitmproxy で傍受し、project ID を抽出

### Cortex 直叩き (未解決)

- **project ID 問題**: LS 内部でしか取得できない。`OnboardUserResponse` の傍受が必要
- **proto descriptor**: LS バイナリから FileDescriptorSet を抽出すれば grpcurl で正式な呼び出しが可能

---

*Created 2026-02-13 — Ochēma IDE Hack Series*
*v2 — Cloud Backend 認証フロー解明 + LS API 141メソッド + 三層認証構造 追加 (2026-02-13)*
*v3 — 4-Step LLM フルフロー成功 + Cortex API 直叩き結果 + Python 実装完了 (2026-02-13)*
