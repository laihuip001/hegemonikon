---
description: Gemini の作業を Claude が監査する。Cross-Model Verification による品質保証。
hegemonikon: Akribeia
modules: [A2, A4]
skill_ref: ".agent/skills/akribeia/a2-krisis/SKILL.md"
pair: "/sop"
tempo: Fast
parent: "/dia"
version: "3.1"
lcm_state: beta
lineage: "v3.0 + 再実行提案フロー → v3.1"
anti_skip: enabled
sel_enforcement:
  "+":
    description: "MUST execute all 5 layers with detailed findings"
    minimum_requirements:
      - "L1-L5 全層チェック 必須"
      - "発見事項の詳細記載 必須"
      - "SEL 遵守率表示 必須"
  "-":
    description: "MAY provide summary only"
    minimum_requirements:
      - "総合判定のみ"
  "*":
    description: "MUST meta-analyze: why this audit approach?"
    minimum_requirements:
      - "監査手法のメタ分析"
ccl_signature: "/vet+"
---

# /vet: 監査ワークフロー（Verification）v3.0

> **Hegemonikón Module**: A2 Krisis（検証）
> **目的**: Gemini の作業結果を Claude が第三者視点で監査し、品質を保証する
> **設計根拠**: Cross-Model Verification（幻覚検出 92.6% 精度、最大 35% 品質改善）
> **v3.0 新機能**: L5 SEL 遵守層追加

---

## STEP 0: SKILL.md 読込（必須・省略不可）

> **環境強制**: このステップを飛ばして PHASE に進んではならない。
> パスは以下にリテラルで記載されている。「パスがわからない」は発生しない。

// turbo

```
view_file /home/makaron8426/oikos/hegemonikon/.agent/skills/akribeia/a2-krisis/SKILL.md
```

---

## 発動条件

| トリガー | 説明 |
| :-------- | :---- |
| `/vet` | Gemini 直前作業の監査を開始 |
| `/vet [対象]` | 特定のファイル/タスクを監査 |
| `/vet full` | 全数監査モード（時間がかかる） |
| `/vet sel` | SEL 遵守のみチェック |

---

## 監査5層フレームワーク

| 層 | 検証内容 | Claude の問い |
| :- | :------- |--------------|
| **L1: 成果物正確性** | ファイル存在、スキーマ一致、内容整合性 | 「作ったものは正しいか？」 |
| **L2: プロセス遵守** | 手順通りか、スキップはないか | 「手順を守ったか？」 |
| **L3: 計画一致** | やると言ったことをやったか | 「計画と一致するか？」 |
| **L4: 品質基準** | コード品質、ドキュメント品質、命名規則 | 「品質は十分か？」 |
| **L5: SEL 遵守** | CCL 演算子の minimum_requirements 充足 | 「演算子要件を満たしたか？」 |

---

## 監査チェックリスト

```markdown
## L1: 成果物正確性
- [ ] 変更対象ファイルが全て存在する
- [ ] ファイルパスが正しい（古いパス参照なし）
- [ ] 内容が意図通り（削除すべきものが残っていないか）

## L2: プロセス遵守
- [ ] task.md の項目を全て実行した
- [ ] 指示を忘れていない（日本語出力、命名規則など）
- [ ] 不要な変更をしていない（スコープ逸脱なし）

## L3: 計画一致
- [ ] implementation_plan.md の項目を達成した
- [ ] 予定外の変更は合理的に説明できる

## L4: 品質基準 (C-4 消化)

> **Origin**: C-4 冷徹なコード監査 を消化

- [ ] コード/ドキュメントの品質が許容範囲
- [ ] 命名規則に従っている
- [ ] 古い情報への参照がない

### Code Smells 検知
- [ ] Magic Values がない（ハードコード禁止）
- [ ] 変数名が具体的（`data`, `tmp` 禁止）
- [ ] ネストが深すぎない（循環的複雑度監視）
- [ ] DRY 原則遵守（重複コードなし）

### Type Safety
- [ ] 型定義が厳格（`Any` 禁止）
- [ ] エラーを握りつぶしていない
- [ ] Edge Cases 考慮（Null/None/Empty）

### Modern Syntax
- [ ] 言語の最新機能を活用
```

---

## 重大度分類

| 重大度 | 定義 | 具体例 | 対応 |
| :---- |------| :---- |------|
| **Critical** | システム破損/データ損失/ルール違反 | 指示無視、ファイル誤削除、英語出力 | 🔴 即座に報告、ユーザー承認必須 |
| **Major** | 機能部分的障害/品質低下 | パス間違い、計算ミス、項目漏れ | 🟡 是正案提示、修正実行要求 |
| **Minor** | スタイル/最適化問題 | 冗長な記述、軽微なフォーマット | 🟢 記録のみ、次回改善提案 |

---

## 監査プロセス

