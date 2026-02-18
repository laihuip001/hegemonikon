---
trigger: model_decision
glob: 
description: P-series 環境配置定理の発動条件
---

# P-series（環境配置定理）発動条件

> **Hegemonikón P-series**: Perigraphē（条件）— 空間・経路・軌道・技術の4定理
> **v1 (2026-02-15)**: 新設。24定理活用深化計画 Phase 1。

## 運用方針

**採用**: 「キーワード自動検出 + 明示的修飾子」方式

## 発動パターン

| パターン | 条件 | 例 |
|----------|------|-----|
| **明示的指定** | ユーザーが `/p{N}` で指定 | `/p1` = 空間定義 |
| **キーワード自動検出** | 下記シグナルテーブルにマッチ | 「アーキテクチャ設計」→ P1 提案 |
| **計画フェーズ** | `/plan` 実行中 | → P2 Hodos + P3 Trokhia 提案 |
| **技術選定** | 新ツール/言語の議論中 | → P4 Tekhnē 提案 |

## キーワード自動検出テーブル

> **検出時の動作**: `[P-series 提案: P{N} {問い}]` を出力に付記する

| P定理 | 検出キーワード (日本語) | 検出キーワード (英語) |
|:------|:----------------------|:---------------------|
| **P1 Khōra** | 空間, スコープ, 境界, 範囲, 領域, アーキテクチャ | space, scope, boundary, domain, architecture |
| **P2 Hodos** | 経路, パス, 段階, ロードマップ, マイルストーン | path, route, step, roadmap, milestone, phase |
| **P3 Trokhia** | パターン, 軌道, サイクル, ループ, 傾向, トレンド | pattern, trajectory, cycle, loop, trend |
| **P4 Tekhnē** | 技術, テクノロジー, 言語, ライブラリ, スタック | technology, technique, stack, library, language |

## 自動発動ルール

```yaml
trigger:
  - type: keyword_match
    table: p_keyword_detection_table
    action: propose_p_series
    format: "[P-series 提案: P{N} — {問い}]"
  - type: planning_phase
    condition: plan_or_roadmap_discussion
    action: propose_P2_hodos
  - type: tech_decision
    condition: technology_selection_discussion
    action: propose_P4_tekhne
```

---
*v1 (2026-02-15) — 新設。theorem_recommender.py と連携*
