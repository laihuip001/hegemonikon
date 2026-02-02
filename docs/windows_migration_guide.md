# 🖥️ Windows PC 移行ガイド

> **対象環境**: Windows + RTX 2070 Super (8GB VRAM)
> **目的**: ローカル LLM + Synergeia 基盤構築
> **作成日**: 2026-02-01

---

## 1. 環境概要

```
┌─────────────────────────────────────────────────────┐
│  自宅 PC (Windows)                                  │
│  ├── GPU: RTX 2070 Super (8GB)                      │
│  ├── Ollama: ローカル LLM サーバー                  │
│  └── Synergeia: 5スレッド Coordinator               │
│       ├── T1: Gemini (API)                          │
│       ├── T2: Claude (API)                          │
│       ├── T3: Perplexity (API)                      │
│       ├── T4: OpenManus + Qwen 7B (ローカル) ←NEW   │
│       └── T5: Codex (API)                           │
└─────────────────────────────────────────────────────┘
```

---

## 2. セットアップ手順

### Step 1: Ollama インストール

```powershell
# winget でインストール
winget install Ollama.Ollama

# または公式サイトから
# https://ollama.com/download/windows
```

### Step 2: Qwen 2.5 7B ダウンロード

```powershell
# モデル取得 (~4GB)
ollama pull qwen2.5:7b

# 動作確認
ollama run qwen2.5:7b "こんにちは"

# API 確認 (別ターミナル)
curl http://localhost:11434/api/generate -d '{"model":"qwen2.5:7b","prompt":"Hello"}'
```

### Step 3: 自動起動設定

```powershell
# タスクスケジューラで起動時に実行
# コマンド: ollama serve
```

---

## 3. Synergeia 統合

### 3.1 新スレッド定義

```python
# synergeia/thread_config.py

THREAD_LOCAL_LLM = {
    "name": "LocalLLM",
    "type": "ollama",
    "base_url": "http://localhost:11434/v1",
    "model": "qwen2.5:7b",
    "capabilities": ["reasoning", "coding", "japanese"],
    "cost": 0,  # 無料
    "latency": "medium",
    "availability": "24/7",
}
```

### 3.2 Coordinator 拡張

```python
# synergeia/coordinator.py に追加

class OllamaAdapter:
    """ローカル LLM アダプター"""
    
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        self.model = "qwen2.5:7b"
    
    async def query(self, prompt: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=120,
            )
            return response.json()["response"]
```

### 3.3 OpenManus 設定

```toml
# OpenManus/config/config.toml

[llm]
model = "qwen2.5:7b"
base_url = "http://localhost:11434/v1"
api_key = "ollama"
max_tokens = 4096
temperature = 0.0
```

---

## 4. GPU メモリ管理

### 推奨設定

```powershell
# 環境変数 (省メモリモード)
set OLLAMA_NUM_PARALLEL=1
set OLLAMA_MAX_LOADED_MODELS=1
```

### VRAM 使用量

| モデル | 量子化 | VRAM | 余裕 |
|:-------|:-------|:-----|:-----|
| Qwen 2.5 7B | Q4_K_M | ~5GB | 3GB |
| LLaMA 3 8B | Q4_K_M | ~5.5GB | 2.5GB |
| Phi-3 Mini | Q4_K_M | ~3GB | 5GB |

---

## 5. 検証チェックリスト

- [ ] Ollama 起動確認 (`ollama serve`)
- [ ] Qwen 2.5 7B 応答確認
- [ ] OpenManus 動作確認
- [ ] Synergeia Coordinator 統合テスト
- [ ] 24時間連続稼働テスト

---

## 6. トラブルシューティング

| 症状 | 対処 |
|:-----|:-----|
| CUDA エラー | NVIDIA ドライバ更新 |
| OOM (メモリ不足) | Q4_K_S 量子化に変更 |
| レスポンス遅い | `OLLAMA_NUM_GPU=999` で GPU フル活用 |

---

## 7. 関連ファイル

- `experiments/activation_steering_mvp.ipynb`
- `experiments/openmanus_mvp.ipynb`
- `docs/gpu_required_tasks.md`

---

*Ready for Windows migration! 🚀*
