---
id: "X-HK"
name: "Hormē → Kairos"
category: "relation-layer"
pair: "H → K"
shared_coordinate: "C5 (Valence)"
relation_count: 8
type: "Bridge"
description: "傾向 (Hormē) が文脈 (Kairos) を歪める/活性化する8つの射"

activation_conditions:
  - context: "欲求・確信が強い状態で、タイミングや目的の判断が求められるとき"
  - trigger: "「これが欲しい → 今がチャンスだ」の認知バイアスを検出するとき"
  - confidence_threshold: 0.4
  - priority: "high"

triggers: ["傾向→文脈歪み", "/ore >> /euk", "/pis >> /chr", "欲求がタイミング認識を歪める"]
keywords: [horme-kairos, drive-to-context, x-hk, bias-detection, wishful-timing]
risk_tier: L0
risks: ["none identified"]
reversible: true
requires_approval: false
fallbacks: ["manual execution"]
---

# X-HK: Hormē → Kairos (傾向→文脈)

> **共有座標**: C5 (Valence) | **型**: Bridge (Mixed→Mixed)
> **認知的意味**: 欲求・確信が好機の認識を歪める

## なぜこの接続が存在するか

**最も危険な接続の一つ**。人間は望むものがあると「今がチャンスだ」と思い込みやすい。確信が強いと時間感覚が歪む。これは認知バイアスの構造的表現。

FEP 的には、precision が高すぎると prediction error を無視し、explore を阻害する。

## 8関係

| X | Source | Target | 認知的説明 | CCL |
|:--|:-------|:-------|:-----------|:----|
| X-HK1 | H1 Propatheia | K1 Eukairia | 直感→「今がチャンスだ」の認識 | `/pro >> /euk` |
| X-HK2 | H1 Propatheia | K3 Telos | 直感→直感が目的を修正する | `/pro >> /tel` |
| X-HK3 | H3 Orexis | K1 Eukairia | 欲求→欲しいものに好機を見出す | `/ore >> /euk` |
| X-HK4 | H3 Orexis | K3 Telos | 欲求→欲求が目的を書き換える | `/ore >> /tel` |
| X-HK5 | H2 Pistis | K2 Chronos | 確信→確信度が時間感覚を支配 | `/pis >> /chr` |
| X-HK6 | H2 Pistis | K4 Sophia | 確信→確信が「何を知るべきか」決める | `/pis >> /sop` |
| X-HK7 | H4 Doxa | K2 Chronos | 信念→信念が時間感覚を拡張/圧縮 | `/dox >> /chr` |
| X-HK8 | H4 Doxa | K4 Sophia | 信念→信念が「知恵の源泉」を選ぶ | `/dox >> /sop` |

## 使用例

```ccl
# 欲求が好機判断を歪めていないか検証
/ore >> /euk _ /dia.epo{check: "wishful timing?"}

# 確信が時間感覚に与える影響を自覚
/pis{level: "HIGH"} >> /chr{bias_check: true}
```

## アンチパターン

| ❌ | 理由 |
|:---|:-----|
| 欲求のまま好機を宣言する | X-HK3 の典型的悪用。必ず `/dia.epo` で判断停止を挟む |
| 確信が高いから急ぐ | X-HK5 のバイアス。高確信 = 短期感覚 → 早すぎる行動 |
| 信念で知恵を選り好みする | X-HK8 の確証バイアス。都合の良い情報だけ集める |

> ⚠️ **このペアを使うときは必ず `/dia.epo` (判断停止) を先行させよ。**
