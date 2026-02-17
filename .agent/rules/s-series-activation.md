---
trigger: model_decision
glob: 
description: S-series 様態定理の発動条件
---

# S-series（様態定理）発動条件

> **Hegemonikón S-series**: Schema（様態）— 方法論と品質の4定理
> **v1 (2026-02-15)**: 新設。24定理活用深化計画 Phase 1。

## 運用方針

**採用**: 「キーワード自動検出 + 明示的修飾子」方式

## 発動パターン

| パターン | 条件 | 例 |
|----------|------|-----|
| **明示的指定** | ユーザーが `/s{N}` で指定 | `/s2` = 方法論選択 |
| **キーワード自動検出** | 下記シグナルテーブルにマッチ | 「品質を測りたい」→ S3 提案 |
| **実装フェーズ** | コード実装中 | → S4 Praxis 提案 |

## キーワード自動検出テーブル

> **検出時の動作**: `[S-series 提案: S{N} {問い}]` を出力に付記する

| S定理 | 検出キーワード (日本語) | 検出キーワード (英語) |
|:------|:----------------------|:---------------------|
| **S1 Metron** | 測定, 指標, メトリクス, KPI, 数値, パフォーマンス | measure, metric, benchmark, performance |
| **S2 Mekhanē** | 方法, 手段, ツール, フレームワーク, やり方, 手順 | method, tool, framework, how-to, procedure |
| **S3 Stathmos** | 品質, 基準, レビュー, 評価基準, テスト, 検査 | quality, standard, review, criteria, assessment |
| **S4 Praxis** | 実践, 運用, デプロイ, 適用, ワークフロー | practice, deploy, apply, workflow, production |

## 自動発動ルール

```yaml
trigger:
  - type: keyword_match
    table: s_keyword_detection_table
    action: propose_s_series
    format: "[S-series 提案: S{N} — {問い}]"
  - type: phase_detection
    condition: implementation_phase
    action: propose_S4_praxis
  - type: review_context
    condition: code_review_or_quality_discussion
    action: propose_S3_stathmos
```

---
*v1 (2026-02-15) — 新設。theorem_recommender.py と連携*
