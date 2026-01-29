# Flow AI — Hegemonikón Recast

> **poiēma** (ποίημα) = 「作られたもの」「成果物」
>
> Hegemonikón の設計原則に基づいて構築されたテキスト前処理ツール

---

## 概要

Flow AI は「殴り書き」を「整形されたプロンプト」に変換するツールです。
このモジュールは Hegemonikón の語彙で完全に再構築されています。

## 哲学的マッピング

| モジュール | 定理 | 責務 |
|:-----------|:-----|:-----|
| `MetronResolver` | S1 Metron | 連続スペクトラム → 離散段階への尺度解決 |
| `EpocheShield` | A2 Krisis (Epochē) | 判断保留状態での PII 保護 |
| `EnergeiaCoreResolver` | O4 Energeia | 意志を現実化する統一行動層 |
| `DoxaCache` | H4 Doxa | 信念（結果）の永続化 |
| `NoesisClient` | O1 Noēsis | 外部AI認識への委譲 |

## 使用例

```python
from hegemonikon.mekhane.poiema.flow import (
    MetronResolver,
    EpocheShield,
    EnergeiaCoreResolver,
)

# S1 Metron: 尺度解決
level = MetronResolver.resolve_level(75)  # -> 100 (RICH)
prompt = MetronResolver.get_system_prompt(level)

# A2 Epochē: PII 保護
shield = EpocheShield()
masked, mapping = shield.mask("Call me at 03-1234-5678")
# masked: "Call me at [EPOCHE_0]"

# O4 Energeia: 統合処理
core = EnergeiaCoreResolver()
result = await core.process("入力テキスト", metron_level=60)
```

## 後方互換性

旧名もエイリアスとして使用可能：

```python
# 旧Flow AI コードとの互換性
from hegemonikon.mekhane.poiema.flow.metron_resolver import SeasoningManager
from hegemonikon.mekhane.poiema.flow.epoche_shield import PrivacyHandler
from hegemonikon.mekhane.poiema.flow.energeia_core import CoreProcessor
```

## 設計原則

### 下処理の美学

```text
「素材を活かす。過剰加工しない」
→ H1 Propatheia (前感情): 第一印象を大切に
```

### 非破壊的介入

```text
「既存AIの人格を上書きしない。黒子に徹する」
→ A2 Epochē: 判断を保留し、安全側に倒す
```

### ゼロ・フリクション

```text
「最短・最速。思考を止めない」
→ K1 Eukairia: 適切なタイミングで適切な選択
```

---

## ディレクトリ構造

```
poiema/flow/
├── __init__.py           # パッケージ定義
├── metron_resolver.py    # S1 Metron
├── epoche_shield.py      # A2 Krisis
├── energeia_core.py      # O4 Energeia
├── doxa_cache.py         # H4 Doxa
├── noesis_client.py      # O1 Noēsis
└── tests/
    └── test_flow_recast.py
```

---

*Recast from Flow AI v5.0 — 2026-01-29*
*Hegemonikón poiēma Layer*
