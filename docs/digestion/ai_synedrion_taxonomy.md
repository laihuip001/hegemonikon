# AI Synedrion 評価軸 (AI-001 〜 AI-022)

> **Generated**: 2026-02-01 10:35 JST
> **Source**: 43 AI-Risk PRs from Jules Synedrion
> **Integration Target**: A2 Krisis (判定力) 派生

---

## 📊 概要

Jules Synedrion は **22種類の AI リスク検出パターン** を定義している。
これらは A2 Krisis の派生モードとして Hegemonikón に統合可能。

---

## 🔍 AI リスク検出パターン一覧

### Category: 幻覚系 (Hallucination)

| Code | 名称 | 検出対象 | 重大度 |
|:-----|:-----|:---------|:------:|
| AI-001 | Naming Hallucination | 存在しないライブラリ/関数への参照 | High |
| AI-002 | Mapping Hallucination | 無効な API メソッド呼び出し | High |
| AI-003 | Resource Hallucination | 架空の URL/エンドポイント | Critical |
| AI-004 | Logic Hallucination | 到達不能なコードパス | High |

> **CCL 統合**: `/dia --mode=hallu` として一括検出

---

### Category: コード品質系 (Code Quality)

| Code | 名称 | 検出対象 | 重大度 |
|:-----|:-----|:---------|:------:|
| AI-005 | Incomplete Code | 未完成のロジック (pass, TODO) | Medium |
| AI-006 | DRY Violation | コードの重複 | Medium |
| AI-007 | Pattern Inconsistency | スタイルの不統一 | Low |
| AI-013 | Style Inconsistency | スタイルの不統一（詳細版） | Low |
| AI-014 | Excessive Comment | 冗長なコメント | Low |
| AI-015 | Copy-Paste Trace | コピペの痕跡 | Medium |
| AI-016 | Dead Code | 使われていないコード | Medium |
| AI-017 | Magic Number | ハードコードされた数値 | Low |
| AI-018 | Hardcoded Path | ハードコードされたパス | Medium |

> **CCL 統合**: `/dia --mode=quality` として一括検出

---

### Category: ロジック系 (Logic)

| Code | 名称 | 検出対象 | 重大度 |
|:-----|:-----|:---------|:------:|
| AI-008 | Self-Contradiction | 矛盾するロジック | High |
| AI-010 | Input Validation Omission | 入力検証の欠如 | High |
| AI-011 | Over-Optimization | 過剰最適化 | Medium |
| AI-012 | Context Loss | 文脈の消失 | High |
| AI-019 | Implicit Type Conversion | 暗黙の型変換 | Medium |

> **CCL 統合**: `/dia --mode=logic` として一括検出

---

### Category: 安全性系 (Safety)

| Code | 名称 | 検出対象 | 重大度 |
|:-----|:-----|:---------|:------:|
| AI-009 | Security Vulnerabilities | CWE ベースの脆弱性 | Critical |
| AI-020 | Exception Swallowing | 例外の握り潰し | High |
| AI-021 | Resource Leak | リソースリーク | High |
| AI-022 | Race Condition | 競合状態 | Critical |

> **CCL 統合**: `/dia --mode=safety` として一括検出

---

## 📐 A2 Krisis への統合仕様

### 新規派生モード

```yaml
# .agent/workflows/dia.md への追加

--mode=ai-audit:
  description: AI Synedrion 22軸による AI リスク監査
  ccl_signature: /dia --mode=ai-audit @F:[AI-*]{check}
  sub_modes:
    - hallu: AI-001〜AI-004 幻覚検出
    - quality: AI-005〜AI-018 コード品質
    - logic: AI-008〜AI-019 ロジック整合性
    - safety: AI-009〜AI-022 安全性
```

### CCL 表現

```ccl
# 単一ファイルへの AI 監査
[jules_client.py]/dia --mode=ai-audit

# 特定カテゴリのみ
[jules_client.py]/dia --mode=hallu

# 全ファイルへの安全性監査
F:[*.py]/dia --mode=safety
```

---

## 🎯 優先実装順序

1. **Critical (即時対応)**: AI-003, AI-009, AI-022
2. **High (優先対応)**: AI-001, AI-002, AI-004, AI-008, AI-010, AI-012, AI-020, AI-021
3. **Medium (通常対応)**: AI-005, AI-006, AI-011, AI-015, AI-016, AI-018, AI-019
4. **Low (低優先)**: AI-007, AI-013, AI-014, AI-017

---

## 📚 参照

- `/dia` ワークフロー: `.agent/workflows/dia.md`
- A2 Krisis 定理: Hegemonikón Core Theorems
- Synedrion 基盤: `mekhane/ergasterion/synedrion/`

---

*Extracted from 43 AI-Risk PRs as part of Jules Perspectives Digestion Phase 2*
