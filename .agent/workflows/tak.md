---
description: タスク/TODO/アイデアを自動で整理・分類・見積もり・期限別Must/Should提示
hegemonikon: Kairos
modules: [K2, O2, S3]
skill_ref: null
version: "1.2"
lcm_state: stable       # draft | beta | stable | deprecated
lineage: "v1.1 + 5項目プリプロセス統合 (Flow AI 消化) → v1.2"
anti_skip: enabled
ccl_signature: "/tak+"
derivatives: [tria, eise, kair]
cognitive_algebra:
  "+": "詳細分析：全フェーズ展開、依存・工数を詳細計算"
  "-": "高速分類：Must/Should のみ、見積なし"
  "*": "メタ分析：分類ロジック自体を問う"
sel_enforcement:
  "+":
    description: "MUST execute all 8 phases with dependency and estimation"
    minimum_requirements:
      - "全8フェーズ展開 必須"
      - "依存関係 必須"
      - "工数見積 必須"
  "-":
    description: "MAY provide Must/Should only without estimation"
    minimum_requirements:
      - "Must/Should のみ"
  "*":
    description: "MUST meta-analyze: is this classification logic correct?"
    minimum_requirements:
      - "分類ロジックのメタ分析"
---

# /tak: タスク管理ワークフロー (Task Orchestration) v1.0

> **目的**: タスク/TODO/アイデアを整理し、期限別Must/Should形式で提示
> **発動条件**: 雑多なタスクを投げ込んだ時、計画を立てたい時
> **本質**: バイブ（ノリ）を具体（6W3H）に着地させる機構

---

## Cognitive Algebra

| Operator | Meaning | Output |
|:---------|:--------|:-------|
| `/tak+` | **Deepening** | 詳細分析: 全8フェーズ展開、依存・工数・不足情報を詳細計算 |
| `/tak-` | **Reduction** | 高速分類: 期限バケットのみ、見積なし |
| `/tak*` | **Expansion** | メタ分析: 「この分類ロジックは正しいか」を問う |

---

## 発動条件

| トリガー | 説明 |
|:---------|:-----|
| `/tak` | タスク管理ワークフロー開始（派生自動選択） |
| `/tak --derivative=tria` | トリアージモード（緊急度重視） |
| `/tak --derivative=eise` | アイゼンハワーモード（重要度×緊急度） |
| `/tak --derivative=kair` | カイロスモード（好機・タイミング重視） |

---

## 派生モード

| 派生 | 意味 | 適用場面 |
|:-----|:-----|:---------|
| **tria** | トリアージ | 大量タスク投入時、迅速な振り分け |
| **eise** | アイゼンハワー | 戦略的整理、重要度評価 |
| **kair** | カイロス | 機会損失回避、タイミング重視 |

---

## 8フェーズ処理パイプライン

```text
入力: 雑多なタスク/TODO/アイデア
  ↓
[PHASE 0] PREPROCESS — 5項目構造化 (v1.2 新規)
  └→ 曖昧・口語を構造化フォーマットに変換
  ↓
[PHASE 1] INTAKE — 入力解析
  └→ 箇条書き分割、キーワード抽出、期限検出
  ↓
[PHASE 2] CLASSIFY — 優先度・緊急度分類
  └→ Eisenhower Matrix: 緊急度 × 重要度
  ↓
[PHASE 3] STRUCTURE — 階層化
  └→ プロジェクト → エピック → タスク
  ↓
[PHASE 4] DEPEND — 依存関係解決
  └→ FS/SS/FF/BLOCKER 検出
  ↓
[PHASE 5] GAP — 不足情報分析
  └→ SCOPE/TECHNICAL/RESOURCE/DEADLINE 特定
  ↓
[PHASE 6] ESTIMATE — 工数見積
  └→ XS/S/M/L/XL (T-Shirt Sizing)
  ↓
[PHASE 7] SCHEDULE — スケジュール照合
  └→ 可用時間との照合、オーバーフロー検出
  ↓
[PHASE 8] OUTPUT — Must/Should 提示
  └→ 期限別Must/Shouldリスト
  ↓
出力: 整理されたタスクリスト
```

---

## PHASE 0: 5項目プリプロセス (v1.2)

