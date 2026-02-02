# Dendron 次フェーズ実装計画

> **目的**: Dendron CLI の統合・強化と、CCL 実行保証の Multi-Agent 監査基盤構築
> **CCL**: `/mek+` >> `/plan`

---

## 概要

Dendron MVP は完成（mekhane/ 100% カバレッジ達成）。次フェーズで以下を実装する:

1. **check_proof.py との統合** — 機能重複解消、Dendron を正本化
2. **Phase 3 Multi-Agent 監査** — CCL 実行出力の論理検証

---

## User Review Required

> [!IMPORTANT]
> **Phase 3 Multi-Agent 監査**は複雑で、1週間以上の工数が見込まれます。
> まず **統合フェーズ（1-2時間）** を完了してから Phase 3 に着手することを推奨します。

---

## 現状分析

### 機能重複

| 機能 | check_proof.py | dendron/ |
|------|---------------|----------|
| PROOF ヘッダー検出 | ✅ | ✅ |
| レベル統計 (L1/L2/L3) | ✅ | ✅ |
| ディレクトリ PROOF.md 検証 | ❌ | ✅ |
| 対象範囲 | mekhane/ 固定 | 任意ディレクトリ |
| 出力形式 | text のみ | text/markdown/json/ci |
| CI インテグレーション | ✅ (exit code) | ✅ (--ci flag) |

**結論**: Dendron は check_proof.py の上位互換。統合により check_proof.py を非推奨化。

---

## Proposed Changes

### Phase A: check_proof.py 統合 (1-2時間)

#### [MODIFY] [check_proof.py](file:///home/laihuip001/oikos/hegemonikon/mekhane/scripts/check_proof.py)

- Dendron CLI への委譲ラッパーに変更
- 後方互換性維持（同じ引数、同じ終了コード）
- 非推奨警告を出力

```python
#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] 後方互換ラッパー（非推奨）
"""
DEPRECATED: Use `python -m dendron.cli check mekhane/` instead.
"""

import subprocess
import sys
import warnings

warnings.warn(
    "check_proof.py is deprecated. Use 'python -m dendron.cli check mekhane/' instead.",
    DeprecationWarning,
)

def main():
    cmd = [
        sys.executable, "-m", "dendron.cli", "check", "mekhane/",
        "--format", "ci" if "--ci" in sys.argv else "text",
    ]
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent.parent)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
```

#### [MODIFY] [checker.py](file:///home/laihuip001/oikos/hegemonikon/dendron/checker.py)

- レベル統計を CheckResult に追加（check_proof.py の機能移植）

```python
@dataclass
class CheckResult:
    # ... existing fields ...
    level_stats: Dict[ProofLevel, int] = field(default_factory=dict)
```

#### [MODIFY] [reporter.py](file:///home/laihuip001/oikos/hegemonikon/dendron/reporter.py)

- レベル統計の出力を追加

---

### Phase B: Phase 3 Multi-Agent 監査基盤 (1週間)

> **文脈**: 前回セッションで実装した Zero-Trust CCL Executor の Phase 3

#### [NEW] [audit_agents/__init__.py](file:///home/laihuip001/oikos/hegemonikon/mekhane/ccl/agents/__init__.py)

パッケージ定義

#### [NEW] [operator_agent.py](file:///home/laihuip001/oikos/hegemonikon/mekhane/ccl/agents/operator_agent.py)

CCL 演算子の正しい理解を検証するエージェント

```python
class OperatorUnderstandingAgent:
    """演算子理解検証エージェント"""
    
    def check(self, output: CCLExecutionOutput) -> AgentResult:
        """演算子の意味が正しく適用されているか検証"""
        ...
```

#### [NEW] [logic_agent.py](file:///home/laihuip001/oikos/hegemonikon/mekhane/ccl/agents/logic_agent.py)

論理矛盾検出エージェント

#### [NEW] [completeness_agent.py](file:///home/laihuip001/oikos/hegemonikon/mekhane/ccl/agents/completeness_agent.py)

出力の完全性検証エージェント

#### [NEW] [audit_orchestrator.py](file:///home/laihuip001/oikos/hegemonikon/mekhane/ccl/agents/audit_orchestrator.py)

3エージェントの統合オーケストレーター

---

## Verification Plan

### Phase A: 自動テスト

```bash
# 1. Dendron 単体テスト（現状テストなし → 新規作成が必要）
cd /home/laihuip001/oikos/hegemonikon
PYTHONPATH=/home/laihuip001/oikos/hegemonikon .venv/bin/python -m pytest dendron/tests/ -v

# 2. 統合テスト: check_proof.py が Dendron に委譲することを確認
python mekhane/scripts/check_proof.py --verbose
# 期待: 非推奨警告 + 正常終了

# 3. 回帰テスト: mekhane/ 100% カバレッジ維持
PYTHONPATH=/home/laihuip001/oikos/hegemonikon .venv/bin/python -m dendron.cli check mekhane/ --format ci
# 期待: ✅ 100.0% coverage
```

### Phase B: 手動検証

Phase 3 Multi-Agent 監査は、実際の CCL 式を入力して検証:

```bash
# CCL 式の実行と監査
python -m mekhane.ccl.executor "/noe+*^/dia-" --audit
# 期待: 3エージェントによる監査レポート
```

---

## ディレクトリ構造（最終形）

```
hegemonikon/
├── dendron/              # 存在証明検証ツール（正本）
│   ├── __init__.py
│   ├── checker.py        # ← レベル統計追加
│   ├── reporter.py       # ← レベル統計出力追加
│   ├── cli.py
│   └── tests/
│       ├── __init__.py
│       └── test_checker.py  # ← NEW
│
└── mekhane/
    ├── scripts/
    │   └── check_proof.py   # ← 非推奨ラッパーに変更
    │
    └── ccl/
        └── agents/          # ← NEW: Phase 3
            ├── __init__.py
            ├── operator_agent.py
            ├── logic_agent.py
            ├── completeness_agent.py
            └── audit_orchestrator.py
```

---

## 実装順序

| 順序 | タスク | 工数 |
|------|--------|------|
| 1 | CheckResult にレベル統計追加 | 15分 |
| 2 | Reporter にレベル統計出力追加 | 15分 |
| 3 | check_proof.py を非推奨ラッパー化 | 30分 |
| 4 | test_checker.py 作成 | 30分 |
| 5 | 統合テスト実行 | 15分 |
| **A 合計** | **Phase A 完了** | **1.5時間** |
| 6 | agent 基盤スケルトン作成 | 1時間 |
| 7 | OperatorUnderstandingAgent 実装 | 2時間 |
| 8 | LogicConsistencyAgent 実装 | 2時間 |
| 9 | CompletenessAgent 実装 | 2時間 |
| 10 | Orchestrator + テスト | 2時間 |
| **B 合計** | **Phase B 完了** | **9時間** |
