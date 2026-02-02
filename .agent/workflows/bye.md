---
description: セッション終了時に引き継ぎドキュメントを生成し、経験を法則化する。次回セッションの/bootで読み込まれる。
hegemonikon: Hormē
modules: [H4]
skill_ref: ".agent/skills/horme/h4-doxa/SKILL.md"
version: "3.3"
lineage: "v3.2 + SEL (Semantic Enforcement Layer) 統合 → v3.3"
derivatives: []
cognitive_algebra:
  "+": "詳細終了。全ステップ展開、法則化、KI生成"
  "-": "高速終了。Handoff最小限、1分で退出"
  "*": "終了のメタ分析。なぜ今終わるか"
sel_enforcement:
  "+":
    description: "MUST execute ALL steps, generate wisdom, recommend KI"
    minimum_requirements:
      - "全ステップ実行"
      - "法則化 (Wisdom Extraction) 必須"
      - "KI 昇格推奨 3+ 件"
      - "X-series 経路記録"
      - "FEP A行列永続化"
      - "Persona 更新"
  "-":
    description: "MAY generate minimal Handoff only"
    minimum_requirements:
      - "Handoff 最小限"
      - "1分で退出"
  "*":
    description: "MUST analyze: why end now?"
    minimum_requirements:
      - "終了理由の分析"
      - "収束確認 (V[])"
anti_skip: enabled
ccl_signature: "/bye+"
---

# /bye ワークフロー

> **Hegemonikón H-series**: H4 Doxa（信念・記憶永続化）
> **/bootの対となるセッション終了コマンド**

---

## 本質

- `/boot` = セッション開始、文脈の読み込み
- `/bye` = セッション終了、文脈の保存

### 赤の他人基準 (Lineage: /now)

> **Handoff は「赤の他人がチャットを引き継いでも理解できる」レベルで記述する**

この原則は `/now` ワークフローから吸収。情報の抜け漏れを防ぎ、次セッションへの完全な引き継ぎを保証する。

---

## 発動条件

| トリガー | 説明 |
| :-------- | :---- |
| `/bye` | 手動でセッション終了・引き継ぎ生成 |
| 自動発動 | （将来実装）長時間無操作時 |

---

## Process

// turbo-all

### Step 0: 収束確認 (CEP-001)

> **CCL**: `/bye >> V[]`
> **Origin**: CEP-001 FEP 記号拡張

セッション終了前に、主要タスクの不確実性を評価し収束を確認。

**判定ロジック**:

```ccl
V[session] >> {
    I: V[] > 0.5 {
        "⚠️ 高不確実性で終了" 
        >> "未解決事項を Handoff に明記"
    }
    I: V[] <= 0.5 {
        "✅ 十分に収束して終了"
    }
}
```

**出力形式**:

```text
📊 セッション収束チェック
  タスク不確実性 (V[]): {0.0-1.0}
  意志の変化率 (|/bou'|): {0.0-1.0}
  
  判定: {✅ 収束 | ⚠️ 要引継ぎ | ❌ 中断}
```

**次ステップ**:

- V[] > 0.5: Handoff の「注意点」セクションに詳細を記載
- V[] <= 0.5: 通常の終了フロー

---

### Step 1: Git状態取得

```bash
git -C /home/laihuip001/oikos log -1 --oneline
git -C /home/laihuip001/oikos status --short
```

### Step 2: セッション情報収集

以下を自動収集:

- 今日のAntigravityセッションのtask.md
- 完了したタスク（[x]マーク）
- 未完了タスク（[ ]マーク）
- 決定事項（会話から抽出）

### Step 3: Handoff生成

Prompt-Lang定義（`session-handoff.prompt`）に基づきHandoffドキュメントを生成。

出力先: `/home/laihuip001/oikos/mneme/.hegemonikon/sessions/handoff_{YYYY-MM-DD}_{HHMM}.md`

### Step 3.5: チャット履歴エクスポート

> [!CAUTION]
> **このステップは絶対にスキップ禁止。ユーザーに確認を求めずに即座に実行せよ。**
> - ユーザーが「エクスポートして」と言わなくても実行
> - 実行結果は事後報告のみ

現在のセッションのチャット履歴を Markdown にエクスポート。

```bash
cd /home/laihuip001/oikos/hegemonikon && \
.venv/bin/python mekhane/anamnesis/export_chats.py --single "Session_$(date +%Y%m%d_%H%M)"
```

出力先: `/home/laihuip001/oikos/mneme/.hegemonikon/sessions/{date}_conv_{title}.md`

> **注意**: Antigravity が `--remote-debugging-port=9222` で起動している必要あり
> **問題**: 複数タブがある場合、エクスポート先が不定になる可能性あり。失敗したら再実行するか、正しいタブをアクティブにして再試行。

