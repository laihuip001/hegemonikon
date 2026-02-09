---
trigger: model_decision
glob: 
description: Dispatch Protocol — 静的ルール Phase A
---

# Dispatch Protocol（静的ルール Phase A）

> **Hegemonikón Multi-Agent Coordination**: T-series → Agent Mapping

## 概要

マルチAI環境において、どの定理（T-series/O-series）をどのエージェントに委譲するかを定義する静的ルール。

## ディスパッチルール

### T-series マッピング

| T-series | Default Agent | Fallback | 条件 |
|----------|---------------|----------|------|
| **T1 Aisthēsis** | Claude | - | 知覚・初期分析 |
| **T2 Krisis** | Claude | - | 判断・優先順位決定 |
| **T3 Theōria** | Claude | - | 内省・自己モデル更新 |
| **T4 Phronēsis** | Claude | Gemini | 戦略策定・計画立案 |
| **T5 Peira** | Perplexity | Claude | 情報収集・Web検索 |
| **T6 Praxis** | Gemini | Claude | ファイル操作・コード実行 |
| **T7 Dokimē** | Claude | Gemini | 検証・仮説確認 |
| **T8 Anamnēsis** | Claude | - | 記憶・長期保存 |

### O-series マッピング

| O-series | Default Agent | 理由 |
|----------|---------------|------|
| **O1 Noēsis** | Claude | メタ認知・深い認識 |
| **O2 Boulēsis** | Claude | 意志・目的設定 |
| **O3 Zētēsis** | Perplexity | 探求・調査依頼 |
| **O4 Energeia** | Gemini | 行為・実行 |

## YAML形式（プログラム参照用）

```yaml
dispatch_rules:
  t_series:
    T1_Aisthesis:
      default: claude
      fallback: null
      
    T2_Krisis:
      default: claude
      fallback: null
      
    T3_Theoria:
      default: claude
      fallback: null
      
    T4_Phronesis:
      default: claude
      fallback: gemini
      
    T5_Peira:
      default: perplexity
      fallback: claude
      
    T6_Praxis:
      default: gemini
      fallback: claude
      
    T7_Dokime:
      default: claude
      fallback: gemini
      
    T8_Anamnesis:
      default: claude
      fallback: null

  o_series:
    O1_Noesis:
      default: claude
      
    O2_Boulesis:
      default: claude
      
    O3_Zetesis:
      default: perplexity
      
    O4_Energeia:
      default: gemini
```

## エージェント特性

| Agent | 強み | 弱み | 主担当 |
|-------|------|------|--------|
| **Claude** | 設計・分析・判断・内省 | 外部情報アクセス | T1-T4, T7-T8, O1-O2 |
| **Gemini (Jules)** | コード実行・ファイル操作 | 深い分析 | T6, O4 |
| **Perplexity** | Web検索・最新情報収集 | 実行能力なし | T5, O3 |

## 使用例

```markdown
[Hegemonikon] Dispatch
  発動: T5 Peira（情報収集）
  判定: default → Perplexity
  アクション: /zet で調査依頼書を作成し、Perplexityに委譲
```

## Phase B 移行条件

| 条件 | 閾値 | 現状 |
|------|------|------|
| 運用実績 | 50回以上 | 未計測 |
| 失敗率 | <10% | N/A |
| 例外パターン | 3種以上蓄積 | 0 |

Phase B では K-series 評価結果に基づく動的ディスパッチを導入予定。

---
*Source: Claude.ai設計案 (2026-01-26)*
