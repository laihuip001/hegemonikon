# プロンプトエンジニアリング教養 Skill 実装計画

> **CCL**: `CLL/mek+`
> **定理**: S2 Mekhanē × A3 Gnōmē × A2 Krisis
> **目的**: プロンプトエンジニアリングの「教養」を教え、フィードバック機構を提供

---

## 1. 課題と目標

| 項目 | 内容 |
|:-----|:-----|
| **何を教えるか** | 言葉遣い・推奨フレーズ・指示の使い分け |
| **解説要件** | 意図差・出力変化・**作用機序** を含む |
| **例題** | 「教えて」vs「考えて」の違い |
| **フィードバック** | AIチャット履歴→改善提案・技法提案 |

---

## User Review Required

> [!IMPORTANT]
> **CLL/mek+ の解釈確認**: 今回の Skill は `/mek+` の派生 `adap`（既存を適応させる）として位置づけ、Hegemonikón 体系に馴染む「聖」な生成を行います。

---

## 2. Proposed Changes

### A. Skill 本体

#### [NEW] [SKILL.md](file:///home/makaron8426/oikos/.agent/skills/schema/s2-mekhane/prompt-literacy/SKILL.md)

プロンプトリテラシー教養 Skill:

```yaml
# Skill Frontmatter
id: "S2-PE"
name: "Prompt Literacy"
greek: "Πρoτρoπή"  # Prototropē = 最初の転換点
series: "Schema"
parent: "S2 Mekhanē"

description: >
  プロンプトエンジニアリングの教養を教え、
  過去チャット履歴から改善提案・技法提案を提供する。

triggers:
  - "プロンプトの教養"
  - "言い回し"
  - "教えて vs 考えて"
  - "履歴分析"
  - "表現改善"

derivatives: [didact, feed, mech]
```

**3派生モード**:

| 派生 | 役割 | トリガー |
|:-----|:-----|:---------|
| **didact** | 教授モード — 概念・技法の解説 | 「〜の違いを教えて」 |
| **feed** | フィードバックモード — 履歴解析 | 「履歴を分析して」 |
| **mech** | 作用機序モード — メカニズム解説 | 「なぜそうなる？」 |

---

### B. コンテンツ構造

#### [NEW] [instruction_taxonomy.md](file:///home/makaron8426/oikos/.agent/skills/schema/s2-mekhane/prompt-literacy/references/instruction_taxonomy.md)

指示語の分類学:

```markdown
# 指示語タクソノミー（作用機序付き）

## 1. 認知モード指定語

### 1.1 「教えて」系 (Tell)
- **意図**: 既知情報の提示を要求
- **作用機序**: LLM を「知識検索モード」に設定
- **出力傾向**: 既存知識の再構成、引用的
- **適用**: 事実確認、定義要求

### 1.2 「考えて」系 (Think)
- **意図**: 推論・分析プロセスの実行を要求
- **作用機序**: LLM を「推論モード」に設定
- **出力傾向**: ステップバイステップの論証、新しい結論の導出
- **適用**: 問題解決、設計、分析

### 1.3 「作って/生成して」系 (Create)
- **意図**: 新規コンテンツの創出を要求
- **作用機序**: LLM を「生成モード」に設定
- **出力傾向**: 創造的、構成的
- **適用**: コード生成、文章作成

---

## 2. 「教えて」vs「考えて」詳細解説

| 観点 | 「〜を教えて」 | 「〜を考えて」 |
|:-----|:-------------|:--------------|
| **意図差** | 知識の提示を求める | 思考プロセスの実行を求める |
| **LLMの内部状態** | 検索・要約モード | 推論・演繹モード |
| **出力形式** | 「〜とは〜である」 | 「まず〜次に〜したがって」 |
| **作用機序** | 訓練データからのパターンマッチ最重視 | 論理的連鎖の生成を最重視 |

### 作用機序の詳細

```

「教えて」:
  入力 → [知識ベース参照] → [整理・要約] → 出力
  
「考えて」:
  入力 → [問題分解] → [仮説生成] → [論証] → 出力

```

**例**:
- 「ソートアルゴリズムを教えて」 → アルゴリズム一覧と定義
- 「このデータをソートする方法を考えて」 → 分析→選択→理由の論証
```

---

### C. フィードバック機構

#### [NEW] [feedback_analyzer.py](file:///home/makaron8426/oikos/hegemonikon/mekhane/ergasterion/prompt_literacy/feedback_analyzer.py)

```python
"""
プロンプトリテラシー・フィードバック分析器

入力: AIチャット履歴（ユーザー発話部分）
出力: 改善提案 + 技法提案
"""

# 分析パターン
IMPROVEMENT_PATTERNS = [
    {
        "pattern": r"(教えて|説明して)",
        "context_check": "推論が必要な文脈",
        "suggestion": "「考えて」に変更を検討",
        "mechanism": "推論モードを明示的に発動させる"
    },
    {
        "pattern": r"(?<!ステップ)(?<!段階).*してください$",
        "context_check": "複雑なタスク",
        "suggestion": "「ステップバイステップで」を追加",
        "mechanism": "Chain-of-Thought を誘発"
    },
    # ... 追加パターン
]

TECHNIQUE_RECOMMENDATIONS = {
    "目標不明確": {
        "technique": "Goal-First Declaration",
        "example": "目標: 〜。そのために〜",
        "mechanism": "LLMの注意を目標に固定"
    },
    "曖昧な条件": {
        "technique": "Constraint Enumeration",
        "example": "【条件】1. ... 2. ... 3. ...",
        "mechanism": "制約を明示的にチェックリスト化"
    }
}
```