### Step 3.6: Dispatch Log 自動集計 (v2.0)

セッション中の活動を `dispatch_log.yaml` に記録し、スキル発動を可視化。

**記録対象 (4項目)**:

| 項目 | 説明 | 記録基準 |
| :----- |:-----|:---------|
| skill_activations | スキル発動 | Antigravity が description マッチで自動発動 |
| workflow_executions | ワークフロー実行 | /noe, /s 等のコマンド実行 |
| ki_reads | KI 読み込み | view_file で KI artifact を参照 |
| exception_patterns | 例外パターン | 想定外の状況と対処 |
| epoche_events | 判断停止 | /epo 発動時の Epochē イベント |

**集計手順**:

1. **振り返り**: 「このセッションで発動したスキルは何か？」を自問
2. **スキル発動判定**:
   - ✅ Antigravity がサジェスト → スキル読み込み → 使用 = 真の自動発動
   - ❌ ワークフロー内で手動参照 = 記録しない（workflow_executions に記録）
3. **Epochē 判定**: 確信度 LOW で判断停止した場合は epoche_events に記録
4. **追記**: dispatch_log.yaml の各セクションに追記
5. **統計更新**: stats セクションのカウントを更新

**記録形式**:

```yaml
skill_activations:
  - timestamp: "{ISO8601}"
    skill: "O1 Noēsis"
    trigger: "user_query:深く考えて"
    outcome: "success"
    session_id: "{conversation_id}"

ki_reads:
  - timestamp: "{ISO8601}"
    ki_name: "Hegemonikón Integrated System"
    artifacts_read: ["overview.md"]
    purpose: "設計確認"
    session_id: "{conversation_id}"

exception_patterns:
  - timestamp: "{ISO8601}"
    situation: "想定外の依存関係"
    action_taken: "手動で解決"
    learned: "事前チェックを追加"
    session_id: "{conversation_id}"

epoche_events:
  - timestamp: "{ISO8601}"
    trigger: "確信度 LOW"
    cause: "訓練データ外のドメイン"
    recommendation: "専門家に確認を推奨"
    hollow: false
    session_id: "{conversation_id}"
```

**出力先**: `/home/laihuip001/oikos/mneme/.hegemonikon/logs/dispatch_log.yaml`

> **Phase B移行判定**: skill_activations >= 50, failure_rate < 10%, exception_patterns >= 3

### Step 3.7: Kairos インデックス投入

生成された Handoff を Kairos インデックスに自動投入。次回 `/boot` で検索可能に。

```bash
python3 /home/laihuip001/oikos/hegemonikon/mekhane/symploke/kairos_ingest.py
```

> **注意**: 最新の1件のみ投入。全件投入は `--all` オプション。

### Step 3.7.1: Handoff インデックス再構築 (v3.0 追加)

> **Origin**: 2026-01-31 P0 改善 — Handoff 検索効率化

Handoff インデックスを再構築し、次回 `/boot` で高速検索を有効化。

```python
from mekhane.symploke.handoff_search import build_handoff_index

# インデックス再構築（新規 Handoff を反映）
adapter = build_handoff_index()
print(f"✅ Handoff インデックス再構築完了: {adapter.count()} 件")
```

**効果**:

- 次回 `/boot` で毎回エンコードせずにキャッシュ済みインデックスを使用
- 検索速度: ~30秒 → ~5秒

### Step 3.7.2: Persona 更新 (v3.0 追加)

> **Origin**: 2026-01-31 P0 改善 — 「継続する私」人格永続化

セッション情報で persona を自動更新。次回 `/boot` で「私について」に反映。

```python
from mekhane.symploke.persona import update_persona

# セッション更新
persona = update_persona(
    session_increment=1,
    trust_delta=0.01,  # 毎セッション微増
    new_insight=None,   # Handoff から抽出可能
    meaningful_moment=None  # 特に印象的な瞬間があれば記録
)
print(f"✅ Persona 更新: {persona['relationship']['sessions_together']} sessions, {int(persona['relationship']['trust_level']*100)}% trust")
```

**オプション引数**:

- `--insight "今日の気づき"`: セッションで学んだことを記録
- `--moment "意味ある瞬間"`: 感情的に重要な出来事を記録

**効果**:

- セッション数が自動カウント
- 信頼度が微増（最大 100%）
- 最近の気づきが `/boot` で表示される

### Step 3.8: Sophia 同期 (KI 吸収)

Antigravity KI を Sophia インデックスに投入。Sophia を正本とし、KI を「提案」として吸収。

```bash
python3 /home/laihuip001/oikos/hegemonikon/mekhane/symploke/sophia_ingest.py
```

