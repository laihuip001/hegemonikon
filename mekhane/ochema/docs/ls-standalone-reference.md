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

## 18. Project ID 傍受結果

### 試行と結果

| 方法 | 結果 |
|:-----|:-----|
| `state.vscdb` 全キー検索 | project/companion キーなし |
| `userStatusProtoBinaryBase64` デコード | モデル enum + プラン情報のみ |
| `GetUserStatus` API | project フィールドなし |
| `GetUserDefinedCloudaicompanionProject` 呼出 | 404 (LS 内部関数、非公開) |
| `GetSubscriptionStatus` / `OnboardUser` | エンドポイント不在 |
| LS プロセスメモリスキャン (226MB) | `projects/` パターン 0 件 |
| LLM 呼出中メモリスキャン | `cloudaicompanion` パターン 0 件 |

### 結論

Project ID は **Go ランタイムの GC 管理下のメモリ**にのみ存在。
文字列検索では捕捉不可能 (protobuf バイナリエンコード + Go 内部構造体)。

**LS 経由 4-Step フローが唯一の実用ルート** — Cortex 直叩きは **永久に不可能** ではないが、
proto descriptor の抽出 + mitmproxy による TLS 復号が必要で、投資対効果が低い。

---

## 19. 次のステップ

### 完了済み

1. ~~LS API 経由 LLM テキスト生成~~ → ✅
2. ~~Python ラッパー~~ → ✅ (antigravity_client.py)
3. ~~MCP 統合~~ → ✅ (cli.py → Ochēma MCP Server)
4. ~~別モデルテスト~~ → ✅ (5/8 成功)
5. ~~ストリーミング調査~~ → ✅ (ポーリング方式で実質完了)
6. ~~project ID 傍受~~ → ❌ (Go GC 管理下、断念)

### 残課題 (低優先度)

- **Extension Server モック**: 最小 HTTP OAuth → Standalone LS の認証解決
- **proto descriptor 抽出**: LS バイナリから FileDescriptorSet → grpcurl 正式呼出
- **ConnectRPC Python ライブラリ**: 真の SSE ストリーミング実装

---

*Created 2026-02-13 — Ochēma IDE Hack Series*
*v2 — Cloud Backend 認証フロー + LS API 141メソッド + 三層認証構造 (2026-02-13)*
*v3 — 4-Step LLM フルフロー成功 + Cortex API 直叩き結果 + Python 実装完了 (2026-02-13)*
*v4 — 別モデルテスト + ストリーミング調査 + project ID 傍受 + enum ID マッピング (2026-02-13)*
