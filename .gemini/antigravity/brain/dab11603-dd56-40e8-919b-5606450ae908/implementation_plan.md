# FEP Integration Features Implementation Plan

> **Hegemonikón**: O4 Energeia → P4 Tekhnē → S2 Mekhanē

## 概要

前回セッションの「アイデアの種」3つを実装し、`/noe` ワークフローで体験する。

| Feature | 目的 | 優先度 |
|:--------|:-----|:-------|
| **X-series FEP 統合** | `/noe` 完了時の次ステップを FEP で推奨 | High |
| **リアルタイム学習デモ** | A行列の学習進捗を可視化 | Medium |
| **自動 encoder 呼び出し** | PHASE 5 → FEP 観察の自動変換 | High |

---

## Proposed Changes

### Feature 1: X-series 36関係の FEP 統合

#### [NEW] [x_series_navigator.py](file:///home/laihuip001/oikos/hegemonikon/mekhane/fep/x_series_navigator.py)

36関係を FEP 状態空間として定義し、現在地から次ステップを推奨。

```python
# 概要
X_SERIES_TRANSITIONS = {
    "O": ["X-OO", "X-OS", "X-OH", "X-OP", "X-OK", "X-OA"],
    "S": ["X-SO", "X-SS", "X-SH", "X-SP", "X-SK", "X-SA"],
    ...
}

def recommend_next_step(current_series: str, context: dict) -> XSeriesRecommendation:
    """FEP agent を使って最適な次ステップを推奨"""
    ...
```

---

### Feature 2: FEP Agent のリアルタイム学習デモ

#### [MODIFY] [encoding.py](file:///home/laihuip001/oikos/hegemonikon/mekhane/fep/encoding.py)

学習進捗の可視化関数を追加。

```python
def format_learning_progress(
    before_A: np.ndarray,
    after_A: np.ndarray,
    observation: tuple
) -> str:
    """A行列の変化を Markdown で可視化"""
    ...
```

---

### Feature 3: /noe 実行時の自動 encoder 呼び出し

#### [MODIFY] [encoding.py](file:///home/laihuip001/oikos/hegemonikon/mekhane/fep/encoding.py)

既存の `encode_noesis_output()` を拡張し、自動変換ロジックを強化。

```python
def auto_encode_noesis(phase5_output: dict) -> tuple:
    """PHASE 5 JSON 出力を FEP 観察に自動変換"""
    confidence = phase5_output.get("confidence_score", 0.5)
    zones = phase5_output.get("uncertainty_zones", [])
    return encode_noesis_output(confidence, zones)
```

#### [MODIFY] [O1 Noēsis SKILL.md](file:///home/laihuip001/oikos/.agent/skills/ousia/o1-noesis/SKILL.md)

PHASE 5 完了後の FEP 統合を明確化。

---

## Verification Plan

### Automated Tests

```bash
# 既存テスト（336件）が通ることを確認
cd /home/laihuip001/oikos/hegemonikon && \
/home/laihuip001/oikos/hegemonikon/.venv/bin/python -m pytest mekhane/fep/tests/ -v

# 新規テスト追加
# - test_x_series_navigator.py (Feature 1)
# - encoding.py の format_learning_progress テスト (Feature 2)
```

### Manual Verification

`/noe` ワークフローを実行し、以下を確認:

1. **X-series 推奨**: `/noe` 完了時に X-series 次ステップが表示されるか
2. **学習可視化**: A行列の変化が表示されるか
3. **自動 encoder**: PHASE 5 出力が自動で FEP に渡されるか

---

## 実装順序

```mermaid
graph LR
    F3[Feature 3: 自動encoder] --> F2[Feature 2: 学習可視化]
    F3 --> F1[Feature 1: X-series統合]
    F2 --> T[テスト]
    F1 --> T
    T --> N[/noe 実体験]
```

**理由**: Feature 3 が他2つの基盤となるため最初に実装。

---

*Plan created: 2026-01-29T13:40+09:00*
