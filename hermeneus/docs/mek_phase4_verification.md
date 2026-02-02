# [CCL]/mek+ Hermēneus Phase 4 — Formal Verification

---
sel:
  workflow: /mek+
  scope: P4=formal_verification
  output_format: CCL Skill Definition + Implementation Plan
  quality_gate: 
    - Multi-Agent Debate
    - 形式証明インターフェース
    - 検証可能な実行保証
---

## CCL シグネチャ

```ccl
/mek+ "Hermēneus Phase 4"
  [target: Formal Verification Layer]
  {
    /s1 "Multi-Agent Debate"  -- AIによる相互検証
    /s2 "Prover Interface"    -- 形式証明ツール連携
    /s3 "Confidence Scoring"  -- 検証スコア算出
    /s4 "Audit Trail"         -- 検証履歴記録
  }
  >> 形式的実行保証 ✅
```

---

## Phase 4 概要

| 属性 | 値 |
|:-----|:---|
| **目標** | LLM 出力の検証可能性を確立 |
| **成果物** | `verifier.py`, `prover.py`, `audit.py` |
| **依存** | `langchain`, `lean4` (オプション) |
| **検証** | Multi-Agent 一致率 >90% |

---

## 検証アーキテクチャ

```
                    ┌──────────────────────────────────────┐
                    │         CCL Execution Result         │
                    └────────────────┬─────────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
         ▼                           ▼                           ▼
   ┌───────────────┐         ┌───────────────┐         ┌───────────────┐
   │   Agent 1     │         │   Agent 2     │         │   Agent 3     │
   │  (Proposer)   │         │  (Critic)     │         │  (Arbiter)    │
   └───────┬───────┘         └───────┬───────┘         └───────┬───────┘
           │                         │                         │
           └─────────────────────────┼─────────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────┐
                    │         Consensus Engine             │
                    │    (Majority Vote + Confidence)      │
                    └────────────────┬─────────────────────┘
                                     │
          ┌──────────────────────────┴──────────────────────────┐
          │                                                     │
          ▼                                                     ▼
   ┌────────────────┐                                 ┌─────────────────┐
   │  Prover        │ (オプション)                    │   Audit Trail   │
   │  Interface     │                                 │   (SQLite)      │
   │ (Lean4/Dafny)  │                                 └─────────────────┘
   └────────────────┘
```

---

## 実装タスク CCL

```ccl
# Phase 4 タスクリスト
let phase_4_tasks = [
  /s1+ "Multi-Agent Debate" {
    DebateAgent クラス (Proposer, Critic, Arbiter)
    ConsensusEngine (多数決 + 確信度加重)
    ディベートラウンド管理
    反論生成ロジック
  }
  
  /s2+ "Prover Interface" {
    ProverInterface 抽象クラス
    Lean4Prover 実装 (オプション)
    DafnyProver 実装 (オプション)
    PythonTypeChecker (mypy 統合)
  }
  
  /s3+ "Confidence Scoring" {
    ConfidenceCalculator
    一致率スコア
    反論強度スコア
    最終確信度合成
  }
  
  /s4+ "Audit Trail" {
    AuditRecord データクラス
    AuditStore (SQLite)
    検証履歴クエリ
    レポート生成
  }
]

F:[phase_4_tasks]{/ene+} >> 全タスク完了
```

---

## コンポーネント設計

### DebateAgent

```ccl
/mek "DebateAgent"
  [input: Claim]
  [output: Response]
  {
    class AgentRole(Enum):
      PROPOSER = "proposer"   # 主張生成
      CRITIC = "critic"       # 批判・反論
      ARBITER = "arbiter"     # 最終判定
      
    class DebateAgent:
      role: AgentRole
      model: str
      
      def propose(claim: str) -> str:
        # 主張を支持する論拠を生成
        
      def critique(claim: str, argument: str) -> str:
        # 反論を生成
        
      def arbitrate(claim: str, for_args: List, against_args: List) -> Verdict:
        # 最終判定を下す
  }
```

### ConsensusEngine

```ccl
/mek "ConsensusEngine"
  [input: DebateResults]
  [output: Consensus + Confidence]
  {
    class ConsensusEngine:
      def reach_consensus(
        proposer_result: str,
        critic_results: List[str],
        arbiter_verdict: Verdict
      ) -> ConsensusResult:
        
        # 1. 多数決
        majority = count_agreement(...)
        
        # 2. 確信度加重
        weighted_score = calc_weighted_confidence(...)
        
        # 3. 最終判定
        return ConsensusResult(
          accepted=majority > threshold,
          confidence=weighted_score,
          dissent_reasons=collect_dissent(...)
        )
  }
```

