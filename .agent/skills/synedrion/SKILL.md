---
name: Synedrion Council
description: "\u5049\u4EBA\u8A55\u8B70\u4F1A (Synedrion) \u306B\u3088\u308B\u591A\u89D2\
  \u7684\u30EC\u30D3\u30E5\u30FC\u30FB\u76E3\u67FB"
triggers:
- "\u8A55\u8B70\u4F1A"
- "\u30EC\u30D3\u30E5\u30FC"
- "\u76E3\u67FB"
- synedrion
- "\u5049\u4EBA"
- "\u591A\u89D2"
- "\u6279\u8A55"
- /syn
risk_tier: L1
reversible: true
requires_approval: false
risks: []
fallbacks: []
---

# Synedrion Council

> **目的**: 偉人評議会を召喚し、多角的批評を実行する。

## 発動条件

- 設計・方針の多角的レビューが必要な時
- /syn ワークフロー実行時
- AI 監査が必要な時

## 手順

### Step 1: 評議会を召喚

AI 監査モードを使用:

// turbo

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from mekhane.synedrion.ai_auditor import AIAuditor
auditor = AIAuditor()
result = auditor.audit('TOPIC_OR_CODE')
print(result)
"
```

> ⚠️ `TOPIC_OR_CODE` を監査対象に置換。

### Step 2: /syn ワークフローを参照

大規模レビューには `/syn` WF を実行すること。

---

*v1.0 — 全PJ IDE配線 (2026-02-08)*
