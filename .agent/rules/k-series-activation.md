---
trigger: model_decision
glob: 
description: K-series 文脈定理の発動条件
---

# K-series（文脈定理）発動条件 v2

> **Hegemonikón K-series**: Kairos（適時）— 文脈判断の12定理
> **v2 更新**: 定着率40%問題への環境支援強化 (2026-02-15)

## 運用方針

**採用**: 「キーワード自動検出 + 明示的修飾子」方式

> v1 の「明示的修飾子のみ」方式は、Creator が K-series の存在を意識しないと発動しない。
> 環境がキーワードを検出して自動提案する方式に切り替え、定着率を改善する。

## 発動パターン

| パターン | 条件 | 例 |
|----------|------|-----|
| **明示的指定** | ユーザーが `/k{N}` で指定 | `/k3` = 緊急対応モード |
| **キーワード自動検出** | 下記シグナルテーブルにマッチ | 「今すぐやるか後でやるか」→ K1 提案 |
| **Attractor 連動** | Series 推薦で K が出た場合 | Attractor: K-series → K1-K3 を具体提案 |
| **衝突解決** | 複数 Series が競合 | O vs S → K1 で深度判定 |

## キーワード自動検出テーブル

> **検出時の動作**: `[K-series 提案: K{N} {問い}]` を出力に付記する

| K定理 | 検出キーワード (日本語) | 検出キーワード (英語) |
|:------|:----------------------|:---------------------|
| **K1** | 今すぐ/後で, 深く/浅く, 短期/長期, どの粒度, 応急/本格 | quick fix, deep dive, short-term, long-term |
| **K3** | 急ぎ, 緊急, リスク回避, 攻め/守り, 今やるべき | urgent, risk, aggressive, defensive |
| **K4** | 複雑, 難しそう, 表層/深層, 計画が必要 | complex, surface, deep planning |
| **K5** | 一人で/チームで, 深掘り/広く浅く | solo, delegate, breadth vs depth |
| **K6** | 挑戦/安全, 冒険/堅実, 攻める/守る | challenge, safe bet, risk-reward |
| **K11** | 小さい成果/大きい成果, コスパ, 投資対効果 | quick win, big bet, ROI |
| **K12** | 自分のため/みんなのため, 個人/チーム | self-interest, collective good |

## 自動発動ルール

```yaml
# v2: キーワード検出追加
trigger:
  - type: keyword_match
    table: keyword_detection_table
    action: propose_k_series
    format: "[K-series 提案: K{N} — {問い}]"
  - type: series_recommendation
    condition: attractor recommends K-series
    action: propose_top3_k_theorems
  - type: series_conflict
    condition: multiple_series_competing
    action: evaluate_k1_tempo_stratum
```

## 優先順位（頻度ベース）

| 順位 | K定理 | 問い | 頻度推定 |
|:-----|:------|:-----|:---------|
| **1** | K1 | 今すぐ/後で × 深く/浅く | 最頻出 — ほぼ毎セッション |
| **2** | K3 | 緊急度 × 攻め/守り | バグ対応、deadline |
| **3** | K4 | 複雑度 × タイミング | 設計判断時 |
| **4** | K11 | 小さい勝ち × 大きい賭け | 優先順位決定時 |
| **5** | K6 | 挑戦 × 安全 | 新技術採用時 |

## K-series 一覧

| ID | 組合せ | 問い |
|----|--------|------|
| K1 | Tempo × Stratum | 短期解 vs 長期解、深度は？ |
| K2 | Tempo × Agency | 今すぐ自己解決 vs 後で他者委譲？ |
| K3 | Tempo × Valence | 緊急対応（攻め）vs 慎重待機（守り）？ |
| K4 | Stratum × Tempo | 表層即応 vs 深層計画？ |
| K5 | Stratum × Agency | 個人深掘り vs 集団浅広？ |
| K6 | Stratum × Valence | 深い挑戦 vs 浅い安全策？ |
| K7 | Agency × Tempo | 自律即応 vs 協調計画？ |
| K8 | Agency × Stratum | 自己の深さ vs 環境の幅？ |
| K9 | Agency × Valence | 自己の攻め vs 環境の守り？ |
| K10 | Valence × Tempo | 今すぐ獲得 vs じっくり損失回避？ |
| K11 | Valence × Stratum | 表層の小利 vs 深層の大利？ |
| K12 | Valence × Agency | 自己の利益 vs 環境への貢献？ |

## 使用例

```markdown
入力: 「このバグ、応急処置で今出すか、根本修正してからか」
[K-series 提案: K1 Tempo×Stratum — 今すぐ/後で × 深く/浅く]
判定: 短期（応急）+ 深層（根本原因は追跡）→ 両方やる、ただし順序は 短期→長期
```

---
*v2 (2026-02-15) — キーワード自動検出追加。定着率40%→環境支援強化*