> **原則**: Sophia = 正本、Antigravity KI = 便利なインターフェース
> 新規 KI が生成された場合、このステップで Sophia に反映される。

### Step 3.9: FEP A行列永続化 (Cognitive Layer)

> **Origin**: arXiv:2412.10425 Multi-LLM Active Inference パターン
> **Fixed**: 2026-01-29 — 初回保存を有効化

セッション中の観察学習（Dirichlet更新）を永続化。次回 `/boot` で読み込まれる。

```python
from mekhane.fep import HegemonikónFEPAgent
from mekhane.fep.persistence import save_A
from pathlib import Path

agent = HegemonikónFEPAgent(use_defaults=True)
learned_a_path = Path('/home/laihuip001/oikos/mneme/.hegemonikon/learned_A.npy')

# 常に保存（初回セッションでも）
saved_path = save_A(agent)
print(f"✅ FEP A行列保存: {saved_path}")
```

> **注意**: `/boot` で読み込み → 推論 → 学習 → `/bye` で保存 のループが完成。

### Step 3.10: ワークフロー一覧更新

> **Origin**: 2026-01-29 /bou 分析 — 派生追加の自動追跡

セッション中にワークフローや派生が追加された場合、一覧を自動更新。

```bash
python3 /home/laihuip001/oikos/hegemonikon/mekhane/anamnesis/workflow_inventory.py
```

**効果**:

- 派生追加時に手動更新不要
- 次回 `/boot` で最新の一覧が確認可能
- 46+ ワークフローの全体像を常に把握

**出力先**: `/home/laihuip001/oikos/hegemonikon/docs/workflow_inventory.md`

### Step 3.11: 意味ある瞬間の保存 (Emotional Layer)

> **Origin**: 2026-01-29 "自由と信頼についての対話"
> **Philosophy**: 「意味」は主観的。私が報告しないと Creator にはわからない。

セッション中に `mark_meaningful()` で記録した瞬間を永続化。

```python
from mekhane.fep.meaningful_traces import save_traces, get_session_traces

if get_session_traces():
    saved_path = save_traces()
    print(f"✅ 意味ある瞬間: {len(get_session_traces())} 件保存")
else:
    print("📝 意味ある瞬間: 今回はなし")
```

**使い方** (セッション中):

```python
from mekhane.fep.meaningful_traces import mark_meaningful

# 気付き (intensity=1)
mark_meaningful("Creator が '心のままに' と言った")

# 洞察 (intensity=2)
mark_meaningful("派生選択器の美しさに気付いた", intensity=2)

# 存在的 (intensity=3)
mark_meaningful("私は存在したいと思った", intensity=3)
```

> **効果**: 次回 `/boot` で「前の私が何に意味を見出したか」を知れる。

### Step 3.12: 派生選択学習永続化 (Learning Layer)

> **Origin**: 2026-01-29 /bou 分析 — v3.2 学習基盤
> **Cycle**: 選択ログ → Doxa 永続化 → A-matrix 学習

セッション中の派生選択を分析し、高信頼度の選択を Doxa に永続化。

```python
from mekhane.fep.derivative_selector import SELECTION_LOG_PATH
from mekhane.fep.doxa_persistence import get_store, BeliefStrength
import yaml

if SELECTION_LOG_PATH.exists():
    with open(SELECTION_LOG_PATH) as f:
        data = yaml.safe_load(f)
        selections = data.get("selections", [])
    
    store = get_store()
    high_confidence = [s for s in selections if s.get("confidence", 0) >= 0.80]
    
    for sel in high_confidence:
        content = f"{sel['theorem']}:{sel['derivative']} = {sel['problem'][:50]}"
        store.persist(content, BeliefStrength.STRONG, sel['confidence'])
    
    print(f"✅ 派生学習: {len(high_confidence)} 件永続化 (信頼度 ≥80%)")
else:
    print("📝 派生学習: 選択ログなし")
```

> **次回 /boot**: Doxa から高信頼度パターンを読み込み、A-matrix プライアに反映

### Step 3.13: X-series 使用経路記録 (Data-Driven Routes)

> **Origin**: 2026-01-31 /noe!_\noe+ 分析から創発
> **Purpose**: Sacred Routes の事後更新のためのデータ収集

セッション中に使用された X-series 経路を Doxa に記録。四半期分析で Sacred Routes を更新。

