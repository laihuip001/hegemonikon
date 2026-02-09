---
name: Poiema Generator
description: 構造化出力の生成 (Boot レポート, Handoff, 定型ドキュメント)
triggers:
  - "生成"
  - "レポート"
  - "Handoff"
  - "出力"
  - "poiema"
  - "テンプレート"
  - "ドキュメント生成"
---

# Poiema Generator

> **目的**: 構造化された出力を生成する。Boot レポート、Handoff、定型ドキュメント等。

## 発動条件

- 構造化出力の生成が必要な時
- /bye での Handoff 生成時
- /boot での Boot レポート生成時

## モジュール構造

| モジュール | import | 用途 |
|:---|:---|:---|
| NoesisClient | `from mekhane.poiema.flow.noesis_client import NoesisClient` | Gemini API 呼び出し |
| EnergeiaCoreResolver | `from mekhane.poiema.flow.energeia_core import EnergeiaCoreResolver` | コア実行解決 |
| EpocheShield | `from mekhane.poiema.flow.epoche_shield import EpocheShield` | PII マスキング |
| DoxaCache | `from mekhane.poiema.flow.doxa_cache import DoxaCache` | 信念キャッシュ |
| MetronResolver | `from mekhane.poiema.flow.metron_resolver import MetronResolver` | スケール解決 |

## 手順

### Step 1: Boot レポート生成

// turbo

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from mekhane.symploke.boot_integration import get_boot_context
ctx = get_boot_context(mode='standard')
print(f'Boot context loaded: {len(ctx)} keys')
print(f'Formatted output: {len(ctx[\"formatted\"])} chars')
"
```

### Step 2: Handoff 生成 (/bye 用)

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from mekhane.symploke.boot_integration import get_boot_context
ctx = get_boot_context()
# Handoff 情報を要約
handoffs = ctx.get('handoffs', {})
print(f'Handoffs: {handoffs.get(\"count\", 0)} entries')
"
```

### Step 3: PII マスキング (Epochē)

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from mekhane.poiema.flow.epoche_shield import mask_pii
masked, mapping = mask_pii('INPUT_TEXT')
print(f'Masked: {masked}')
print(f'Mapping: {len(mapping)} entries')
"
```

> ⚠️ `INPUT_TEXT` を実際のテキストに置換。

---

*v1.1 — import パス検証済み (2026-02-09)*

risk_tier: L1
reversible: true
requires_approval: false
risks:
  - Implicit assumptions
fallbacks:
  - Manual intervention