### ProverInterface

```ccl
/mek "ProverInterface"
  [input: Claim + Code]
  [output: ProofResult]
  {
    class ProverInterface(ABC):
      @abstractmethod
      def verify(claim: str, code: str) -> ProofResult:
        pass
        
    class Lean4Prover(ProverInterface):
      # Lean 4 形式証明
      # 数学的性質の検証
      
    class PythonTypeProver(ProverInterface):
      # mypy 型チェック
      # 型安全性の検証
  }
```

### AuditStore

```ccl
/mek "AuditStore"
  [input: VerificationRecord]
  [output: Persistent Audit]
  {
    class AuditRecord:
      record_id: str
      ccl_expression: str
      execution_result: str
      debate_transcript: List[str]
      consensus: ConsensusResult
      prover_results: Optional[ProofResult]
      timestamp: datetime
      
    class AuditStore:
      # SQLite 永続化
      path: Path = ~/.hermeneus/audit/
      
      def record(audit: AuditRecord)
      def query(filters: Dict) -> List[AuditRecord]
      def generate_report(period: DateRange) -> Report
  }
```

---

## 実装ファイル

| ファイル | 役割 |
|:---------|:-----|
| `src/verifier.py` | [NEW] Multi-Agent Debate + Consensus |
| `src/prover.py` | [NEW] 形式証明インターフェース |
| `src/audit.py` | [NEW] 検証履歴永続化 |
| `src/__init__.py` | [MODIFY] v0.4.0 API 更新 |
| `tests/test_verifier.py` | [NEW] 検証テスト |

---

## 依存関係

```bash
# 必須
pip install langchain-core  # Agent 実行

# オプション (形式証明)
# lean4 のインストール (別途)
# dafny のインストール (別途)

# 型チェック
pip install mypy
```

---

## 使用例 (目標)

```python
from hermeneus.src import verify_execution, DebateEngine

# Multi-Agent Debate で検証
result = verify_execution(
    ccl="/noe+ >> V[] < 0.3",
    execution_output="分析結果: プロジェクトは成功する見込みが高い",
    debate_rounds=3
)

print(f"Consensus: {result.accepted}")
print(f"Confidence: {result.confidence:.2%}")
print(f"Dissent: {result.dissent_reasons}")

# 検証履歴クエリ
from hermeneus.src import query_audits

audits = query_audits(
    ccl_pattern="/noe*",
    min_confidence=0.8,
    period="last_7_days"
)
```

---

## ユースケース CCL

### 1. 高リスク決定の検証

```ccl
# 重要な決定は Multi-Agent Debate で検証
/ene+![verify(rounds=5, min_confidence=0.9)]

# 検証フロー
/ene+ → [Proposer: "実行すべき理由"]
      → [Critic: "リスクと反論"]
      → [Arbiter: "最終判定"]
      → ConsensusResult
```

### 2. 自動検証パイプライン

```ccl
# 収束ループ + 検証
(/noe+ >> V[] < 0.3)![auto_verify]

# 各反復で検証スコアを計算
iteration_1 → debate → confidence: 0.6
iteration_2 → debate → confidence: 0.8
iteration_3 → debate → confidence: 0.92 ✅ PASS
```

### 3. 形式証明 (高保証モード)

```ccl
# 数値計算の正確性を形式証明
/calc+![prove(lean4)]

# Lean 4 で数学的性質を検証
theorem calc_is_correct : ∀ x, f(x) > 0 := by
  ...
```

---

## メトリクス

| 指標 | 目標値 |
|:-----|:-------|
| Agent 一致率 | >90% |
| 誤判定率 (False Positive) | <5% |
| 検証オーバーヘッド | <2x 実行時間 |
| 監査カバレッジ | 100% (高リスク操作) |

---

## リスク分析 CCL

```ccl
/pre "Phase 4 Risks"
  {
    R1: Agent 間の無限ループ    -- 最大ラウンド数で強制終了
    R2: 形式証明の複雑性        -- オプション化 + Python型のみ必須
    R3: 検証コストが高い        -- キャッシュ + 閾値ベース実行
    R4: 偽の合意 (共謀)         -- 異なるモデル/プロンプトを使用
  }
  >> リスク緩和策実装
```

---

## 次ステップ

```ccl
# Phase 4 完了後 → Phase 5 (Production Ready)
/mek+ "Production Hardening"
  {
    API サーバー化
    キャッシング層
    モニタリング/ログ
    ドキュメント整備
  }
  _/ene+
```

---

*Generated: 2026-02-01 | Origin: /mek+ Hermēneus Phase 4*
