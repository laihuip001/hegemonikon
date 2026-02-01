# 🔑 API キーリスト (移行用)

> **目的**: Windows 環境で設定が必要な API キー一覧
> **注意**: このファイルには実際のキーを記載しない

---

## 必須 API キー

| サービス | 環境変数 | 取得先 | 用途 |
|:---------|:---------|:-------|:-----|
| **Anthropic** | `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com/) | Claude API, /vet |
| **Google AI** | `GOOGLE_API_KEY` | [aistudio.google.com](https://aistudio.google.com/apikey) | Gemini API |
| **Perplexity** | `PERPLEXITY_API_KEY` | [perplexity.ai/settings](https://www.perplexity.ai/settings/api) | /sop 検索 |

---

## オプション API キー

| サービス | 環境変数 | 用途 |
|:---------|:---------|:-----|
| OpenAI | `OPENAI_API_KEY` | OpenManus, GPT-4o |
| GitHub | `GITHUB_TOKEN` | Codex, PR 自動化 |
| Semantic Scholar | `S2_API_KEY` | 論文検索 |

---

## ローカル (キー不要)

| サービス | 備考 |
|:---------|:-----|
| Ollama | `api_key = "ollama"` (ダミー) |
| ローカル Qwen | GPU で無限動作 |

---

## Windows 環境変数設定

```powershell
# システム環境変数に追加
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-...", "User")
[Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", "AIza...", "User")
[Environment]::SetEnvironmentVariable("PERPLEXITY_API_KEY", "pplx-...", "User")
```

または `.env` ファイル:

```
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
PERPLEXITY_API_KEY=pplx-...
```

---

*Created: 2026-02-01*
