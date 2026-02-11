#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/symploke/
# PURPOSE: Value Pitch の Benefit Angle 自動提案 + 骨格ドラフト生成
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

A0 → /bye の Value Pitch は成果の意義を語る (Step 3.6π)
   → 成果ごとに最適な Benefit Angle を選ぶ必要がある
   → value_pitch_proposer.py が自動提案する:
     1. 完了タスクを受け取る
     2. Benefit Angle を keyword 分類で推定
     3. 骨格ドラフト (タイトル + Before→After) を生成

Q.E.D.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


# =============================================================================
# Benefit Angle Definition
# =============================================================================

# 7公理 + X-series = 8次元
BENEFIT_ANGLES = {
    "wakaru": {
        "label": "わかる",
        "axiom": "FEP",
        "question": "なぜ因果が見えるようになったか",
        "sensation": "霧が晴れた",
        "keywords": [
            "可視化", "明確", "説明", "透明", "理解", "構造化",
            "因果", "分析", "diagnosis", "debug", "trace",
            "dashboard", "表示", "見える", "分解", "把握",
        ],
    },
    "dekiru": {
        "label": "できる",
        "axiom": "Flow",
        "question": "なぜ不可能が可能になったか",
        "sensation": "壁を越えた",
        "keywords": [
            "新規", "実装", "追加", "新しい", "機能", "create",
            "implement", "enable", "unlock", "初めて", "導入",
            "パイプライン", "接続", "統合", "bridge", "connect",
        ],
    },
    "fukai": {
        "label": "深い",
        "axiom": "Value",
        "question": "なぜ構造を貫く原理か",
        "sensation": "骨まで見えた",
        "keywords": [
            "原理", "本質", "根本", "公理", "定理", "演繹",
            "FEP", "哲学", "圏論", "随伴", "射", "関手",
            "同型", "構造", "体系", "理論", "洞察",
        ],
    },
    "karui": {
        "label": "軽い",
        "axiom": "Scale",
        "question": "なぜ貴方の負担を減らすか",
        "sensation": "重荷が下りた",
        "keywords": [
            "削減", "圧縮", "簡素", "統合", "整理", "remove",
            "clean", "refactor", "減らす", "省略", "自動",
            "効率", "短縮", "不要", "廃止", "deprecated",
        ],
    },
    "sodatsu": {
        "label": "育つ",
        "axiom": "Function",
        "question": "なぜ未来の貴方を助け続けるか",
        "sensation": "種を蒔いた",
        "keywords": [
            "テスト", "検証", "CI", "自動化", "永続", "学習",
            "蓄積", "成長", "改善", "進化", "calibration",
            "persist", "save", "load", "future", "次回",
        ],
    },
    "mamoru": {
        "label": "守る",
        "axiom": "Valence",
        "question": "なぜ貴方を○○から守るか",
        "sensation": "盾ができた",
        "keywords": [
            "防止", "防御", "安全", "制約", "制限", "guard",
            "validate", "check", "error", "fix", "修正",
            "バグ", "脆弱", "リスク", "二重", "重複",
        ],
    },
    "tashika": {
        "label": "確か",
        "axiom": "Precision",
        "question": "なぜ根拠を持って語れるか",
        "sensation": "地に足がつく",
        "keywords": [
            "根拠", "証拠", "測定", "数値", "定量", "精度",
            "閾値", "パラメータ", "calibrate", "benchmark",
            "PROVISIONAL", "演繹", "証明", "接地", "根拠",
        ],
    },
    "hibiku": {
        "label": "響く",
        "axiom": "X-series",
        "question": "なぜ掛け合わさって効くか",
        "sensation": "偶然じゃない",
        "keywords": [
            "相乗", "連携", "組み合わせ", "統合", "掛け算",
            "synergy", "compose", "pipeline", "chain", "依存",
            "全体", "end-to-end", "e2e", "一貫", "一気通貫",
        ],
    },
}


# =============================================================================
# Data Classes
# =============================================================================


# PURPOSE: CompletedTask の機能を提供する
@dataclass
class CompletedTask:
    """完了タスク。/bye 時に収集される。"""

    title: str
    description: str = ""
    files_changed: List[str] = field(default_factory=list)
    tests_added: int = 0
    tests_passed: int = 0


