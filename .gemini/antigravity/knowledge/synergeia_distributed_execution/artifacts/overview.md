# Synergeia: Distributed Execution & Autonomous AI Infrastructure

## 1. 概要 (Vision)

**Synergeia (シナジーイア)** は、Hegemonikón の「頭脳」である認知制御言語 (CCL) を、複数の「手足」である AI スレッドへ分散して実行するためのアーキテクチャである。

- **目的**: 30分以上の「労働（Labor）」や 60 CP を超える複雑な推論を外部委譲し、メイン AI の認知負荷を軽減しつつ、大規模な成果を創出する。
- **哲学**: 認識の瞬発力（私）と、行動の持続力（外部スレッド）の分離。

---

## 2. 実行アーキテクチャ

### 2.1 スレッド構成 (Threads)

| カテゴリ | スレッド名 | 接続方式 | 得意な CCL |
|:---|:---|:---|:---|
| **Cognition** | Antigravity | Session | `/noe`, `/dia`, `/u`, `/bou` |
| **Research** | Perplexity API | REST | `/sop`, `/zet` |
| **Execution** | Claude Code | CLI | `/s`, `/ene`, `/mek` |
| **Context** | Gemini CLI | CLI | `/tek`, `/sta` |
| **Code Expansion** | Codex CLI | CLI | `/ene`, `/mek` |
| **Long-term** | OpenManus | Docker | 汎用 / 大規模 |
| **Nervous** | n8n / Zapier | Webhook | 自動化 / 同期 |

### 2.2 演算子マッピング

- `|>` (Pipeline): スレッド間での文脈リレー。
- `||` (Parallel): 独立した調査・実装の同時進行。
- `@thread[name]`: 特定スレッドへの強制割り当て。

---

## 3. 自律型インフラの研究成果

### 3.1 主要サービスの長時間実行機能 (2026)

| カテゴリ | サービス/機能 | 特徴 | 長時間実行限界 |
|:---------|:--------------|:-----|:---------------|
| **Anthropic** | Claude Agent SDK | セッション無制限、compaction 搭載 | **Unbound** |
| **Google** | Vertex AI Agent Engine | Memory Bank 統合によるメモリ自動管理 | **60 min+** |
| **Perplexity** | Deep Research API | リアルタイムWeb検索統合の非同期API | **30 min** |
| **Mistral** | Durable Execution | Temporal 基盤による自動状態復旧 | **High** |
| **Open Source**| OpenManus | Docker 隔離環境によるマルチエージェント基盤 | **Unbound** |

### 3.2 階層的認知キャッシュ (HCC)

推論の連続性とトークン効率を保つため、メモリを 3 層に階層化するパターンを推奨。

- **L1 (Immediate)**: アクティブなコンテキスト。
- **L2 (Episodic)**: セッション内履歴の要約。
- **L3 (Semantic)**: 永続的な知識ベース（Vector DB / Knowledge Items）。

---

## 4. 自動化戦略 (n8n/Zapier)

- **/boot 自動化**: 毎朝の Gnōsis 収集とサマリー生成。
- **/bye 自動化**: セッション終了時の Kairos 投入と統計集計。
- **/sop 外感化**: Slack/Discord 等からの直接調査リクエスト。

---

## 5. ロードマップ

1. [x] マルチスレッド・コーディネーター (`coordinator.py`) の確立。
2. [x] Claude / Gemini / Codex / Perplexity CLI/API 対応の完了。 ✅
3. [x] 実験 03: 3スレッド並列実行 (300 CP+ 規模) の成功。 ✅
4. [x] 実験 04: Codex CLI 統合と認証フローの確立。 ✅
5. [x] 実験 05: 4つの外部スレッド同時並列実行 (5スレッド体制) の成功。 ✅
6. [x] 2026-02-01: 長期記憶からの文脈復元と開発再開。 ✅
7. [x]- **Hermeneus Adapter**: 構造化出力・型検証を伴う実行を保証。v0.6.0 では WorkflowExecutor と統合され、バッチ実行をサポート。 ✅
8. [ ] n8n Server (GCP) の構築。
9. [ ] OpenManus (自宅PC) とのセキュアなトンネル確立。
10. [x] 実験 06: Hermeneus Phase 2 実装による「自己言及的開発」の成功。 ✅
11. [x] 実験 07: 「再帰的発見 (Recursive Discovery)」による Phase 3 コンテキストの完全復旧。 ✅

---
*Consolidated: 2026-02-01 | Synergeia Master Overview v2.1 | Context Recovery & Resumption Integrated*
