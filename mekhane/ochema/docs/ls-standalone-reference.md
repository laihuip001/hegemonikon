# LS Standalone Boot — Complete Reference

> **Date**: 2026-02-13 | **Status**: 実証済み (ローカル機能), 未達成 (LLM 推論)

---

## 1. バイナリ情報

| 項目 | 値 |
|:-----|:---|
| パス | `/usr/share/antigravity/resources/app/extensions/antigravity/bin/language_server_linux_x64` |
| 依存 | libresolv, libpthread, libm, libdl (標準Linux) — 自己完結 |
| RSS | ~3 GB (起動後) |
| 内部名 | `jetski` (Google 内部PJ名) |

---

## 2. stdin Metadata Proto

LS は起動時に stdin から **protobuf バイナリ** (`exa.codeium_common_pb.Metadata`) を読取る。
Go: `setUpMetadataProvider()` (server.go:353) → `io.ReadAll(stdin)` → `proto.Unmarshal()`

### フィールド定義

| # | 名前 | 型 | 必須 | 用途 |
|:--|:-----|:---|:----:|:-----|
| 1 | `ide_name` | string | ✅ | `"antigravity"` |
| 7 | `ide_version` | string | ✅ | `"1.99.0"` |
| 12 | `extension_name` | string | — | `"google.antigravity"` |
| 2 | `extension_version` | string | ✅ | `"1.27.0"` |
| 17 | `extension_path` | string | — | 拡張機能パス |
| 4 | `locale` | string | — | `"ja"` |
| 5 | `os` | string | — | `"linux"` |
| 8 | `hardware` | string | — | HW 情報 |
| 10 | `session_id` | string | — | 任意 |
| 24 | `device_fingerprint` | string | — | — |
| 29 | `user_tier_id` | string | — | — |
| 3 | `api_key` | string | — | Codeium 旧 API キー |
| 6 | `disable_telemetry` | bool | — | テレメトリ無効化 |
| 18 | `user_tags` | string[] | — | repeated |

### Python 生成スクリプト

```python
import io

def varint(v):
    d = []
    while v > 0x7f: d.append((v & 0x7f) | 0x80); v >>= 7
    d.append(v)
    return bytes(d)

def string(fn, v):
    tag = (fn << 3) | 2
    e = v.encode('utf-8')
    return varint(tag) + varint(len(e)) + e

def boolean(fn, v):
    return varint((fn << 3) | 0) + varint(1 if v else 0)

buf = io.BytesIO()
buf.write(string(1, 'antigravity'))
buf.write(string(7, '1.99.0'))
buf.write(string(12, 'google.antigravity'))
buf.write(string(2, '1.27.0'))
buf.write(string(4, 'ja'))
buf.write(string(5, 'linux'))
buf.write(string(10, 'standalone-session'))
buf.write(boolean(6, True))

with open('/tmp/ls_metadata.bin', 'wb') as f:
    f.write(buf.getvalue())
```

---

## 3. 起動コマンド

```bash
cat /tmp/ls_metadata.bin | \
  language_server_linux_x64 \
  --standalone=false \
  --enable_lsp=false \
  --csrf_token="my-csrf-token" \
  --server_port=55900 \
  --workspace_id=standalone_test \
  --cloud_code_endpoint=https://daily-cloudcode-pa.googleapis.com \
  --app_data_dir=antigravity
```

### 全フラグ

| フラグ | デフォルト | 説明 |
|:-------|:----------|:-----|
| `--standalone` | `false` | `true` で即 exit 0。**`false` を使う** |
| `--server_port` | `42100` | HTTPS リスニングポート |
| `--csrf_token` | `""` | X-Codeium-Csrf-Token 値 |
| `--workspace_id` | `""` | ワークスペース ID |
| `--enable_lsp` | `false` | LSP 有効化 |
| `--extension_server_port` | `0` | IDE extension server |
| `--cloud_code_endpoint` | `""` | Cloud Code API |
| `--app_data_dir` | `"antigravity"` | データ dir |
| `--parent_pipe_path` | `""` | 親プロセス死活監視パイプ |

---

## 4. API 通信

### 認証ヘッダー

```
Content-Type: application/json
X-Codeium-Csrf-Token: {csrf_token}
Connect-Protocol-Version: 1
```

### エンドポイント動作結果

| エンドポイント | 結果 | OAuth必要 |
|:---|:---|:---:|
| `StartCascade` | ✅ `{"cascadeId":"uuid"}` | ❌ |
| `GetUserMemories` | ✅ 全メモリ返却 | ❌ |
| `GetAllCascadeTrajectories` | ✅ `{}` | ❌ |
| `InitializeCascadePanelState` | ✅ `{}` | ❌ |
| `GetModelStatuses` | ✅ `{}` | ❌ |
| `GetUserStatus` | ❌ 500 OAuth失敗 | ✅ |
| `SendUserCascadeMessage` | ❌ 500 model not found | ✅ |

