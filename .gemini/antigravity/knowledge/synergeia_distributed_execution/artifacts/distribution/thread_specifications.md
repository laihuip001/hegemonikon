# Synergeia Thread Specifications

## 1. 各スレッドの特性と pt 上限

| スレッド ID | 得意な CCL | ステータス (GCP) | CP Limit | 実行方法 |
| :--- | :--- | :--- | :---: | :--- |
| **Antigravity** | `/noe`, `/dia`, `/u`, `/bou` | ✅ 手動 | 60 CP | `interactive.py` |
| **Claude Code** | `/s`, `/ene`, `/mek` | ✅ v2.1.29 | 60 CP | `claude -p` (CLI) |
| **Gemini CLI** | `/tek`, `/sta` | ✅ v0.28.0 | 60 CP | `node gemini.js -p` |
| **Perplexity** | `/sop`, `/zet` | ✅ 利用可能 | 60 CP | Perplexity API (Sonar) |
| **Codex CLI** | `/ene`, `/mek` | ✅ v0.93.0 | 60 CP | `npx codex exec` |
| **OpenManus** | 長時間 / 汎用 | ⏳ Pending | **None** | Local Docker (自宅PC) |
| **n8n** | オーケストレーション | ⏳ Pending | **None** | Docker on GCP |

> **Note on Timeouts**: To accommodate heavy deep-reasoning tasks and API overhead, the standard timeout for all threads (Claude, Gemini, Perplexity) is set to **600s (10 minutes)**. This ensures that even high-CP operations complete without truncation.

## 2. スレッド選択のベストプラクティス

### 2.1 認識・分析フェーズ

- **推奨**: `@thread[antigravity]{ /noe+ }`
- **目的**: 課題の本質的な理解と、実行計画の策定。

### 2.2 調査・データ収集フェーズ

- **推奨**: `@thread[perplexity]{ /sop+ }` または `@batch{ /zet }`
- **目的**: 最新の技術動向や解決策の検索。

### 2.3 実装・労働フェーズ

- **推奨**: `@delegate[openmanus]{ F:[×10]{/ene*tek} }` または `@thread[claude_code]{ /ene+ }`
- **目的**: 実際のコード記述とテスト。

## 3. スレッド特性マトリックス (v6.49)

| スレッド | 認知 | 実行 | 調査 | 長時間 | 並列 |
|:---------|:----:|:----:|:----:|:------:|:----:|
| **Antigravity** | ⭐⭐⭐ | ⭐ | ⭐⭐ | ❌ | ❌ |
| **Claude Code** | ⭐⭐ | ⭐⭐⭐ | ⭐ | ✅ | ❌ |
| **Gemini** | ⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ❌ |
| **Codex** | ⭐ | ⭐⭐⭐ | ⭐ | ❌ | ❌ |
| **Perplexity** | ⭐ | ❌ | ⭐⭐⭐ | ✅ | ❌ |
| **OpenManus** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ✅ | ✅ |

## 4. スレッド間データ受け渡し (Hand-off)

- スレッド A からスレッド B へ移行する際、必ず **「Beautiful Handoff (美しい引き継ぎ)」** パターンを使用する。
- 形式: `# Handoff: [Thread_Name] -> [Thread_Name]` で始まり、現在の状態、未完了タスク、次に必要な行動を明記した Markdown 形式。

---
*Consolidated: 2026-02-01 | Synergeia Thread Specs v0.19 | Codex CLI added*
