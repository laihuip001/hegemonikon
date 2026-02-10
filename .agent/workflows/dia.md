---
description: A2 Krisis（判定力）を発動する抽象コマンド。敵対的レビュー機能統合。
hegemonikon: A2 Krisis
version: "7.0"
skill_ref: ".agent/skills/akribeia/a2-krisis/SKILL.md"
lcm_state: stable       # draft | beta | stable | deprecated
layer: "Δ"
derivatives: [aff, neg, epo, root, devil, steelman, counterfactual, cold_mirror, deliberative, explore]
trigonon:
  series: A
  type: Pure
  theorem: A2
  coordinates: [C, U]
  bridge: []
  anchor_via: [H, K]
  morphisms:
    ">>H": [/pro, /pis, /ore, /dox]
    ">>K": [/euk, /chr, /tel, /sop]
cognitive_algebra:
  "+": 詳細判定（証拠/論拠/反論を完全展開）
  "-": 判定要約（PASS/FAIL + 1行理由）
  "*": メタ判定（判定プロセス自体を判定）
sel_enforcement:
  "+":
    minimum_requirements:
      - "証拠セクション: 具体的データ/事実を引用"
      - "論拠セクション: 推論の連鎖を明示"
      - "反論セクション: 最も強い反論を提示"
      - "確信度: [確信/推定/仮説] を明示"
  "-":
    minimum_requirements:
      - "PASS/FAIL + 1行理由のみ"
---

# /dia: A2 Krisis 発動コマンド

> **Hegemonikón**: A2 Krisis（判定力）
> **層**: Δ（デルタ）— 抽象コマンド
> **役割**: 判定・検証・批評の能力を発動する
>
> **制約**: モード未指定時は自動選択ロジックを使用する。判定後は必ず確信度を明示すること。

---

## サブモジュール

| ファイル | 内容 |
|----------|------|
| [basic-modes.md](dia/basic-modes.md) | 基本モード (aff/neg/root/devil/steelman/counterfactual) |
| [advanced-modes.md](dia/advanced-modes.md) | 高度モード (epochē/audit/panorama/cross-model/cold_mirror/deliberative) |

---

## Cognitive Algebra

| Operator | Meaning | Output |
|:---------|:--------|:-------|
| `/dia+` | **Deepening** | 詳細判定: 証拠、論拠、反論を完全展開 |
| `/dia-` | **Reduction** | 要約判定: PASS/FAIL + 1行理由 |
| `/dia*` | **Expansion** | メタ判定: 「この判定は正当か」を判定 |

---

## モード一覧

### 基本モード

| モード | 説明 | 発動 |
|:-------|:-----|:-----|
| `aff` | 肯定的判定 | 「良い点は」 |
| `neg` | 否定的判定 | 「問題点は」 |
| `root` | 根源探索 | 「そもそも」 |
| `devil` | 悪魔の代弁者 | 「反論して」 |
| `steelman` | 最強論証 | 「最強の形で」 |
| `counterfactual` | 反実仮想 | 「もし」 |

### 高度モード

| モード | 説明 | 発動 |
|:-------|:-----|:-----|
| `epochē` | 判断停止 | 「確信度を宣言」 |
| `audit` | 消化品質診断 | 「消化できてる？」 |
| `panorama` | 6層メタ認知スキャン | 「盲点」「見落とし」 |
| `cross-model` | Cross-Model Verification | 「別のAI」 |
| `cold_mirror` | 冷徹な鏡 | 「厳しく」 |
| `deliberative` | 三視点反復改善 | 「反復改善」 |
| `explore` | 探索的テスト (UI) | 「触って壊して」「UIテスト」 |

---

## STEP 0: SKILL.md 読込（必須・省略不可）

> **環境強制**: このステップを飛ばして PHASE に進んではならない。
> パスは以下にリテラルで記載されている。「パスがわからない」は発生しない。

// turbo

```
view_file /home/makaron8426/oikos/hegemonikon/.agent/skills/akribeia/a2-krisis/SKILL.md
```

---

## STEP 0.5: 適用基準（Self-Refine 腐食効果対策）

> **警告**: Snorkel 研究 (2025) により、簡単な問題に Self-Refine を適用すると
> 正答率が **98% → 57%** に低下することが判明（腐食効果）。
> /dia は Self-Refine の一形態であるため、**適用基準を守ること**。

| タスク複雑度 | /dia 適用 | 理由 |
|:-----------|:---------|:-----|
| **瑣末** (typo修正、1行変更) | ❌ 不要 | 腐食リスク > 改善効果 |
| **中程度** (関数追加、バグ修正) | ⚠️ `/dia-` のみ | PASS/FAIL + 1行理由で十分 |
| **複雑** (設計変更、新機能) | ✅ `/dia` or `/dia+` | 詳細レビューが正当化される |
| **クリティカル** (安全性、不変資料) | ✅ `/dia+` 必須 | 腐食リスクより見落としリスクが大きい |

> **自問**: 「この /dia は腐食を起こさないか？ タスクの複雑度に見合っているか？」

---

## 発動条件

| トリガー | 動作 |
|:---------|:-----|
| `/dia` | 状況に応じてモード自動選択 |
| `/dia --mode={mode}` | 特定モード実行 |
| `/dia {mode}` | 特定モード実行（省略形） |

---

## 自動選択ロジック

> モード未指定時、文脈から最適モードを提案する。

```yaml
if 統合・マージ・吸収 の話題:
  → --mode=audit (消化品質診断)

if Gemini/Jules の成果物:
  → --mode=cross-model (Cross-Model 監査)

if 空虚語・抽象論 を検出:
  → Buzzword Guillotine 発動

if Cone.needs_devil == True (V > 0.3):
  → --mode=devil (FEP devil_attack 自動発動)

if 確信度が LOW or 認識限界を検出:
  → --mode=epochē (判断停止)

if 盲点・見落とし を問う:
  → --mode=panorama (6層スキャン)

if 認知歪み・論理的欠陥・甘え を指摘すべき:
  → --mode=cold_mirror (冷徹な鏡)

default:
  → ユーザーに確認（提案付き）
```

---

## 自動提案の出力形式

| 項目 | 内容 |
|:-----|:-----|
| 文脈分析 | 検出したキーワード/パターン |
| 推奨モード | `--mode={mode}` |
| 理由 | なぜこのモードか |
| 確認 | このまま実行 / 代替モード / キャンセル |

---

## Hegemonikón Status

| Module | Workflow | Status |
|:-------|:---------|:-------|
| A2 Krisis | /dia | v7.1 Ready |

> **制約リマインダ**: 判定後は確信度を明示すること [Certain/Estimated/Hypothetical]。

---

*v7.1 — FBR 適用 (2026-02-07)*

---

## Post-Check (環境強制)

> **`+` モード時のみ自動発動。** 出力が sel_enforcement の minimum_requirements を満たすか検証。

// turbo

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python scripts/wf_postcheck.py --wf dia --mode "+" --text "$DIA_OUTPUT"
```

> FAIL 時は不足を補完してから Creator に提示。PASS するまでループ。

---

## @complete: 射の提案 (暗黙発動 L1)

> WF完了時、`/x` 暗黙発動プロトコルにより射を提案する。
> 計算ツール: `python mekhane/taxis/morphism_proposer.py dia`

```
/dia 完了 → @complete 発動
→ 結果に確信がありますか？ (Y: Anchor優先 / N: Bridge優先 / 完了)
```