### 全 LS RPC メソッド

```
LanguageServerService/
  StartCascade, SendUserCascadeMessage,
  GetAllCascadeTrajectories, GetCascadeTrajectorySteps,
  GetCascadeModelConfigData, GetStaticExperimentStatus,
  GetUserMemories, GetCascadeMemories, GetUserStatus, GetModelStatuses,
  InitializeCascadePanelState,
  StreamCascadePanelReactiveUpdates, StreamCascadeReactiveUpdates,
  StreamCascadeSummariesReactiveUpdates,
  GetCascadeTrajectoryGeneratorMetadata,
  HandleCascadeUserInteraction, GetMatchingContextScopeItems,
  ProvideCompletionFeedback, RecordChatFeedback,
  DumpFlightRecorder, CancelCascadeSteps, GetMcpServerStates,
  SetBaseExperiments, CaptureConsoleLogs,
  DeleteQueuedUserInputStep, AcknowledgeCodeActionStep,
  ConvertTrajectoryToMarkdown, ReplayGroundTruthTrajectory,
  GetBrowserWhitelistFilePath, GetAllBrowserWhitelistedUrls
```

---

## 5. Extension Server

| 項目 | 値 |
|:-----|:---|
| プロセス | Electron メイン (PID 899921) |
| プロトコル | **HTTP** (not HTTPS) |
| ポート | 動的 (例: 34045) |
| 認証 | CSRF トークン (IDE LS と共通) |

### RPC メソッド (全て 200 確認済み)

```
ExtensionServerService/
  LanguageServerStarted, StoreSecretValue, RunExtensionCode,
  GetChromeDevtoolsMcpUrl, WriteCascadeEdit, RemoveAnnotation,
  ShowTerminal, OpenTerminal, ReadTerminal, SaveDocument, TerminateCommand
```

---

## 6. OAuth クレデンシャル

### 保存場所: `~/.gemini/oauth_creds.json` (権限 0600)

```json
{
  "access_token": "ya29.xxxxx",
  "scope": "cloud-platform userinfo.email userinfo.profile openid",
  "token_type": "Bearer",
  "id_token": "eyJhbGcixxxx",
  "expiry_date": 1770965564651,
  "refresh_token": "1//0exxxxx"
}
```

| トークン | 有効期限 | 更新 |
|:---------|:---------|:-----|
| `access_token` | ~1 時間 | `refresh_token` で自動更新 |
| `refresh_token` | 永続 (~半年) | Google OAuth2 標準 |

---

## 7. アーキテクチャ図

```
Electron Main (PID 899921)
├─ Extension Server (HTTP :34045) ─── CSRF認証
│   ├─ OAuth Token Provider
│   └─ Terminal/Editor 統合
├─ ~/.gemini/oauth_creds.json 管理
│
└─► Language Server (Go binary)
    ├─ stdin: Metadata protobuf
    ├─ HTTPS :server_port (ConnectRPC)
    ├─ ローカル機能 (認証不要): Cascade, Memories
    └─ LLM 推論 (OAuth 必要) → Cloud Code API
```

---

## 8. 攻撃ベクトル

| Vector | 方法 | 結果 |
|:-------|:-----|:-----|
| A: strace | LS write syscall 傍受 | ❌ TLS暗号化で不可視 |
| B: Ext Server CSRF | IDE CSRF で直叩き | ✅ 認証通過、全RPC 200 |
| C: oauth_creds.json | ファイル直接読取 | ✅ access/refresh token 取得 |
| D: Cloud Code 直接 | access_token で API 直叩き | 🔜 未検証 |

---

## 9. 実験ログ

| stdin | バイト数 | 結果 |
|:------|:---------|:-----|
| `printf ''` | 0 | `read initial metadata: <nil>` |
| `echo ""` | 1 (`\n`) | `cannot parse invalid wire-format` |
| `\x00` | 1 | `cannot parse invalid wire-format` |
| Python protobuf | 79 | ✅ **起動成功** |

---

## 10. 次のステップ

1. **oauth_creds.json → Cloud Code API 直接呼出**
2. **Extension Server モック**: 最小 HTTP で OAuth 提供
3. **Metadata api_key に access_token 注入**
4. **OIKOS App 統合**: Claude API 直接 + LS ローカル hybrid

---

*Created 2026-02-13 — Ochēma IDE Hack Series*
