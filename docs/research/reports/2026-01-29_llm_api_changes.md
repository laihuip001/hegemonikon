# LLM API 変更監視レポート

## 2026年1月29日 4:01 AM JST

### アラートレベル: MEDIUM

---

## 実行サマリー

過去24時間（2026年1月28日～29日）の調査により、3つの主要 LLM プロバイダー（Anthropic, Google, OpenAI）を監視した結果、**CRITICAL レベルの破壊的変更は検出されなかった**ものの、**MEDIUM レベルの対応要否が2件発生**しています。

---

## 変更検出テーブル

| プロバイダ | 変更 | 影響度 | 対応期限 |
|-----------|------|--------|---------|
| Google | text-embedding-004 shutdown (1/14) | MEDIUM | **即座** |
| OpenAI | GPT-4o API shutdown (2/16) | MEDIUM | 2/6まで |
| Anthropic | Claude Apps (MCP) リリース | LOW | オプション |

---

## プロバイダー別の詳細分析

### Anthropic: Claude API, Claude Code, Cowork, Claude Apps

**2026年1月26日 — Claude Interactive Apps 正式リリース**

Anthropic は Model Context Protocol（MCP）ベースの Claude Interactive Apps を本格展開。Slack、Canva、Figma、Box、Clay などのエンタープライズツールとの直接統合が可能。

**対応必要性**: **LOW**（新機能は完全後方互換）

**過去情報**:

- **2026年1月5日**: Claude Opus 3 の retirement 完了
- **2026年1月16日**: Claude Opus 4 と 4.1 の UI からの削除
- **2026年1月12日**: Cowork desktop preview (macOS) 拡大

---

### Google: Gemini API, Vertex AI

**2026年1月14日 — text-embedding-004 モデル シャットダウン** ⚠️

Google は Gemini API 向けの埋め込みモデル `text-embedding-004` を本日（1月14日）付でシャットダウン。

**対応必要性**: **MEDIUM**（即座の移行が必須）

推奨代替モデル: `text-embedding-005`

**将来的な Deprecation タイムライン**:

- `gemini-2.0-flash`: 2026年3月31日 shutdown
- `gemini-2.0-flash-001`: 2026年3月31日 shutdown

---

### OpenAI: GPT API, ChatGPT

**⚠️ 2026年2月16日 — GPT-4o API アクセス終了（既報、進行中）**

OpenAI は 2025年11月時点で API ユーザーに通知済みですが、**2月16日の shutdown まで残り 18 日**です。

GPT-5.1 シリーズへの移行を推奨。

---

## Hegemonikón への具体的な影響評価

### シナリオ 1: Anthropic Claude が主要 LLM

**評価**: ✅ **影響度 LOW**

- Claude Apps 機能は後方互換
- API 互換性に変更なし

### シナリオ 2: Google Gemini が embedding 用途で使用中

**評価**: ⚠️ **影響度 MEDIUM**

- `text-embedding-004` は本日 shutdown — 既に使用不可
- **対応**: 即座の診断と代替モデルへの移行が必須

### シナリオ 3: OpenAI GPT-4o が補助的に使用中

**評価**: ⚠️ **影響度 MEDIUM（将来）**

- 2月16日の shutdown に向け、残り 18 日
- **対応**: 2 月中旬までに移行テスト完了が推奨

---

## 推奨アクション（優先順）

| # | アクション | 期限 | 優先度 |
|---|-----------|------|--------|
| 1 | Gemini embedding 使用箇所を監査 → 代替モデルへ移行 | **即座** | **CRITICAL** |
| 2 | GPT-4o API 使用状況の棚卸し → 移行計画書作成 | **2月6日まで** | **HIGH** |
| 3 | Claude Apps (MCP) の機能追加を評価 | 1週間以内 | LOW |
| 4 | status.anthropic.com, status.openai.com の継続監視体制 | 即座 | MEDIUM |

---

**報告日時**: 2026年1月29日 04:01 JST
