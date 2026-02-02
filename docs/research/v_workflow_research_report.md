# LLM間マルチエージェント監査・品質管理アーキテクチャ

> **調査日**: 2026-01-23
> **調査者**: Perplexity (パプ君)
> **目的**: /v コマンド設計のための基礎調査

---

## エグゼクティブサマリー

Gemini（実行）+ Claude（監査）の協調体制は、マルチエージェント監査フレームワークの確立によって初めて実現可能である。2024-2026年の学術研究と実践事例から、**監査成功の鍵は「役割分担の明確化」「エラー伝播の早期検出」「エッジレベル干渉」の3層構造**にある。同一モデル内の自己監査は信頼性が低く（false negative rate 高い）、異なるモデル家族による Cross-Model Verification が効果的（幻覚検出で最大35%改善）。実装上、監査プロセスは **Sequential（直列）+ Hierarchical（階層管理）+ Debate（相互検証）** の複合型が最適であり、具体的な監査チェックリスト、SOP テンプレート、エラー分類フレームワークの導入が必須。

---

## 1. マルチエージェント協調パターン

### 1-1. 基本パターン比較表

| パターン | 構造 | Gemini向き | Claude向き | 監査適性 |
|---------|------|----------|----------|--------|
| **Sequential (直列)** | A→B→C直列処理 | ◎ | △ | ☆☆ |
| **Parallel (並列)** | A/B/C同時＋合議 | △ | ◎ | ☆☆☆ |
| **Hierarchical (階層)** | Manager→Worker | △ | ◎ Manager役 | ☆☆☆☆ |
| **Debate (対話/相互検証)** | 複数視点議論 | ◎ 主張側 | ◎ 批判側 | ☆☆☆☆☆ |

**実装推奨**: Sequential → Hierarchical → Debate の複合型

### 1-2. Gemini + Claude の役割分担根拠

| モデル | 強み | 弱み | 推奨役割 |
|--------|------|------|----------|
| **Gemini** | 1M トークン処理、並列化 | ルール遵守率低、指示忘れ | 実行エージェント |
| **Claude** | ルール遵守、推論深度、安全性 | 200K 上限、Middle Lost | 監査エージェント |

---

## 2. 監査構成要素フレームワーク

### 2-1. 監査対象の4層分類

| 層 | 監査対象 | Claude検証項目 |
|---|---------|--------------|
| **成果物正確性** | 出力の事実性・完全性 | スキーマ一致、数値妥当性、引用根拠 |
| **プロセス遵守** | 手順厳密実行 | 指示忘れ検出、スキップ検出 |
| **計画一致** | 要求仕様への準拠 | SLA達成、スコープ逸脱検出 |
| **品質基準** | 非機能要件 | レイテンシ、エラーハンドリング |

### 2-2. 監査報告の重大度分類

| 重大度 | 定義 | 対応 |
|------|------|------|
| **Critical** | システム停止/データ破損/規制違反 | 即座にロールバック、エスカレーション |
| **Major** | 機能部分的障害/品質低下 | 是正案提示、再実行要求 |
| **Minor** | スタイル/最適化問題 | 記録のみ、次回改善提案 |

---

## 3. Self-Critique の限界と Cross-Model Verification

### 3-1. Self-Critique が失敗する理由

- **False Negative Rate 高い**: GPT-4 でも 21% の指示違反を自己検証できない
- **多数決で性能低下**: Self-Critique ループ回数増加 → 正答率低下
- **Conformity Bias**: モデルは自分の前の回答を「支持」しやすい

### 3-2. Cross-Model Verification の優位性

- 異なる家族のモデルによる検証で信頼性向上
- Claude が Gemini 出力の幻覚検出で **92.6% 精度**
- Debate 方式で **最大 35% 精度改善**

---

## 4. エラー伝播とエッジレベル干渉

### 4-1. エラータイプ分類（AgentAsk 研究）

| エラータイプ | 割合 | Claude 検証方法 |
|-----------|------|--------------|
| **Signal Corruption** | 36.8% | スキーマ検証、型チェック |
| **Referential Drift** | 27.3% | 意味的同一性検証 |
| **Data Gap** | 29.1% | 入力チェックリスト検証 |
| **Capability Gap** | 6.8% | 能力マッチング検証 |

### 4-2. 早期検出アーキテクチャ

```
Gemini (Executor)
    ↓ [出力]
    ├─ Schema Validator (Claude: 自動)
    ├─ Semantic Validator (Claude: 意味チェック)
    └─ Capability Matcher (Claude: 次エージェント対応可否)
        ↓
        ├─ PASS → 次ステップ
        ├─ FAIL (Minor) → 自動修正提案
        └─ FAIL (Critical) → エスカレーション
```

---

## 5. SOP 設計原則（LLM 向け最適化）

### 5-1. 4原則

| 原則 | 実装 |
|-----|------|
| **曖昧性排除** | 選択肢は全て列挙、数値範囲明示 |
| **条件の明示化** | IF-THEN ロジックを論理記号で表現 |
| **成功基準の定量化** | 定性的評価を排除 |
| **エラーハンドリングの明記** | 例外ケースを全て列挙 |

---

## 6. 実装推奨ワークフロー

```
User Input
    ↓
[Gemini Task]
    ↓
[Claude Audit - Level 1: Schema]
    ├→ ✗ FAIL → [Error Correction]
    └→ ✓ PASS
         ↓
[Claude Audit - Level 2: Business Logic]
    ├→ ✗ FAIL (Minor) → [Auto-Correction]
    ├→ ✗ FAIL (Major) → [Debate Mode]
    └→ ✓ PASS
         ↓
[Final Output + Audit Trail Log]
```

---

## 7. 監査チェックリストテンプレート

```
□ 入力スキーマ妥当性（必須パラメータ存在、型一致）
□ 出力スキーマ妥当性（JSON構造、必須フィールド）
□ 指示遵守（Task A → B → C 順序厳密）
□ エラーハンドリング（例外ケース処理）
□ 引用・根拠提示（事実系出力の場合）
```

---

## 8. 主要参照文献

- Multi-Agent Collaboration Mechanisms Survey (arXiv 2025-01-09)
- AgentAsk: Multi-Agent Systems Need to Ask (arXiv 2025-05-09)
- Free-MAD: Consensus-Free Multi-Agent Debate (arXiv 2025-09-13)
- Chain-of-Agents (Google Research, 2026-01-12)

---

*この調査結果は /v ワークフロー設計の基礎資料として使用する。*