> **Origin**: [laihuip001/Flow](https://github.com/laihuip001/Flow) 消化
> **目的**: 雑な自然言語を LLM 実行可能形式に変換

### 原則（絶対遵守）

| # | 原則 | 違反時 |
|:--|:-----|:-------|
| 1 | **意味同一性**: 追加/削除/改変禁止 | やり直し |
| 2 | **命令強度同一性**: 弱体化禁止 | やり直し |
| 3 | **ニュアンス保持**: 温度感を落とさない | やり直し |
| 4 | **出力は整形結果のみ**: 解説・注釈禁止 | やり直し |

### 5項目フォーマット

```text
【目的】
（1〜2行で、元の目的のみ）

【対象】
（元にある対象を列挙）

【実行姿勢／評価態度】
（元にある姿勢・批評態度のみ）

【実行指示】
（具体命令を箇条書き。粒度・徹底度を落とさない）

【出力要件】
（Claudeが提示すべき成果物の形。元から導ける範囲のみ）
```

### 発動条件

```python
def should_preprocess(input_text: str) -> bool:
    """5項目プリプロセスが必要か判定"""
    indicators = [
        len(input_text) > 100,          # 長文
        "⇛" in input_text,              # 省略記号
        "〜" in input_text,              # 曖昧語
        "やって" in input_text,         # 口語
        "とりあえず" in input_text,     # 曖昧指示
    ]
    return any(indicators)
```

### 変換例

**Before**:

```
タスクやtodo、思いつきのアイデアをぶん投げたら、自動的に優先順位や緊急度を
分類してくれる機構 ⇛ 期限別Must/Should提示
```

**After**:

```
【目的】
タスク/TODO/アイデアを投入すると、自動で整理・分類・見積もり・期限別Must/Should提示する機構を製作する。

【対象】
- 投げ込まれる入力：タスク、TODO、思いつきのアイデア
- 期限区分：今日中／三日以内／今週中／3週間以内／2ヶ月以内

【実行姿勢／評価態度】
- 分類・構造化・依存整理・工数見積・期限別の実行計画化まで一貫して行うこと

【実行指示】
- 入力されたタスク/TODO/アイデアを、自動的に「優先順位」と「緊急度」で分類せよ
- 工数を見積もり、スケジュールと照らし合わせて期限別Must/Shouldを提示せよ

【出力要件】
- 機構としての全体像を提示せよ
- 入力例と期待出力例を提示せよ
```

---

## 期限バケット

| 区分 | タイムボックス | 色 |
|:-----|:--------------|:---|
| 🔴 TODAY | 今日中 | Critical |
| 🟠 3DAYS | 三日以内 | High |
| 🟡 WEEK | 今週中 | Medium |
| 🟢 3WEEKS | 3週間以内 | Normal |
| 🔵 2MONTHS | 2ヶ月以内 | Low |

---

## 使用方法

### 基本

```
/tak
- API認証がバグってるのでなおす（急ぎ）
- 来週のv1.2リリースの準備
- 新機能のプロトタイプ作りたい
- Rustの勉強
```

### プログラム呼び出し

```python
from mekhane.orchestration import TaskIntakeParser, TaskOrchestrator
from mekhane.orchestration.task_output import format_output

# パース
parser = TaskIntakeParser()
tasks = parser.parse(raw_input)

# 処理
orchestrator = TaskOrchestrator()
result = orchestrator.process(tasks)

# 出力
print(format_output(result))
```

---

## ワークフロー連携

| 連携先 | 連携内容 |
|:-------|:---------|
| `/bou` | 目的参照 → 重要度評価 |
| `/chr` | 時間評価 → スケジュール照合 |
| `/sop` | 調査実行 → 不足情報収集 |
| `/ene` | 実行 → Must タスク着手 |

---

## O/S/H/P/K/A 体系における位置

```text
K2 Chronos（時間）← 期限・スケジュール評価
  └→ /tak は K2 の実用化
      
O2 Boulēsis（意志）← 目的・優先順位
  └→ 重要度評価に連携

S3 Stathmos（基準）← 評価基準
  └→ Must/Should の判定基準
```

---

## Artifact 自動保存

### 保存先

```
/home/makaron8426/oikos/mneme/.hegemonikon/workflows/tak_<date>.md
```

---

*v1.0 — Task Orchestration Workflow (2026-01-30)*
