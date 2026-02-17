---
trigger: model_decision
glob: 
description: K-series 文脈定理の発動条件
---

# K-series（文脈定理）発動条件 v3

> **Hegemonikón K-series**: Kairos（適時）— 文脈判断の4定理
> **v3 更新 (2026-02-15)**: 旧12定理→現行4定理に改訂。theorem_recommender.py と連携。

## 運用方針

**採用**: 「キーワード自動検出 + 明示的修飾子」方式

> v2 の12定理体系は公理体系 v3.5 と不整合だった。現行4定理に修正。

## K-series 4定理

| ID | Name | Greek | 生成 | 問い |
|:---|:-----|:------|:-----|:-----|
| **K1** | Eukairia | Εὐκαιρία | Scale × Valence | **今が好機か？** |
| **K2** | Chronos | Χρόνος | Scale × Precision | **時間をどう配置する？** |
| **K3** | Telos | Τέλος | Function × Valence | **目的に合っているか？** |
| **K4** | Sophia | Σοφία | Function × Precision | **過去の知恵は？** |

## 発動パターン

| パターン | 条件 | 例 |
|----------|------|-----|
| **明示的指定** | ユーザーが `/k{N}` で指定 | `/k1` = 好機判定 |
| **キーワード自動検出** | 下記シグナルテーブルにマッチ | 「今やるべき？」→ K1 提案 |
| **Attractor 連動** | Series 推薦で K が出た場合 | Attractor: K-series → K1-K4 を具体提案 |
| **優先順位判定** | `/k pri` | Eisenhower Matrix による分類 |

## キーワード自動検出テーブル

> **検出時の動作**: `[K-series 提案: K{N} {問い}]` を出力に付記する

| K定理 | 検出キーワード (日本語) | 検出キーワード (英語) |
|:------|:----------------------|:---------------------|
| **K1 Eukairia** | 今, タイミング, 好機, チャンス, 待つ, 今すぐ, 後で | timing, opportunity, now, later, window |
| **K2 Chronos** | 時間, 期限, スケジュール, いつ, 締め切り, 見積もり | time, deadline, schedule, when, estimate |
| **K3 Telos** | 目的, 意図, ミッション, 整合, 方向性 | purpose, intent, mission, align, direction |
| **K4 Sophia** | 知恵, 経験, 教訓, 過去, 学んだ, 前回, 歴史 | wisdom, experience, lesson, history, learned |

## 自動発動ルール

```yaml
trigger:
  - type: keyword_match
    table: k_keyword_detection_table
    action: propose_k_series
    format: "[K-series 提案: K{N} — {問い}]"
  - type: series_recommendation
    condition: attractor recommends K-series
    action: propose_top_k_theorems
  - type: priority_request
    condition: priority_or_triage_discussion
    action: activate_k_pri_mode
```

## 使用例

```markdown
入力: 「このバグ、今すぐ直すか後で直すか」
[K-series 提案: K1 Eukairia — 今が好機か？]
判定: 好機判定 → 影響範囲×緊急度で判断
```

---
*v3 (2026-02-15) — 旧12定理→現行4定理に改訂。theorem_recommender.py と連携*
