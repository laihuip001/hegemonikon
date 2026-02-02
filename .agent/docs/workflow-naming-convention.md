# ワークフロー命名規則

> **Hegemonikón v2.2**
> **自動生成**: このファイルは `.agent/scripts/update-workflow-registry.py` で自動更新可能

---

## 階層構造

| 層 | 文字数 | 命名規則 | 役割 |
|:---|:-------|:---------|:-----|
| **Ω (Omega)** | 1-2 | 英字のみ | 定理群統合オーケストレーター |
| **Δ (Delta)** | 3 | ギリシャ語由来 | ドメイン専門家（定理発動） |
| **τ (Tau)** | 3-4 | 英語可 | 個別タスク実行 |
| **特殊** | 1 | `/u` のみ | 例外（意見要求） |

---

## Ω層 (Omega) — 1-2文字

| cmd | 対応 | description |
|:----|:-----|:------------|
| `/o` | O-series | O-series（Ousia 純粋定理 O1-O4）を駆動 |
| `/s` | S-series | S-series（Schema 戦略定理 S1-S4）を駆動 |
| `/h` | H-series | H-series（Hormē 衝動定理 H1-H4）を駆動 |
| `/p` | P-series | P-series（Perigraphē 環境定理 P1-P4）を駆動 |
| `/k` | K-series | K-series（文脈定理 K1-K12）を駆動 |
| `/a` | A-series | A-series（Akribeia 精度定理 A1-A4）を駆動 |
| `/x` | X-series | X-series（関係層）を駆動 |
| `/ax` | 全定理 | O/S/H/P/K/A/X 定理群を順に実行する統合ワークフロー |

---

## Δ層 (Delta) — 3文字

| cmd | modules | description |
|:----|:--------|:------------|
| `/noe` | O1 | O1 Noēsis（深い認識・直観）を発動する最深層思考ワークフロー |
| `/bou` | O2 | O2 Boulēsis（意志・目的）を発動し、「何を望むか」を明確化 |
| `/zet` | O3 | O3 Zētēsis（探求）を発動し、調査依頼書を生成 |
| `/ene` | O4 | O4 Energeia（行為）を発動し、意志を現実に具現化 |
| `/dia` | O1, A2 | A2 Krisis を駆動する統合ワークフロー。検証・批評・診断・Synedrion（旧 /chk 統合済） |

---

## τ層 (Tau) — 3-4文字

<!-- AUTO_GENERATED_START -->
| cmd | modules | description | pair |
|:----|:--------|:------------|:-----|
| `/boot` | O1,H4 | MAY abbreviate, minimum viable boot only | `-` |
| `/bye` | H4 | MUST analyze: why end now? | `-` |
| `/dev` | P4 | MUST meta-analyze: why this module? | `-` |
| `/sop` | K4 | MUST question the research direction itself | `-` |
| `/vet` | A2,A4 | MUST meta-analyze: why this audit approach? | `/sop` |
| `/why` | O3 | MUST meta-analyze: is Five Whys process correct? | `-` |
<!-- AUTO_GENERATED_END -->

---

## 規則

1. **文字数でおおよその階層が判別できる**
2. **直感的命名を優先**（厳密な文字数制限より意味が通じることが重要）
3. **ペア関係のあるコマンドは `pair:` フィールドで明示**
4. **新規ワークフロー追加時は `update-workflow-registry.py` を実行**

---

*Last updated: 2026-02-01*
