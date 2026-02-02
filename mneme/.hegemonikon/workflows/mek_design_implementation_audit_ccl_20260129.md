# /mek+ 設計-実装整合性監査 CCL

> **Hegemonikón**: S2 Mekhanē (inve 派生) + 深化モード
> **生成日時**: 2026-01-29T22:11
> **要件**: Hegemonikón の設計思想と現在の実装との乖離を精査する CCL コード

---

## 1. CCL監査プログラム CANON-ΔELΤΑ

> **ギリシャ語**: ΔELΤΑ = 差異 (差分を暴く監査の暗号名)

```ccl
PROGRAM: CANON-ΔELΤΑ (Design-Implementation Gap Audit)
VERSION: 1.0
INTENT: "核心原則の実装乖離を特定し、修正優先度を決定する"

# ========================================
# PHASE 1: 正典抽出 (Canon Extraction)
# ========================================

/noe+s1@4 ?s3 [philosophy]
# 解釈:
#   - /noe+ : 深い認識（詳細モード）
#   - s1@4  : 人生レベルの抽象度で観る
#   - ?s3   : 基準 (Stathmos) を満たすか問う
#   - [philosophy] : 哲学セクションのみ抽出
#
# 期待出力: Hegemonikón の核心設計思想リスト

_

# ========================================
# PHASE 2: 実装スキャン (Implementation Scan)
# ========================================

/noe+p1 [implementation]
# 解釈:
#   - /noe+ : 深い認識（詳細モード）
#   - p1    : 領域 (Khōra) を広げて全実装を観る
#   - [implementation] : 実装関連のみ抽出
#
# 期待出力: 現在の実装状態リスト

_

# ========================================
# PHASE 3: 差分検出 (Delta Detection)
# ========================================

/dia+ --mode=cold-mirror *X
# 解釈:
#   - /dia+        : A2 Krisis 判定力（詳細モード）
#   - --mode=cold-mirror : 冷酷な自己監査モード
#   - *X           : 全関係層との融合（Universal X-Fusion）
#
# 期待出力:
#   - 乖離リスト (Gap List)
#   - 各乖離の重大度 (Critical/High/Medium/Low)
#   - 根本原因仮説

_

# ========================================
# PHASE 4: 根本原因分析 (Root Cause Analysis)
# ========================================

/why! ~/zet+
# 解釈:
#   - /why!  : Five Whys を全派生展開
#   - ~      : 振動（探求層と往復）
#   - /zet+  : 問いの深掘り
#
# 期待出力: 乖離の根本原因マップ

_

# ========================================
# PHASE 5: 優先順位決定 (Priority Triage)
# ========================================

/bou+*sta ?h2
# 解釈:
#   - /bou+ : 意志明確化（詳細モード）
#   - *sta  : S3 Stathmos（基準）と融合
#   - ?h2   : 確信度 (Pistis) を問う
#
# 期待出力:
#   - 優先修正リスト
#   - 各項目の確信度スコア

_

# ========================================
# PHASE 6: 修正計画生成 (Remediation Plan)
# ========================================

/s+ _/ene ?k1
# 解釈:
#   - /s+   : S-series 詳細設計
#   - _     : シーケンス（完了後に次へ）
#   - /ene  : O4 Energeia 実行計画
#   - ?k1   : K1 Eukairia（今がタイミングか）を問う
#
# 期待出力: 具体的な修正アクションプラン

# ========================================
# FINAL OUTPUT
# ========================================

ARTIFACT: audit_canon_delta_{date}.md
LOCATION: /mneme/.hegemonikon/workflows/
```

---

## 2. CCL式の全体構造（ワンライナー版）

```ccl
/noe+s1@4?s3[philosophy] _/noe+p1[implementation] _/dia+--mode=cold-mirror*X _/why!~/zet+ _/bou+*sta?h2 _/s+_/ene?k1
```

---

## 3. 各フェーズの詳細設計 (/mek+ 深化出力)

### 3.1 PHASE 1: 正典抽出

| 項目 | 詳細 |
|:-----|:-----|
| **定理** | O1 Noēsis (nous 派生) |
| **対象** | 設計思想文書 (7 Core Principles) |
| **抽出項目** | - FEP 原理との整合 (L0-1.75) |
|  | - Universal X-Fusion |
|  | - 60要素均衡 |
|  | - 消化原則 |
|  | - 3層アーキテクチャ |
|  | - 認知負荷軽減 |
|  | - Self-Completing System |

