# O/T/K/X 命名体系 ドキュメント更新マニュアル

> **目的**: P/M/K/T体系からO/T/K/X体系への移行を完全に実行するための作業指示書

---

## 正本

**参照すべき正規定義**: `docs/session_handoff_20260124.md`

---

## 命名変更マップ

| 旧記号 | 旧名称 | 新記号 | 新名称 | 正式名（複合形） | ギリシャ語 |
|--------|--------|--------|--------|-----------------|-----------|
| P | Praxis | **O** | Ousia | Ousiakē Tetras | Οὐσιακὴ Τετράς |
| M | Mēkhanē | **T** | Tropos | Tropikē Ogdoas | Τροπικὴ Ὀγδοάς |
| K | Kairos | **K** | Kairos | Kairiakē Dodecas | Καιριακὴ Δωδεκάς |
| T | Taxis | **X** | Taxis | Taxikē Eikositessera | Ταξικὴ Εἰκοσιτέσσερα |

---

## ID変更マップ

### O-series (旧P-series)
| 旧ID | 新ID | 機能 |
|------|------|------|
| P1 | **O1** | Noēsis (情報推論) |
| P2 | **O2** | Boulēsis (目標推論) |
| P3 | **O3** | Zētēsis (情報行為) |
| P4 | **O4** | Energeia (目標行為) |

### T-series (旧M-series)
| 旧ID | 新ID | 機能 |
|------|------|------|
| M1 | **T1** | Aisthēsis (知覚) |
| M2 | **T2** | Krisis (判断) |
| M3 | **T3** | Theōria (内省) |
| M4 | **T4** | Phronēsis (戦略) |
| M5 | **T5** | Peira (探索) |
| M6 | **T6** | Praxis (実行) |
| M7 | **T7** | Dokimē (検証) |
| M8 | **T8** | Anamnēsis (記憶) |

### K-series (変更なし)
| 旧ID | 新ID | 備考 |
|------|------|------|
| K1-K12 | K1-K12 | 変更なし |

### X-series (旧T-series/Taxis)
| 旧ID | 新ID | 機能 |
|------|------|------|
| T-P | **X-O** | メタ認知的従属 |
| T-M | **X-T** | 機能間従属 |
| T-K | **X-K** | 文脈間従属 |

---

## 更新対象ファイル

| # | ファイル | 変更内容 | 優先度 |
|---|----------|----------|--------|
| 1 | `kernel/axiom_hierarchy.md` | 全シリーズ名・ID更新 | HIGH |
| 2 | `kernel/SACRED_TRUTH.md` | シリーズ名・構造図更新 | HIGH |
| 3 | `kernel/doctrine.md` | 公理表更新 | HIGH |
| 4 | `kernel/taxis_design.md` | X-series表記に更新 | HIGH |
| 5 | `README.md` | 構造図・表更新 | HIGH |
| 6 | `kernel/KERNEL_PRACTICE_GUIDE.md` | 早見表更新 | MEDIUM |
| 7 | `.gemini/GEMINI.md` | 参照更新 | MEDIUM |

---

## 検索・置換パターン

```
P-series → O-series (Ousia)
M-series → T-series (Tropos)
T-series (Taxis関連) → X-series (Taxis)
P1, P2, P3, P4 → O1, O2, O3, O4
M1-M8 → T1-T8
T-P, T-M, T-K → X-O, X-T, X-K
```

---

## チェックリスト

### 更新前
- [x] session_handoff_20260124.md を確認した
- [ ] 全対象ファイルをバックアップした（Git管理）

### 各ファイル更新時
- [ ] シリーズ名が O/T/K/X に変更された
- [ ] 個別IDが O1-O4, T1-T8, K1-K12, X-O/X-T/X-K に変更された
- [ ] ギリシャ語正式名が追加された

### 更新後
- [ ] 全ファイルで表記が一貫している
- [ ] git commit 完了

---

*このマニュアルは O/T/K/X 命名体系への移行を支援する。*
