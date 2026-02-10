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

risk_tier: "L1"
risks:
  - "テンプレート不整合による出力品質低下"
---

# Poiema Generator

> **目的**: 構造化された出力を生成する。Boot レポート、Handoff、定型ドキュメント等。

## Overview

Poiema はテンプレートベースの構造化出力生成エンジン。Boot レポート、Handoff、PII マスキング、信念キャッシュなどの定型ドキュメントを品質保証付きで生成する。EpocheShield による PII 保護機能を内蔵。

## Core Behavior

- Boot context の取得と構造化レポート生成
- Handoff ドキュメントの自動生成
- PII マスキング (EpocheShield): 個人情報の自動検出と置換
- 信念キャッシュ (DoxaCache): 過去の判断をキャッシュして再利用
- Fallback: API/モジュール不在時はテンプレート骨格のみ出力
- エラーハンドリング: 生成失敗時はエラー詳細と手動代替手順を提示

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

## Quality Standards

- 生成されたレポートに必須セクションが全て含まれること
- PII マスキング精度: 既知パターンの検出率 ≥ 95%
- Handoff が「赤の他人」基準 (読み手が一人で理解し行動できる) を満たすこと

## Edge Cases

- **Boot context が空**: 最小限のテンプレートで骨格を出力
- **PII 偽陽性**: 技術用語をPIIと誤検出した場合、マッピングに記録して復元可能にする
- **テンプレート不整合**: バージョン差がある場合は警告を出力して最新テンプレートを使用
- **API 接続失敗**: ローカルキャッシュから生成

## Examples

**入力**: `mask_pii("田中太郎さん (03-1234-5678) の検査結果")`

**出力**:

```
Masked: [NAME_1]さん ([PHONE_1]) の検査結果
Mapping: 2 entries
  NAME_1 → 田中太郎
  PHONE_1 → 03-1234-5678
```

---

*v1.2 — Quality Scorer 対応セクション追加 (2026-02-11)*