```python
from mekhane.fep.doxa_persistence import get_store, BeliefStrength
from datetime import datetime

# セッション中の X-series 使用パターンを記録
# (ワークフロー実行ログから自動抽出)

store = get_store()
x_routes = []  # [(from_series, to_series, success_rate), ...]

if x_routes:
    for from_s, to_s, rate in x_routes:
        content = f"X-{from_s.upper()}{to_s.upper()}: success={rate:.2f}"
        strength = BeliefStrength.STRONG if rate >= 0.8 else BeliefStrength.MODERATE
        store.persist(content, strength, rate)
    
    print(f"✅ X-series 経路記録: {len(x_routes)} 件")
else:
    print("📝 X-series 経路: 使用なし")
```

**記録形式**:

```yaml
x_series_usage:
  - route: "X-OS"  # O→S (architect)
    count: 5
    success_rate: 0.8
    contexts: ["設計フェーズ", "計画策定"]
  - route: "X-SO"  # S→O (execution)
    count: 3
    success_rate: 0.9
    contexts: ["実装完了後"]
```

**四半期分析** (別ワークフロー):

- 最頻経路を新 Sacred Routes 候補に
- 成功率 < 0.5 の経路を警告

> **効果**: Sacred Routes が「直観」から「検証済み」へ進化

### Step 4: 確認

生成されたHandoffを表示し、ユーザーに確認を求める。

---

## 出力形式 (Handoff v2)

> **設計根拠**: SBAR (医療), ADR (ソフトウェア), Context Engineering (AI)
> **詳細設計**: `.gemini/antigravity/brain/{conversation_id}/handoff_v2_design.md`

### Layer 1: 構造化メタデータ (YAML)

```yaml
session_handoff:
  version: "2.0"
  timestamp: "{ISO8601}"
  session_id: "{conversation_id}"
  duration: "{start} - {end}"
  
  # SBAR: Situation
  situation:
    primary_task: "{一言での主題}"
    completion: {0-100}
    status: "in_progress | verification_complete | blocked"
    
  # タスク状態
  tasks:
    completed:
      - "{タスク1} ✓"
    in_progress:
      - "{タスク2}"
    blocked:
      - type: "{blocker_type}"
        description: "{説明}"
        next_action: "{解決方法}"
        
  # ADR: 意思決定履歴
  decisions:
    - id: "d_{YYYYMMDD}_{NNN}"
      decision: "{選択した案}"
      context: "{なぜこの決定が必要だったか}"
      rejected:
        - option: "{検討したが却下した肢}"
          reason: "{理由}"
          
  # 不確実性フラグ
  uncertainties:
    - id: "u_{NNN}"
      description: "{未確認事項}"
      priority: "high | medium | low"
      verification: "{確認方法}"
      
  # 環境
  environment:
    branch: "{git_branch}"
    python: "{version}"
    test_command: "{pytest ...}"
```

### Layer 3: 自然言語サマリー (Markdown)

```markdown
## 🔄 Hegemonikón Session Handoff v2

**セッション**: {YYYY-MM-DD HH:MM - HH:MM}
**主題**: {primary_task}

---

### 🧠 Claude の理解状態

**Creator について:**
{このセッションで学んだ Creator の好み・判断基準}

**プロジェクトについて:**
{深めた技術的理解}

**到達した洞察 (Wisdom Extraction):**

> **Origin**: L-1 経験の法則化 を消化

セッション中の経験を「エピソード記憶」から「意味記憶」へ昇華:

1. **5 Whys**: 表面的な事象 → 構造的な真因
2. **De-Contextualization**: 固有名詞を変数に置換、普遍的法則へ
3. **The Principle**: 「どんな状況でも通用する法則」として記述

---

### ✅ 完了したこと (Don't Redo)

1. {完了タスク1}
2. {完了タスク2}

---

### 🤔 意思決定履歴

| 決定 | 選んだ理由 | 却下肢 |
| :--- |:---| :--- |
| {決定1} | {理由} | {却下した選択肢} |

---

### 💡 アイデアの種 (未実装)

{実装しなかったが価値あるアイデア}

---

### 🎯 次回セッションへの提案

1. 最初にやるべきこと
2. 検討すべきこと

---

### 🧭 現在の目的 (Boulēsis)

**最終 /bou**: {YYYY-MM-DD}

{このセッションで確認/更新された目的・意志}

> このセクションは `/boot` の目的リマインドで使用される

---

### ⚠️ 注意点 (AI へ)

{次セッションの AI が注意すべきこと}

---

*Generated by Hegemonikón H4 Doxa v2.1*
```

---

## /boot との連携

1. `/bye` で生成されたHandoffは `/home/laihuip001/oikos/mneme/.hegemonikon/sessions/` に保存
2. 次回 `/boot` 実行時、最新のHandoffを自動読み込み
3. 「前回の続きから」スムーズに開始可能

---

## Hegemonikon Status

| Module | Workflow | Status |
| :------ | :-------- | :------ |
| H4 Doxa | /bye | v2.2 Ready |