# PURPOSE: AngleScore の機能を提供する
@dataclass
class AngleScore:
    """特定の角度に対するスコア。"""

    angle_key: str
    label: str
    axiom: str
    score: float
    matched_keywords: List[str] = field(default_factory=list)


# PURPOSE: PitchProposal の機能を提供する
@dataclass
class PitchProposal:
    """Value Pitch 提案。"""

    task: CompletedTask
    primary_angle: AngleScore
    secondary_angles: List[AngleScore] = field(default_factory=list)
    suggested_title: str = ""
    skeleton: str = ""


# =============================================================================
# Core Functions
# =============================================================================


def _classify_angle(task: CompletedTask) -> List[AngleScore]:
    """タスクを Benefit Angles にスコアリング。

    keyword マッチでスコアリング。title + description + files_changed を走査。
    """
    text = f"{task.title} {task.description} {' '.join(task.files_changed)}".lower()

    scores = []
    for key, angle in BENEFIT_ANGLES.items():
        matched = []
        for kw in angle["keywords"]:
            if kw.lower() in text:
                matched.append(kw)

        if matched:
            # スコア = マッチしたキーワード数 (重複除去) / 全キーワード数
            unique_matches = list(set(matched))
            score = len(unique_matches) / len(angle["keywords"])

            # テスト追加は「育つ」を強化
            if key == "sodatsu" and task.tests_added > 0:
                score += 0.2

            scores.append(
                AngleScore(
                    angle_key=key,
                    label=angle["label"],
                    axiom=angle["axiom"],
                    score=min(1.0, score),
                    matched_keywords=unique_matches,
                )
            )

    # スコア降順
    scores.sort(key=lambda s: s.score, reverse=True)
    return scores


def _generate_title(task: CompletedTask, angle: AngleScore) -> str:
    """Benefit Angle タイトルを生成。

    「なぜ {X} が {angle} か」形式。
    """
    # タスク名から主語を抽出 (最初の名詞相当)
    subject = task.title
    if len(subject) > 30:
        subject = subject[:30] + "…"

    return f"なぜ {subject} が **{angle.label}** か"


def _generate_skeleton(task: CompletedTask, angle: AngleScore) -> str:
    """骨格ドラフトを生成。

    書き方原則に沿った構造だが、中身は AI が埋める。
    """
    angle_def = BENEFIT_ANGLES[angle.angle_key]

    test_line = ""
    if task.tests_added > 0:
        test_line = f"\n| テスト | 0 | {task.tests_added} 追加 ({task.tests_passed} passed) |"

    files_line = ""
    if task.files_changed:
        changed = ", ".join(f"`{f}`" for f in task.files_changed[:3])
        if len(task.files_changed) > 3:
            changed += f" + {len(task.files_changed) - 3} more"
        files_line = f"\n変更ファイル: {changed}"

    return f"""### ❶ {_generate_title(task, angle)}

**Angle**: {angle.label} ({angle.axiom})
**問い**: {angle_def["question"]}
**感覚**: {angle_def["sensation"]}

**Before → After**:

| Before | After |
|:-------|:------|
| {{Before の痛みを具体的に}} | {{After の解放を具体的に}} |

**ここで語ること**:
- Before の苦しみ: {{何がどう辛かったか}}
- 変えた理由: {{前は○○だったから、×のために▲にした}}
- After の解放: {{誰が、いつから、何ができるようになったか}}
- 放置リスク: {{もしやらなかったら…}}
{files_line}

**数字**:

| 指標 | Before | After |
|:-----|:-------|:------|
| ... | ... | ... |{test_line}

---
"""