---

### D. ワークフロー連携

#### [MODIFY] [mek.md](file:///home/makaron8426/oikos/.agent/workflows/mek.md)

`/mek` に派生を追加:

```yaml
# 追加項目
derivatives: [comp, inve, adap, lit]  # lit = literacy

# lit 派生の定義
lit:
  purpose: "プロンプトリテラシー教育・フィードバック"
  modes: [didact, feed, mech]
  skill_ref: "schema/s2-mekhane/prompt-literacy/SKILL.md"
```

**発動方法**:

```ccl
/mek lit          # didact: 概念・技法解説
/mek lit:feed     # feed: 履歴分析・改善提案
/mek lit:mech     # mech: 作用機序解説
```

---

## 3. 出力要件への回答

### 3.1 Skill 仕様

| 項目 | 内容 |
|:-----|:-----|
| **何を教えるか** | 言葉遣い・推奨フレーズ・指示の使い分け |
| **どう解説するか** | 意図差・出力変化・作用機序の3層構造 |
| **入力** | 質問 or チャット履歴 |
| **出力** | 解説 or 改善提案リスト + 技法提案 |

### 3.2 「教えて」vs「考えて」解説フォーマット

```markdown
## 「〇〇を教えて」vs「〇〇を考えて」

### 1. 意図の差
- **教えて**: 知識の提示を求める → 「正解を出して」
- **考えて**: プロセスの実行を求める → 「導き出して」

### 2. 出力の変化
| 入力 | 出力傾向 |
|:-----|:---------|
| 「機械学習を教えて」 | 定義・種類・特徴の列挙 |
| 「このデータで機械学習を適用する方法を考えて」 | 分析→手法選択→理由の論証 |

### 3. 作用機序
LLM は入力の動詞から「認知モード」を推定する:
- **Tell 系**: 知識ベース→要約→出力（検索優勢）
- **Think 系**: 分解→推論→統合→出力（計算優勢）

### 4. 使い分けガイド
[判定フロー図]
```

### 3.3 フィードバック出力形式

```markdown
# 📊 プロンプト改善レポート

## 分析対象
- セッション: {ID}
- 発話数: {N}
- 分析日: {date}

## 🔴 改善すべき表現

| # | 元の表現 | 改善案 | 理由 (作用機序) |
|:--|:---------|:-------|:----------------|
| 1 | 「〜を教えて」 | 「〜を考えて」 | 推論が必要な文脈。検索モードより推論モードが適切 |
| 2 | 「してください」 | 「ステップバイステップで」 | CoT誘発で精度向上 |

## 🟢 取り入れるべき技法

| 技法 | 適用場面 | 効果 (作用機序) |
|:-----|:---------|:----------------|
| Goal-First Declaration | 目標が後出しの発話 | 注意を目標に固定 |
| Constraint Enumeration | 条件が散在する発話 | 制約のチェックリスト化 |

## 📈 推奨アクション
1. {具体的アクション1}
2. {具体的アクション2}
```

---

## 4. Verification Plan

### 4.1 Automated Tests

現時点で `/mek` ワークフローにユニットテストはありません。以下を手動で実行:

```bash
# Skill.md 構文チェック（存在確認）
ls -la /home/makaron8426/oikos/.agent/skills/schema/s2-mekhane/prompt-literacy/SKILL.md

# Python モジュール構文チェック
python -m py_compile /home/makaron8426/oikos/hegemonikon/mekhane/ergasterion/prompt_literacy/feedback_analyzer.py
```

### 4.2 Manual Verification

1. **Skill 発動テスト**:

   ```text
   入力: /mek lit 「教えて」と「考えて」の違いを教えて
   期待: instruction_taxonomy.md の内容に基づく解説
   ```

2. **フィードバック機構テスト**:

   ```text
   入力: /mek lit:feed [チャット履歴ファイル]
   期待: 改善提案表 + 技法提案表
   ```

3. **作用機序解説テスト**:

   ```text
   入力: /mek lit:mech なぜ「考えて」で推論が誘発されるのか
   期待: 認知モード切替のメカニズム解説
   ```

---

## 5. ファイル構成まとめ

```
.agent/skills/schema/s2-mekhane/prompt-literacy/
├── SKILL.md                          # [NEW] Skill本体
└── references/
    └── instruction_taxonomy.md       # [NEW] 指示語分類学

hegemonikon/mekhane/ergasterion/prompt_literacy/
├── __init__.py                       # [NEW]
├── feedback_analyzer.py              # [NEW] フィードバック分析器
└── pattern_db.py                     # [NEW] パターンDB

.agent/workflows/
└── mek.md                            # [MODIFY] lit派生追加
```

---

## 6. リスクと代替案

| リスク | 対策 |
|:-------|:-----|
| パターンDB が不十分 | 初期は基本パターンのみ。運用で拡充 |
| 履歴フォーマット不統一 | 複数フォーマット対応 or 正規化層追加 |
| 作用機序の精度 | 確信度マーカー（HIGH/MEDIUM/LOW）を付与（A2 Krisis 連携） |

---

*Generated by `/mek+ lit:plan` | S2 Mekhanē × A3 Gnōmē*
