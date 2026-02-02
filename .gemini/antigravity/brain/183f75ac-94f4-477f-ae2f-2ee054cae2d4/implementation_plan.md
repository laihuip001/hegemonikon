# FEP Parameter Loader Implementation Plan

> **/plan v3.0 実行結果**

---

## STAGE 0: Blindspot + Scale

| カテゴリ | 盲点 | 解決策 |
|:---------|:-----|:-------|
| 🎯 Framing | YAML を読むだけでは不十分？ | 検証ロジックも含める |
| 📐 Scope | 既存 `_default_*` メソッドとの整合性 | 共存させる（フォールバック） |
| 🔗 Dependencies | PyYAML 必要？ | 標準ライブラリ or 既存依存確認 |
| 👤 Stakeholders | なし | - |
| ⏱️ Temporal | 将来の parameters.yaml 形式変更 | バージョンチェックを含める |

**📏 Scale**: 🔬 **Micro** — 単一モジュール追加

---

## STAGE 1: Strategy Selection

- **Files Read**: `fep_agent.py`, `parameters.yaml`, `persistence.py`
- **KI Referenced**: `active_inference_implementation`
- **Concerns**: 全解決済み

**⚖️ Explore/Exploit**: **Exploit** — 確実性高、緊急性なし

| Plan | 名称 | 概要 | リスク |
|:-----|:-----|:-----|:-------|
| A | Conservative | YAML読み込み関数のみ | 検証なし |
| **B** | **Robust** | 読み込み + 検証 + フォールバック | 工数やや増 |
| C | Aggressive | fep_agent.py 全面リファクタ | 破壊的変更 |

**選択: B (Robust)**

---

## STAGE 2: Success Criteria

| 軸 | Must | Should | Could |
|:---|:-----|:-------|:------|
| 機能性 | YAML から A/B/C/D パラメータ取得 | 検証・警告表示 | CLI ツール |
| 品質 | テスト 3 件以上通過 | docstring 完備 | 型ヒント完全 |
| 性能 | 読み込み < 100ms | キャッシュ | - |

**✅ 完了条件**: Must 全達成 + テスト通過

---

## STAGE 3: Blueprint

### Goal Decomposition

```
最終目標: parameters.yaml の値で FEP Agent を初期化
  ← サブゴール 1: YAML を読み込む関数
  ← サブゴール 2: パラメータを構造体に変換
  ← サブゴール 3: fep_agent.py から呼び出し
  ← サブゴール 4: テスト作成
  ← 現在地
```

### 変更対象ファイル

| ファイル | 変更内容 |
|:---------|:---------|
| [NEW] `mekhane/fep/config.py` | YAML 読み込み + 構造体定義 |
| [MODIFY] `mekhane/fep/fep_agent.py` | `_default_*` を config から取得に変更 |
| [MODIFY] `mekhane/fep/__init__.py` | `load_parameters` をエクスポート |
| [NEW] `tests/test_fep_config.py` | config モジュールのテスト |

### 依存関係

- **PyYAML**: 既存依存確認、なければ追加

---

## STAGE 4: Devil's Advocate

| 視点 | 判定 | 理由 |
|:-----|:-----|:-----|
| 🔴 Feasibility | ✅ PASS | 標準的な YAML 読み込み |
| 🔴 Necessity | ✅ PASS | ハードコード値の根拠明示に必須 |
| 🔴 Alternatives | ✅ PASS | JSON/TOML も可能だが YAML で十分 |
| 🔴 Risks | ✅ PASS | フォールバックで既存動作保証 |
| 🔴 Dependencies | ✅ PASS | PyYAML は一般的 |

### Pre-mortem

| 失敗シナリオ | 対策 |
|:-------------|:-----|
| YAML パースエラー | try/except + デフォルト値フォールバック |
| 型不一致 | 読み込み時に型検証 |
| ファイル見つからない | 存在チェック + デフォルト生成 |

---

## 実装計画

### Step 1: config.py 作成

```python
# mekhane/fep/config.py
from pathlib import Path
from dataclasses import dataclass
import yaml

@dataclass
class FEPParameters:
    A_high_reliability: float = 0.85
    A_low_reliability: float = 0.15
    C_high_positive: float = 2.5
    C_high_negative: float = -2.0
    D_uniform: float = 0.5
    gamma: float = 16.0
    ...

def load_parameters(path: Path = None) -> FEPParameters:
    ...
```

### Step 2: fep_agent.py 修正

```python
# _default_A() 内で config から値を取得
from .config import load_parameters, DEFAULT_PARAMS

...
p_high = self.params.A_high_reliability  # 0.85
```

### Step 3: テスト作成

```python
def test_load_parameters_default():
    params = load_parameters()
    assert params.A_high_reliability == 0.85

def test_load_parameters_from_yaml():
    params = load_parameters(PARAMETERS_YAML_PATH)
    assert params.gamma == 16.0
```

---

## ✅ All Stages Passed

**承認待ち**: 計画を承認しますか？ (`y`)