# PURPOSE: タスク一覧から Value Pitch 提案を生成
def propose_pitches(tasks: List[CompletedTask]) -> List[PitchProposal]:
    """完了タスクから Value Pitch 提案を生成する。

    Args:
        tasks: 完了タスクのリスト

    Returns:
        PitchProposal のリスト (primary_angle スコア降順)
    """
    proposals = []
    for task in tasks:
        scores = _classify_angle(task)
        if not scores:
            # どの角度にもマッチしない → wakaru (FEP) をデフォルト
            scores = [
                AngleScore(
                    angle_key="wakaru",
                    label="わかる",
                    axiom="FEP",
                    score=0.1,
                    matched_keywords=[],
                )
            ]

        primary = scores[0]
        secondary = scores[1:3]  # 上位2つまで

        proposal = PitchProposal(
            task=task,
            primary_angle=primary,
            secondary_angles=secondary,
            suggested_title=_generate_title(task, primary),
            skeleton=_generate_skeleton(task, primary),
        )
        proposals.append(proposal)

    # primary スコア降順
    proposals.sort(key=lambda p: p.primary_angle.score, reverse=True)
    return proposals


# PURPOSE: 提案をフォーマットして表示テキストを生成
def format_proposals(proposals: List[PitchProposal]) -> str:
    """Value Pitch 提案を /bye で表示するフォーマット。"""
    if not proposals:
        return "> Value Pitch: 完了タスクがありません。\n"

    lines = [
        "## 📊 Value Pitch 自動提案",
        "",
        "> 以下は keyword 分類による骨格提案です。",
        "> タイトルと Before→After を肉付けしてください。",
        "",
    ]

    for i, p in enumerate(proposals, 1):
        lines.append(f"### 提案 {i}: {p.suggested_title}")
        lines.append(f"")
        lines.append(
            f"| 角度 | スコア | マッチ |"
        )
        lines.append(f"|:-----|:-------|:-------|")
        lines.append(
            f"| **{p.primary_angle.label}** ({p.primary_angle.axiom}) "
            f"| {p.primary_angle.score:.0%} "
            f"| {', '.join(p.primary_angle.matched_keywords[:5])} |"
        )
        for s in p.secondary_angles:
            lines.append(
                f"| {s.label} ({s.axiom}) "
                f"| {s.score:.0%} "
                f"| {', '.join(s.matched_keywords[:5])} |"
            )

        lines.append("")
        lines.append(p.skeleton)
        lines.append("")

    return "\n".join(lines)


# PURPOSE: Dispatch Log エントリからタスクリストを生成
def tasks_from_dispatch_log(log_data: dict) -> List[CompletedTask]:
    """Dispatch Log YAML をパースして CompletedTask リストに変換。

    Args:
        log_data: dispatch_log YAML の dict

    Returns:
        CompletedTask のリスト (success のもののみ)
    """
    tasks = []

    # workflow_executions
    for entry in log_data.get("workflow_executions", []):
        if entry.get("outcome") == "success":
            tasks.append(
                CompletedTask(
                    title=f"{entry.get('workflow', '')} {entry.get('notes', '')}",
                    description=entry.get("notes", ""),
                )
            )

    # skill_activations
    for entry in log_data.get("skill_activations", []):
        if entry.get("outcome") == "success":
            tasks.append(
                CompletedTask(
                    title=f"{entry.get('skill', '')} {entry.get('notes', '')}",
                    description=entry.get("notes", ""),
                )
            )

    # exception_patterns (学びとして)
    for entry in log_data.get("exception_patterns", []):
        if entry.get("learned"):
            tasks.append(
                CompletedTask(
                    title=f"学び: {entry.get('learned', '')}",
                    description=entry.get("action_taken", ""),
                )
            )

    return tasks


# PURPOSE: Git diff stat からタスクリストを生成
def tasks_from_git_stat(
    commit_messages: List[str],
    files_changed: Optional[List[str]] = None,
    tests_added: int = 0,
    tests_passed: int = 0,
) -> List[CompletedTask]:
    """Git commit メッセージからタスクリストを生成。

    Args:
        commit_messages: commit メッセージのリスト
        files_changed: 変更ファイルリスト
        tests_added: 追加テスト数
        tests_passed: 通過テスト数

    Returns:
        CompletedTask のリスト
    """
    tasks = []
    for msg in commit_messages:
        tasks.append(
            CompletedTask(
                title=msg,
                files_changed=files_changed or [],
                tests_added=tests_added,
                tests_passed=tests_passed,
            )
        )
    return tasks
