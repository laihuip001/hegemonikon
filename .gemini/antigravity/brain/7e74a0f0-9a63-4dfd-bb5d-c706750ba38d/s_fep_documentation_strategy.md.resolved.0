# /s: FEP Module Integration Documentation Strategy

## STAGE 0: Prior Art + Blindspot + Scale [S1 Metron]

### Phase 0.0: Prior Art Check

| 確認事項 | 結果 |
|:---------|:-----|
| 同じ構造のドキュメントがあるか | ❌ FEP層の統合ドキュメントなし |
| 既存パターン | ✅ `/noe` artifact形式、SKILL.md形式がある |
| 参考 | ✅ implementation_plan.md が参考になる |

### Phase 0.1: Blindspot Check

| カテゴリ | 確認 |
|:---------| :----- |
| 🎯 Framing | モジュール間連携が文書化されていない |
| 📐 Scope | 8モジュール + FEP Agent + 派生選択器 = 10コンポーネント |
| 🔗 Dependencies | encode_*_observation → FEP Agent → A-matrix |

### Phase 0.2: Scale Determination

**スケール: 🔭 Meso** (モジュール間統合)

---

## STAGE 1: Strategy Selection [S2 Mekhanē]

### Explore vs Exploit

| 軸 | 判定 |
|:---|:-----|
| 失敗コスト | 低い → **Explore** |
| 環境確実性 | 確実（実装完了済み） |
| 時間制約 | 柔軟 |

**判定: Explore** — ドキュメント整備は低リスク

### 3プラン

| Plan | 内容 | 工数 |
|:-----|:-----|:-----|
| **A Conservative** | README.md に概要追加のみ | 15分 |
| **B Robust ✅** | 統合テスト + アーキテクチャ図 + 使用例 | 45分 |
| **C Aggressive** | 全モジュールにSKILL.md + フル統合デモ | 2時間 |

**選択: B Robust**

### Y-1 評価

| 層 | 評価 |
|:---|:-----|
| **Fast** | ✅ 即座に開発者が使用可能 |
| **Slow** | ✅ セッション間で知識保持 |
| **Eternal** | ✅ Hegemonikón体系の正式文書として永続 |

### D-1 評価

| フェーズ | 影響 |
|:---------|:-----|
| **T+0** | ドキュメント 1ファイル生成 |
| **T+1** | KIに取り込まれる可能性 |
| **T+2** | 新規参加者のオンボーディングに活用 |

---

## STAGE 2: Success Criteria [S3 Stathmos]

| 軸 | Must | Should | Could |
|:---|:-----|:-------|:------|
| 機能性 | モジュール一覧と役割 | 使用例コード | デモスクリプト |
| 品質 | 正確な情報 | mermaid図 | テスト網羅率 |
| 性能 | N/A | N/A | N/A |

---

## STAGE 3: Blueprint [S4 Praxis]

### 成果物

1. **`mekhane/fep/README.md`** — 統合ドキュメント
   - モジュール一覧表
   - アーキテクチャ mermaid 図
   - 使用例コードスニペット
   - FEP Agent 連携フロー

2. **追加統合テスト** (optional)
   - `test_fep_integration.py` — モジュール間連携テスト

### 変更対象

| 操作 | ファイル |
|:-----|:---------|
| [NEW] | `mekhane/fep/README.md` |
| [OPTIONAL] | `mekhane/fep/tests/test_fep_integration.py` |

---

## STAGE 4: Devil's Advocate

| 視点 | 回答 |
|:-----|:-----|
| Feasibility | ✅ 既存コードから生成可能 |
| Necessity | ✅ 297テストあるがドキュメントなし |
| Alternatives | ❌ SKILL.mdは別レイヤー |
| Risks | ⚠️ 情報が古くなる可能性 → バージョン記載で対応 |

---

## 判定

```
┌─[Hegemonikón]──────────────────────────────────────────┐
│ /s v4.1 完了                                           │
│ STAGE 0: ✅ Scale: Meso (モジュール間統合)             │
│ STAGE 1: ✅ Strategy: Explore, Plan: B Robust         │
│ STAGE 2: ✅ Rubric: Must/Should 設定済み              │
│ STAGE 3: ✅ Blueprint: README.md                      │
│ STAGE 4: ✅ Devil's Advocate: All PASS                │
└────────────────────────────────────────────────────────┘
```

**実行へ進む: README.md 作成**
