---
description: |
  12随伴対 + Trigonon のクイックリファレンスマップ。
  「どの WF がどの随伴で、η/ε は何か」を一覧できる always_on Rule。
---

# 🗺️ Category Map — HGK 圏論のクイックリファレンス

> Skill: `.agent/skills/category-engine/SKILL.md` (v1.0)
> 語彙: `.agent/rules/category-theory-verbs.md`
> 問い: `.agent/rules/category-lens.md`

---

## 12随伴対

| # | F⊣G | WF | η (F→忘→戻) | ε (忘→F→戻) | 典型 Drift |
|:--|:-----|:---|:-------------|:-------------|:-----------|
| 1 | Noēsis⊣Zētēsis | /noe⊣/zet | 深い認識→問い→再認識 | 問い→認識→再探求 | 0.1-0.2 |
| 2 | Energeia⊣Boulēsis | /ene⊣/bou | 行為→意志→再行為 | 意志→行為→再意志 | 0.2-0.3 |
| 3 | Krisis⊣Epistēmē | /dia⊣/epi | 判定→知識→再判定 | 知識→判定→再確認 | 0.1-0.2 |
| 4 | Mekhanē⊣Praxis | /mek⊣/pra | 方法→実践→再設計 | 実践→方法→再実行 | 0.2-0.4 |
| 5 | Pistis⊣Doxa | /pis⊣/dox | 確信→信念→再確信 | 信念→確信→再信念 | 0.1-0.2 |
| 6 | Propatheia⊣Orexis | /pro⊣/ore | 前感情→欲求→再直感 | 欲求→前感情→再評価 | 0.3-0.5 |
| 7 | Metron⊣Stathmos | /met⊣/sta | 測定→評価→再測定 | 評価→測定→再評価 | 0.1-0.2 |
| 8 | Eat⊣Fit | /eat⊣/fit | 取り込み→検証→再取込 | 検証→取り込み→再検証 | 0.1-0.3 |
| 9 | Boot⊣Bye | /boot⊣/bye | 起動→終了→再起動 | 終了→起動→再終了 | 0.2-0.4 |
| 10 | Tropos⊣Hodos | /tro⊣/hod | 転換→道程→再転換 | 道程→転換→再道程 | 0.3-0.5 |
| 11 | Gnōsis⊣Eukrineia | /gno⊣/euk | 知識→判明→再知識 | 判明→知識→再判明 | 0.1-0.2 |
| 12 | Khōra⊣Stasis | /kho⊣/sta | 場→配置→再場 | 配置→場→再配置 | 0.2-0.3 |

### 方向の絶対規則

```
左随伴 F = 自由 = 構造付与 = 外→内 (取り込み)
右随伴 G = 忘却 = 構造剥離 = 内→外 (出力)
```

---

## Trigonon K₃

```
           O (Ousia)
          L1 × L1
         ╱     ╲
        S       H
     (Schema) (Hormē)
     L1×L1.5  L1×L1.75
      ╱         ╲
    P ─── K ─── A
 (Perigraphē) (Akribeia)
   L1.5²  (Kairos)  L1.75²
          L1.5×L1.75
```

| 種類 | 頂点/辺 | X-series | 意味 |
|:-----|:--------|:---------|:-----|
| **Pure** | O, P, A | — | 自己積（座標空間の原点） |
| **Mixed** | S, H, K | — | 異種積（頂点間の橋渡し） |
| **Bridge** | S↔H, S↔K, H↔K | X-SH, X-SK, X-HK | 同型的接続 (24) |
| **Anchor** | O↔S, O↔H, P↔S, P↔K, A↔H, A↔K | X-OS, X-OH, X-SP, X-PK, X-HA, X-KA | 類比的接続 (48) |

---

## CCL × 圏論 クイック対応

| CCL | 圏論 | 例 |
|:----|:-----|:---|
| `/noe` | 関手 Noēsis を適用 | 深い認識 |
| `/noe+` | 詳細化（積） | 深い派生 |
| `~` | 自然変換（2つの view で振動） | 探索↔実行 |
| `>>` | 合成 | /noe >> /dia = 認識→判定 |
| `{}` | 直積（並列実行） | {/noe, /dia} |
| `\` | 余極限（合流） | 複数を統合 |

---

## Drift 閾値 [推定: 経験的推定。実データで要検証]

| Drift | 判定 | 対処 |
|:------|:-----|:-----|
| < 0.1 | ✅ 優秀 | そのまま |
| 0.1-0.3 | ⚠️ 注意 | 失われた情報を記録 |
| 0.3-0.5 | ❌ 要改善 | 随伴の再設計を検討 |
| > 0.5 | 🚨 破綻 | 随伴として成立していない |

---

*Rule v3.0 — @repeat[x3, /dia+~/noe+] Kalon 認定 (2026-02-11)*
