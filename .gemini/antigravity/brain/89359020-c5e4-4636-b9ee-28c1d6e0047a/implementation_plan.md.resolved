# Workflow Consolidation Plan v2

> **Model**: `/mek --target=` パターンで子を親が吸収

---

## 改訂版分析

| 親 | 子 | 備考 |
|:---|:---|:-----|
| `/dia` | epo, fit, pan, vet | 4子 (検証系) |
| `/noe` | **syn** | 1子 (批評は認識の深化) |
| `/zet` | poc, why | 2子 |
| `/bou` | pre | 1子 |
| `/ene` | flag | 1子 |
| `/x` | ~~ax~~ | **除外** (全層統合WF) |

**削減**: 46 → **37** ワークフロー (**-9**)

---

## 統合後の姿

```yaml
# /dia (A2 Krisis) - 検証系
/dia                      # デフォルト
/dia --mode=epochē        # 判断停止
/dia --mode=audit         # 消化品質診断
/dia --mode=panorama      # メタ認知レーダー
/dia --mode=cross-model   # Cross-Model 検証

# /noe (O1 Noēsis) - 認識深化系
/noe                      # デフォルト
/noe --mode=council       # 偉人評議会

# /zet (O3 Zētēsis) - 探求系
/zet                      # デフォルト
/zet --mode=poc           # Spike/PoC
/zet --mode=five-whys     # Five Whys

# /bou (O2 Boulēsis) - 意志系
/bou --mode=premortem     # Premortem

# /ene (O4 Energeia) - 実行系
/ene --mode=feature-flag  # Feature Flags
```

---

## 除外

| WF | 理由 |
|:---|:-----|
| `/ax` | 全層統合メタWF、独立維持が美しい |

---

## 実装順序

1. Phase 1: `/dia` (4子吸収)
2. Phase 2: `/noe` (1子吸収 - /syn)
3. Phase 3: `/zet` (2子吸収)
4. Phase 4: 残り (2子)
