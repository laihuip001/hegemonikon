# Zero-Trust CCL Executor 実装計画

> **目的**: LLM の論外処理 (ドキュメント未読・省略・怠惰) を構造的に解消
> **対象**: Hegemonikón CCL 実行

---

## 5段階アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                    CCL Expression Input                      │
│                  @repeat(/noe!~/u+, x2)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 0: 仕様強制注入                                        │
│  • operators.md を自動読み込み                               │
│  • 演算子クイズ: 「! の意味は？」                            │
│  • 理解証明を出力に含める                                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: 出力構造強制                                        │
│  • Pydantic スキーマで型安全                                 │
│  • 演算子別必須セクション                                    │
│  • min_tokens=500 で省略防止                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: 出力検証                                            │
│  • NeMo Guardrails でルール検証                              │
│  • 違反時は理由付きリジェクト                                │
│  • 自動再生成ループ                                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: 論理監査                                            │
│  • Multi-Agent Validator                                     │
│  • 演算子理解エージェント                                    │
│  • 論理矛盾検出エージェント                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: 学習                                                │
│  • 失敗パターン DB に記録                                    │
│  • 次回実行時に警告注入                                      │
│  • 成功パターンも記録                                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Validated Output                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 0: 仕様強制注入

### 実装内容

```python
# mekhane/ccl/spec_injector.py

class SpecInjector:
    """CCL 実行前に仕様を強制注入"""
    
    def inject(self, ccl_expr: str) -> str:
        # 1. 演算子を抽出
        operators = self.parse_operators(ccl_expr)
        
        # 2. 各演算子の仕様を operators.md から取得
        specs = self.load_specs(operators)
        
        # 3. 理解確認クイズを生成
        quiz = self.generate_quiz(operators)
        
        # 4. 注入テンプレート
        return f"""
## 仕様確認 (必須)

以下の演算子を使用します。各演算子の意味を確認してから実行してください。

{specs}

## 理解確認

{quiz}

## 実行

CCL: {ccl_expr}
"""
```

### 演算子クイズ例

```
Q: 演算子 `!` の意味は？
A: [ここに回答を記載] ← 出力に含めさせる

Q: 演算子 `*^` の意味は？
A: [ここに回答を記載]
```

---

## Phase 1: 出力構造強制

### Pydantic スキーマ

```python
# mekhane/ccl/output_schema.py

from pydantic import BaseModel, Field
from typing import List, Optional

class OperatorVerification(BaseModel):
    """演算子理解の証明"""
    operator: str
    definition: str  # operators.md からの引用
    my_understanding: str  # 自分の言葉で説明

class CCLStepOutput(BaseModel):
    """各ステップの出力"""
    step_name: str
    reasoning: str = Field(min_length=100)  # 省略防止
    verification: str
    result: str

class CCLExecutionOutput(BaseModel):
    """CCL 実行全体の出力"""
    operator_verifications: List[OperatorVerification]
    steps: List[CCLStepOutput]
    final_result: str
    self_audit: str  # 自己監査
```

### 演算子別必須セクション

| 演算子 | 必須セクション |
|--------|---------------|
| `!` | `## 全派生リスト` |
| `~` | `## 振動: A ↔ B` (両方向必須) |
| `*` | `## 融合結果` |
| `^` | `## メタ分析` |
| `+` | `## 詳細展開` (3段階以上) |

---

## Phase 2: 出力検証

### Guardrails 設定

```yaml
# mekhane/ccl/guardrails/ccl_rails.yaml

rails:
  output:
    - check_operator_sections    # 演算子別セクション検証
    - check_minimum_length       # 最小長検証
    - check_reasoning_presence   # reasoning セクション検証
    - check_self_audit           # 自己監査の存在

actions:
  - name: check_operator_sections
    params:
      operator_section_map:
        "!": "## 全派生"
        "~": "## 振動"
        "*": "## 融合"
        "^": "## メタ"
        "+": "## 詳細"
```

### 違反時のリジェクト

```python
class OutputValidator:
    def validate(self, output: str, ccl_expr: str) -> ValidationResult:
        operators = self.parse_operators(ccl_expr)
        missing = []
        
        for op in operators:
            required_section = OPERATOR_SECTIONS[op]
            if required_section not in output:
                missing.append(f"演算子 {op} に必要なセクション '{required_section}' がありません")
        
        if missing:
            return ValidationResult(
                valid=False,
                errors=missing,
                instruction="以下のセクションを追加してください"
            )
        return ValidationResult(valid=True)
```

---

## Phase 3: 論理監査

### Multi-Agent 構成

```python
class CCLAuditAgents:
    """3エージェントによる監査"""
    
    def __init__(self):
        self.operator_agent = OperatorUnderstandingAgent()
        self.logic_agent = LogicConsistencyAgent()
        self.completeness_agent = CompletenessAgent()
    
    def audit(self, output: CCLExecutionOutput) -> AuditResult:
        results = [
            self.operator_agent.check(output),
            self.logic_agent.check(output),
            self.completeness_agent.check(output),
        ]
        return self.aggregate(results)
```

---

## Phase 4: 学習

### 失敗パターン DB

```python
# mekhane/ccl/failure_db.py

class FailureDB:
    """失敗パターンの記録と警告"""
    
    def record_failure(self, ccl_expr: str, failure: str, cause: str):
        """失敗を記録"""
        self.db.insert({
            "timestamp": datetime.now(),
            "ccl_expr": ccl_expr,
            "failure": failure,
            "cause": cause,  # 例: "演算子 ! を否定と誤解"
        })
    
    def get_warnings(self, ccl_expr: str) -> List[str]:
        """過去の失敗から警告を生成"""
        operators = self.parse_operators(ccl_expr)
        warnings = []
        for op in operators:
            past_failures = self.db.query(operator=op)
            if past_failures:
                warnings.append(f"⚠️ 演算子 {op} で過去に失敗: {past_failures[0]['cause']}")
        return warnings
```

---

## 実装順序

| Phase | 期間 | 成果物 |
|-------|------|--------|
| **0** | 今すぐ | `spec_injector.py` |
| **1** | 1-2日 | `output_schema.py` |
| **2** | 3-5日 | `guardrails/ccl_rails.yaml` |
| **3** | 1週間 | `audit_agents.py` |
| **4** | 1週間 | `failure_db.py` |

---

## ディレクトリ構造

```
mekhane/ccl/
├── __init__.py
├── spec_injector.py      # Phase 0
├── output_schema.py      # Phase 1
├── guardrails/           # Phase 2
│   ├── ccl_rails.yaml
│   └── validators.py
├── agents/               # Phase 3
│   ├── operator_agent.py
│   ├── logic_agent.py
│   └── completeness_agent.py
├── learning/             # Phase 4
│   ├── failure_db.py
│   └── patterns.json
└── executor.py           # 統合エントリポイント
```
