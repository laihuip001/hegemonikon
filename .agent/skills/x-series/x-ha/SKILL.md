---
id: "X-HA"
name: "Hormē → Akribeia"
category: "relation-layer"
pair: "H → A"
shared_coordinate: "C5 (Valence)"
relation_count: 8
type: "Anchor"
description: "傾向 (Hormē) が精密判断 (Akribeia) を方向づける8つの射"

activation_conditions:
  - context: "感情・確信・欲求が生じた後、それを精密に検証する必要があるとき"
  - trigger: "「感じた。でもそれは正しいか」の遷移"
  - confidence_threshold: 0.5
  - priority: "high"

triggers: ["傾向→精密", "/pro >> /dia", "/pis >> /epi", "/ore >> /pat", "動機→検証"]
keywords: [horme-akribeia, drive-to-precision, x-ha, motivation-to-judgment]
---

# X-HA: Hormē → Akribeia (傾向→精密)

> **共有座標**: C5 (Valence) | **型**: Anchor (Mixed→Pure)
> **認知的意味**: 動機の方向が判断の繊細さを決める

## なぜこの接続が存在するか

何を望むかが何を見極めるかを決定する。直感 (Propatheia) は精密な感情認識 (Pathos) に深化し、確信 (Pistis) は検証済み知識 (Epistēmē) に昇格する。これは FEP の「認識を行動で検証する」サイクル。

## 8関係

| X | Source | Target | 認知的説明 | CCL |
|:--|:-------|:-------|:-----------|:----|
| X-HA1 | H1 Propatheia | A1 Pathos | 直感→感情の精緻な認識 | `/pro >> /pat` |
| X-HA2 | H1 Propatheia | A2 Krisis | 直感→直感を批判的に検証 | `/pro >> /dia` |
| X-HA3 | H3 Orexis | A1 Pathos | 欲求→欲求の正体を感じ取る | `/ore >> /pat` |
| X-HA4 | H3 Orexis | A2 Krisis | 欲求→欲求の妥当性を判定 | `/ore >> /dia` |
| X-HA5 | H2 Pistis | A3 Gnōmē | 確信→確信から原則を抽出 | `/pis >> /gno` |
| X-HA6 | H2 Pistis | A4 Epistēmē | 確信→確信を知識に昇格 | `/pis >> /epi` |
| X-HA7 | H4 Doxa | A3 Gnōmē | 信念→信念から教訓を引き出す | `/dox >> /gno` |
| X-HA8 | H4 Doxa | A4 Epistēmē | 信念→信念を検証済み知識にする | `/dox >> /epi` |

## 使用例

```ccl
# 直感をクリティカルレビューで検証
/pro{first_impression: "これは良い"} >> /dia+{honest: true}

# 信念を知識に昇格
/dox{belief: "CCL は推論サイクルである"} >> /epi{verify: true}
```

## アンチパターン

| ❌ | 理由 |
|:---|:-----|
| 直感を検証せずに行動する | H→A をスキップ = 「楽」を選んでいる |
| 精密判断で感情を殺す | A は H を殺すのではなく精緻化する。Pathos は Propatheia の深化 |
| 知識を確信と混同 | Pistis ≠ Epistēmē。確信は主観、知識は検証済み |