```
/vet 発動
  ↓
[Step 1] 入力収集
  - Gemini の作業サマリー取得
  - 変更ファイルリスト取得
  - 関連計画ドキュメント確認
  ↓
[Step 2] L1-L4 チェック実行
  - 各層のチェックリストを順次検証
  - ファイル存在確認、内容検証、計画照合
  ↓
[Step 3] L5 SEL 遵守チェック (v3.0 新機能)
  - sel_validator.py を使用
  - CCL 演算子の minimum_requirements を照合
  - 遵守率 (score) を計算
  ↓
[Step 4] 問題分類
  ├→ 問題なし → [PASS] 監査完了
  ├→ Minor のみ → [PASS with Notes] 改善提案記録
  ├→ Major → [REVIEW REQUIRED] 是正案提示
  ├→ Critical → [ESCALATE] ユーザーへ即座報告
  └→ SEL 非遵守 → [RE-EXECUTE] 再実行提案へ
  ↓
[Step 5] 監査レポート出力
```

---

## L5 SEL チェック詳細 (v3.0)

### 検証方法

```python
from mekhane.ccl.sel_validator import SELValidator

validator = SELValidator()
result = validator.validate(workflow="boot", operator="+", output=response)

if not result.is_compliant:
    print(f"⚠️ 非遵守: {result.missing_requirements}")
    print(f"📊 遵守率: {result.score:.0%}")
```

### 再実行提案フロー

```
SEL 非遵守検出
  ↓
[判定] 遵守率チェック
  ├→ score >= 80% → 手動補完オプション
  │   "足りない要素を手動で追加しますか？"
  │   → Y: 追加ガイダンス表示
  │   → N: 記録して継続
  ├→ score < 80% → 再実行推奨
  │   "遵守率が低いため再実行を推奨"
  │   → Y: 同じ CCL を再実行
  │   → N: ユーザー判断に委ねる
  └→ score < 50% → 強制再実行警告
      "⚠️ 重大な SEL 違反 - 再実行を強く推奨"
```

### 出力形式 (L5 追加)

```markdown
## L5: SEL 遵守

| CCL | 遵守率 | 状態 | 不足要件 |
|:----|:-------|:-----|:---------|
| /boot+ | 80% | ⚠️ | 変化追跡表示 |
| /zet+ | 100% | ✅ | - |

**推奨アクション**: 
- `/boot+` の変化追跡 (/boot') を手動で追加
```

---

## 出力形式

```markdown
## 監査レポート: /v

**対象**: [Gemini の作業内容]
**監査日時**: [YYYY-MM-DD HH:MM]

---

### 監査結果サマリー

| 層 | 結果 | 発見数 |
| :-- | :---- | :------ |
| L1: 成果物正確性 | ✅/⚠️/❌ | X件 |
| L2: プロセス遵守 | ✅/⚠️/❌ | X件 |
| L3: 計画一致 | ✅/⚠️/❌ | X件 |
| L4: 品質基準 | ✅/⚠️/❌ | X件 |

**総合判定**: ✅ PASS / ⚠️ PASS with Notes / 🟡 REVIEW REQUIRED / 🔴 ESCALATE

---

### 発見事項

#### ⚠️ Major (修正推奨)

| # | 問題 | 場所 | 推奨修正 |
| :- | :---- |------| :-------- |
| 1 | [問題の説明] | [ファイル:行] | [修正案] |

#### 📝 Minor (記録のみ)

- [軽微な問題の列挙]

---

### 推奨アクション

1. [具体的な修正指示]
2. [次のステップ]

---

**修正を実行しますか？** [y/n]
```

---

## エスカレーション基準

| 状況 | 対応 |
| :---- |------|
| **Critical 発見** | 即座にユーザー通知、修正は承認後 |
| **Major 3件以上** | ユーザー通知、再実行を検討 |
| **同一エラー再発** | SOP 更新を提案 |
| **判断困難** | ユーザーに判断を委ねる |

---

## 連携ワークフロー

| 前工程 | → /vet | 後工程 |
| :------ | :---- | :------ |
| Gemini 作業完了 | 監査実行 | 修正 or 承認 |
| `/do` 完了 | 自動的に `/v` 推奨 | コミット前確認 |

---

## ベストプラクティス

1. **Gemini 作業後は必ず `/v`** — 監査なしコミット禁止
2. **Cross-Model Audit**: IDE でモデルを切替えて相互監査（Gemini↔Claude）
3. **トークン節約**: Minor は記録のみ、Major/Critical に集中
4. **修正権限の明確化**: Claude は提案のみ、実行は承認後
5. **SOP 更新**: 同一エラー 3 回で Gemini 向け SOP に追記

---

## Hegemonikon 連携

| Module | 役割 |
| :------ | :---- |
| **A2 Krisis** | 検証実行（本体） |
| **S1 Metron** | 作業サマリーの知覚 |
| **O1 Noēsis** | 計画との因果検証 |
| **H4 Doxa** | 監査履歴の記録 |

---

*Cross-Model Verification: 異なるモデル家族による検証は、自己批判より 35% 高精度*

---

## Hegemonikon Status

| Module | Workflow | Status |
|:-------|:---------|:-------|
| A2 Krisis | /vet | v2.1 Ready |

---

*v2.1 — C-4 消化 + Anti-Skip Protocol (2026-01-28)*
