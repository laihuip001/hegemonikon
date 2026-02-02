# /s: dev-rules リポジトリ消化計画

> **発動**: /s ワークフロー（5-STAGE 認知プロセス）
> **対象**: <https://github.com/laihuip001/dev-rules>

---

## STAGE 0: Blindspot + Scale Detection [S1 Metron]

### Phase 0.0: Prior Art Check

| 確認事項 | 結果 |
|:---------|:-----|
| Hegemonikón に同等機能あり？ | ✅ 多数重複あり |
| 消化済みか？ | ❌ 未消化 |

### Phase 0.1: Blindspot Check

| カテゴリ | 質問 | 結論 |
|:---------|:-----|:-----|
| 🎯 Framing | 「消化」で正しいか？ | ✅ 正しい。dev-rules は Hegemonikón の前身 |
| 📐 Scope | どこまで消化？ | constitution + modules 全体 |
| 🔗 Dependencies | 見落とし？ | diary/ (ツール) は別途検討 |

### Phase 0.2: Scale Determination

**🌍 Macro** — 21モジュール + 7レイヤーの全面統合

---

## STAGE 1: Strategy Selection [S2 Mekhanē]

### dev-rules 構造

```text
dev-rules/
├── constitution/           # 7レイヤー (G-1〜G-7)
│   ├── 00_orchestration.md
│   ├── 01_environment.md
│   ├── 02_logic.md
│   ├── 03_security.md
│   ├── 04_lifecycle.md
│   ├── 05_meta_cognition.md
│   └── 06_style.md
│
├── prompts/modules/        # 21モジュール
│   ├── C*-*.md             # Critical (監査/修正)
│   ├── Q*-*.md             # Quality
│   ├── A*-*.md             # Analysis
│   └── ...
│
├── GEMINI.md               # Agent Persona
└── ARCHITECTURE.md         # 構造図
```

### Hegemonikón との対応マッピング

| dev-rules | Hegemonikón | 関係 |
|:----------|:------------|:-----|
| G-1 Environment | P1 Khōra (場) | **重複** |
| G-2 Logic | S3 Stathmos (基準) | **重複** |
| G-3 Security | A2 Krisis (Epochē) | **重複** |
| G-4 Lifecycle | K2 Chronos (時間) | **重複** |
| G-5 Meta Cognition | O1 Noēsis (認識) | **重複** |
| G-6 Style | S3 Stathmos | **重複** |
| C1-C7 Critical | /dia 敵対的レビュー | **重複** |
| Q1-Q4 Quality | /epi 知識確立 | **部分重複** |
| A2-A9 Analysis | O3 Zētēsis (探求) | **重複** |

### 3プラン

| Plan | 特徴 | リスク |
|:-----|:-----|:-------|
| A 完全廃止 | dev-rules を archive | 価値喪失 |
| **B 栄養素抽出** | 独自価値を Hegemonikón に統合 | 工数増（推奨） |
| C 並行維持 | 両方維持 | 認知負荷 |

**選択: B — 栄養素抽出**

### Y-1 評価

| 層 | 評価 |
|:---|:-----|
| Fast | ✅ 重複解消でシンプル化 |
| Slow | ✅ Hegemonikón に知見が蓄積 |
| Eternal | ✅ 一本化でメンテナンスコスト削減 |

### D-1 評価

| フェーズ | 影響 |
|:---------|:-----|
| T+0 | dev-rules 内のファイルを参照・抽出 |
| T+1 | Hegemonikón の SKILL.md / workflows に統合 |
| T+2 | dev-rules リポジトリを archive |

---

## STAGE 2: Success Criteria [S3 Stathmos]

| 軸 | Must | Should | Could |
|:---|:-----|:-------|:------|
| 機能性 | 独自価値の抽出完了 | 21モジュール全てをマッピング | legacy/ も参照 |
| 品質 | 重複なし | 統合後のテスト | ドキュメント更新 |
| 性能 | N/A | N/A | N/A |

---

## STAGE 3: Blueprint [S4 Praxis]

### 抽出対象（独自価値が高いもの）

| モジュール | 独自価値 | 統合先 |
|:-----------|:---------|:-------|
| Q1 Feynman Filter | 平易化テクニック | A4 Epistēmē 派生 |
| Q3 Occam's Razor | 単純化原則 | S3 Stathmos 派生 |
| Q4 Aesthetic Audit | 美的品質評価 | S3 Stathmos 派生 |
| C1C2 Adversarial | 敵対的レビュー | /dia に統合済み確認 |
| A8 Morphological Matrix | 形態素分析 | O3 Zētēsis 派生候補 |
| R1 Reverse Engineering | リバースエンジニアリング | O3 Zētēsis 派生候補 |

### 実行フェーズ

```text
Phase 1: 分析 (30min)
  ├── 各モジュールの内容を確認
  └── Hegemonikón との重複/補完を判定

Phase 2: 統合 (1-2h)
  ├── 独自価値の高いモジュールを Hegemonikón に統合
  └── SKILL.md または workflows に追加

Phase 3: 検証 (30min)
  ├── 統合後の動作確認
  └── dev-rules リポジトリを archive
```

---

## STAGE 4: Devil's Advocate [/dia]

| 視点 | 質問 | 回答 |
|:-----|:-----|:-----|
| Feasibility | 21モジュール全て必要？ | ❌ 重複多数、抽出は5-6件で十分 |
| Necessity | 本当に消化必要？ | ✅ 前身の知見を継承する価値あり |
| Alternatives | 並行維持？ | ❌ 認知負荷が増える |
| Risks | 見落とし？ | ⚠️ diary/ ツールは別途評価 |

---

## 結論

```text
┌─[Hegemonikon]──────────────────────────────────────────┐
│ /s v4.1 完了                                           │
│ STAGE 0: ✅ Scale: Macro (全面統合)                    │
│ STAGE 1: ✅ Strategy: Exploit, Plan: B (栄養素抽出)    │
│ STAGE 2: ✅ Rubric: 独自価値5-6件抽出                  │
│ STAGE 3: ✅ Blueprint: 3フェーズ実行計画               │
│ STAGE 4: ✅ Devil's Advocate: All PASS                 │
└────────────────────────────────────────────────────────┘
```

---

## 次のアクション

1. **Phase 1**: 各モジュールの詳細確認（独自価値の特定）
2. **Phase 2**: 統合実行
3. **Phase 3**: dev-rules archive

---

*Created: 2026-01-29T13:46*
