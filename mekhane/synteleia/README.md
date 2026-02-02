# Synteleia Cognitive Ensemble Layer

> **Poiēsis/Dokimasia 2層アーキテクチャ** — メタ認知と社会的認知を実装する認知アンサンブル層

## 概要

Synteleia は Hegemonikón の6カテゴリ (O/H/A/S/P/K) を **2層構造** で実装する
メタ認知・社会的認知の実装層。

| 層 | 名称 | カテゴリ | 性質 |
|----|------|---------|------|
| **Layer 1** | Poiēsis (生成) | O, S, H | 何を・どう・なぜ |
| **Layer 2** | Dokimasia (審査) | P, K, A | 範囲・時期・精度 |

## ディレクトリ構造

```
synteleia/
├── __init__.py          # メインパッケージ
├── base.py              # 基底クラス
├── orchestrator.py      # 2層オーケストレーター
├── README.md            # このファイル
│
├── poiesis/             # Poiēsis (生成層)
│   ├── __init__.py
│   ├── ousia_agent.py   # O: 本質洞察
│   ├── schema_agent.py  # S: 構造設計
│   └── horme_agent.py   # H: 動機評価
│
└── dokimasia/           # Dokimasia (審査層)
    ├── __init__.py
    ├── perigraphe_agent.py  # P: 境界画定
    ├── kairos_agent.py      # K: 時宜判断
    ├── operator_agent.py    # A: 記号/演算子
    ├── logic_agent.py       # A: 論理矛盾
    └── completeness_agent.py # A: 欠落要素
```

## 使い方

```python
from mekhane.synteleia import AuditOrchestrator, AuditTarget, AuditTargetType

# ターゲット作成
target = AuditTarget(
    content="監査対象のテキスト",
    target_type=AuditTargetType.CODE
)

# 内積モード（デフォルト）
orchestrator = AuditOrchestrator()
result = orchestrator.audit(target)

print(orchestrator.format_report(result))
```

## CCL 構文

| 構文 | 意味 |
|------|------|
| `@poiesis` | 生成層のみ (O,S,H) |
| `@dokimasia` | 審査層のみ (P,K,A) |
| `@syn·` | 内積: 両層を統合 |
| `@syn×` | 外積: 3×3 交差検証 |

## 参照

- [設計文書](../../docs/architecture/synteleia.md)