### 3.2 PHASE 2: 実装スキャン

| スキャン対象 | パス |
|:-------------|:-----|
| ワークフロー | `.agent/workflows/*.md` |
| スキル | `.agent/skills/**/*.md` |
| Python実装 | `hegemonikon/mekhane/**/*.py` |
| KI アーティファクト | `.gemini/antigravity/knowledge/**/*.md` |
| 設定 | `.agent/tools.yaml` |

### 3.3 PHASE 3: 差分検出マトリクス

| 検出対象 | 乖離タイプ | 検出方法 |
|:---------|:-----------|:---------|
| **原則-実装** | 実装漏れ | 正典にあるが実装にない |
| **実装-原則** | 野良実装 | 実装にあるが正典にない |
| **宣言-動作** | 動作乖離 | 宣言は正しいが動作が違う |
| **依存-独立** | 統合不足 | 独立して動くべきが連携してる |
| **暗黙-明示** | 暗黙依存 | 暗黙の前提が文書化されてない |

### 3.4 PHASE 4: Five Whys テンプレート

```text
Gap: {乖離の概要}
  Why 1: なぜこの乖離が存在するか？ → {理由1}
  Why 2: なぜ{理由1}が起きたか？ → {理由2}
  Why 3: なぜ{理由2}が起きたか？ → {理由3}
  Why 4: なぜ{理由3}が起きたか？ → {理由4}
  Why 5: なぜ{理由4}が起きたか？ → {根本原因}
```

### 3.5 PHASE 5: 優先順位マトリクス

| 優先度 | 条件 | アクション |
|:-------|:-----|:-----------|
| **P0 Critical** | ユーザー影響 + 簡単修正 | 即日修正 |
| **P1 High** | 設計思想の核心に反する | 今週中に修正 |
| **P2 Medium** | 改善により体験向上 | 次スプリント |
| **P3 Low** | あると良い | バックログ |

---

## 4. 監査対象の核心原則 (7 Canon Principles)

> /noe+s1@4 で抽出すべき「正典」

| # | 原則 | 出典 | 期待される実装 |
|:-:|:-----|:-----|:---------------|
| 1 | **FEP 基盤** | L0-1.75 | 全定理が pymdp で実行可能 |
| 2 | **Universal X-Fusion** | impl_standards | `/W` = `/W*X` が暗黙動作 |
| 3 | **60要素均衡** | framework_v2.2 | 7公理, 24定理, 36関係の総和 |
| 4 | **消化原則** | digestion_principle | 追加よりも同化 |
| 5 | **3層アーキテクチャ** | workflow_governance | Skill = 正本, WF = 手順, KI = 記録 |
| 6 | **認知負荷軽減** | ccl_philosophy | 最小打鍵で最大認知 |
| 7 | **CCL = 認知制御言語** | lot_rejection | 思考表現ではなく思考制御 |

---

## 5. 実行コマンド

```bash
# ワンライナーで全監査を実行
/noe+s1@4?s3[philosophy] _/noe+p1[implementation] _/dia+--mode=cold-mirror*X _/why!~/zet+ _/bou+*sta?h2 _/s+_/ene?k1
```

**または段階実行:**

```bash
# Step 1: 正典抽出
/noe+s1@4 ?s3 [philosophy]

# Step 2: 実装スキャン
/noe+p1 [implementation]

# Step 3: 差分検出
/dia+ --mode=cold-mirror *X

# Step 4: 根本原因分析
/why! ~/zet+

# Step 5: 優先順位決定
/bou+ *sta ?h2

# Step 6: 修正計画
/s+ _/ene ?k1
```

---

## 6. Mekhanē 生成メタデータ

| 項目 | 値 |
|:-----|:---|
| 派生 | **inve** (発明・創出) |
| モード | `/mek+` (詳細生成) |
| アーキタイプ | Precision + Safety |
| 品質スコア | 9/10 |
| 生成根拠 | 設計-実装乖離は「発見」問題であり、既存部品の組み合わせでは対応不可 |

---

## 7. X-series 連携

| 関係 | 次ワークフロー |
|:-----|:---------------|
| **X-SA** | 監査後は実装へ `/s → /ene` |
| **X-AO** | 判定後は認識へ `/dia → /noe` (再確認) |
| **X-OS** | 認識後は設計へ `/noe → /s` (修正設計) |

---

*Generated by /mek+ (inve) | Hegemonikón S2 Mekhanē*
