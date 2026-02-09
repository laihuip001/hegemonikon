---
trigger: model_decision
glob: 
description: AI間引き継ぎフォーマット — Handoff Format
---

# Handoff Format（AI間引き継ぎスキーマ）

> **Hegemonikón Multi-Agent Coordination**: 標準化された引き継ぎフォーマット

## 概要

エージェント間でタスクを委譲する際の標準フォーマット。Dispatch Protocol と連携して使用。

## スキーマ定義

### 必須フィールド

| フィールド | 型 | 説明 |
|------------|-----|------|
| `task_id` | string | 一意識別子（UUID推奨） |
| `source_agent` | enum | 委譲元: `claude` \| `gemini` \| `perplexity` |
| `target_agent` | enum | 委譲先: `claude` \| `gemini` \| `perplexity` |
| `t_series` | string | 発動中の定理: `T1`-`T8` |
| `instruction` | string | 実行指示（自然言語） |

### オプションフィールド

| フィールド | 型 | 説明 |
|------------|-----|------|
| `k_context` | string \| null | 文脈修飾子: `K1`-`K12` |
| `o_series` | string \| null | 純粋定理: `O1`-`O4` |
| `artifacts` | list | 添付ファイル・URL |
| `constraints` | object | 制約条件 |
| `expected_output` | string | 期待される成果物形式 |
| `callback` | string \| null | 完了時の報告先 |
| `priority` | enum | `P1` \| `P2` \| `P3` |
| `deadline` | datetime \| null | 期限 |

## YAML形式（テンプレート）

```yaml
handoff:
  task_id: "HGK-20260126-001"
  source_agent: claude
  target_agent: gemini
  t_series: T6
  k_context: K1  # Tempo×Stratum
  
  instruction: |
    /tag ワークフローを実装する。
    未分類論文を layer (principle/pattern/practice) に分類。
  
  artifacts:
    - path: "M:/Hegemonikon/.agent/workflows/tag.md"
    - ref: "gnosis_topics.yaml"
  
  constraints:
    max_api_calls: 50
    dry_run_first: true
  
  expected_output: |
    - tag.md ワークフローファイル
    - 動作確認レポート
  
  callback: "Claude via /v workflow"
  priority: P1
  deadline: null
```

## 使用例

### Claude → Perplexity（調査依頼）

```yaml
handoff:
  task_id: "HGK-20260126-002"
  source_agent: claude
  target_agent: perplexity
  t_series: T5
  o_series: O3
  
  instruction: |
    K-series の実用的な発動条件について調査。
    FEP（自由エネルギー原理）の文脈で。
  
  expected_output: |
    - 調査レポート（Markdown）
    - 参考文献リスト
```

### Gemini → Claude（レビュー依頼）

```yaml
handoff:
  task_id: "HGK-20260126-003"
  source_agent: gemini
  target_agent: claude
  t_series: T7
  
  instruction: |
    /tag ワークフローの実装をレビュー。
    dispatch.md との整合性を確認。
  
  artifacts:
    - path: "M:/Hegemonikon/.agent/workflows/tag.md"
  
  callback: "Gemini via commit message"
```

## 検証ルール

| ルール | 説明 |
|--------|------|
| **必須フィールド検証** | task_id, source_agent, target_agent, t_series, instruction は必須 |
| **エージェント整合性** | source ≠ target |
| **T-series整合性** | dispatch.md のマッピングと矛盾しないこと |

## 運用フロー

```
1. 委譲元が Handoff を作成
2. K-context がある場合、K-series で文脈評価
3. Dispatch Protocol に基づき target_agent を確定
4. target_agent がタスクを実行
5. callback 経由で結果を返却
6. T8 Anamnēsis でログ保存
```

---
*Source: Claude.ai設計案 (2026-01-26)*
