# K-series（文脈定理）発動条件

> **Hegemonikón K-series**: Kairos（適時）— 選択公理×選択公理 = 12文脈定理

## 運用方針

**採用**: 「明示的修飾子」方式（暗黙的発動より予測可能性を優先）

## 発動パターン

| パターン | 条件 | 例 |
|----------|------|-----|
| **明示的指定** | ユーザーが `/k{N}` で指定 | `/k3` = 緊急対応モード |
| **自動修飾** | T-series発動時 `context_ambiguity > 0.5` | T6発動 → 「短期/長期？」→ K4判定 |
| **衝突解決** | 複数T-seriesが競合 | T2 vs T4 → K1でTempo×Stratum評価 |

## 自動発動ルール

```yaml
trigger: T-series_invocation
condition: context_ambiguity > 0.5
action: evaluate_relevant_k_series
max_k_series: 2  # 最大2つまで同時評価
```

## 優先実装順序

| 優先度 | K-series | 組合せ | 理由 |
|--------|----------|--------|------|
| **1** | K1 | Tempo × Stratum | 「今すぐ/後で」「深く/浅く」の判断が最頻出 |
| **2** | K3 | Tempo × Valence | 「今すぐ + 接近/回避」緊急度判定 |
| **3** | K4 | Stratum × Tempo | 「深さ + タイミング」複雑度判定 |

## K-series一覧（参照）

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
[Hegemonikon] K1 Tempo×Stratum
  入力: T6 Praxis発動、文脈曖昧
  判定: 短期実装（Tempo=F）+ 表層対応（Stratum=L）
  結論: クイックフィックスを適用、後でリファクタリング
```

---
*Source: Perplexity調査 (2026-01-25) + Claude.ai提案*
