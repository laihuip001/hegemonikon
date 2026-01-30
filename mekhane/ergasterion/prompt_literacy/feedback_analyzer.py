"""
Prompt Literacy — Feedback Analyzer

プロンプトリテラシー・フィードバック分析器
AIチャット履歴を解析し、改善提案と技法提案を生成する。

Usage:
    from mekhane.ergasterion.prompt_literacy.feedback_analyzer import analyze_history
    
    result = analyze_history(chat_text)
    print(result.to_markdown())
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

from .pattern_db import (
    IMPROVEMENT_PATTERNS,
    TECHNIQUE_RECOMMENDATIONS,
    Pattern,
    Technique,
)


@dataclass
class Improvement:
    """改善提案"""
    original: str
    suggestion: str
    reason: str
    mechanism: str
    line_number: Optional[int] = None


@dataclass
class TechniqueRecommendation:
    """技法提案"""
    name: str
    situation: str
    example: str
    mechanism: str


@dataclass
class FeedbackReport:
    """フィードバックレポート"""
    session_id: str
    utterance_count: int
    analysis_date: str
    improvements: List[Improvement] = field(default_factory=list)
    techniques: List[TechniqueRecommendation] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    
    def to_markdown(self) -> str:
        """Markdown形式でレポートを生成"""
        lines = [
            "# 📊 プロンプト改善レポート",
            "",
            "## 分析対象",
            f"- セッション: {self.session_id}",
            f"- 発話数: {self.utterance_count}",
            f"- 分析日: {self.analysis_date}",
            "",
        ]
        
        # 改善すべき表現
        if self.improvements:
            lines.append("## 🔴 改善すべき表現")
            lines.append("")
            lines.append("| # | 元の表現 | 改善案 | 理由 (作用機序) |")
            lines.append("|:--|:---------|:-------|:----------------|")
            for i, imp in enumerate(self.improvements, 1):
                lines.append(
                    f"| {i} | {imp.original[:30]}... | {imp.suggestion} | {imp.reason} |"
                )
            lines.append("")
        else:
            lines.append("## ✅ 改善すべき表現: なし")
            lines.append("")
        
        # 取り入れるべき技法
        if self.techniques:
            lines.append("## 🟢 取り入れるべき技法")
            lines.append("")
            lines.append("| 技法 | 適用場面 | 効果 |")
            lines.append("|:-----|:---------|:-----|")
            for tech in self.techniques:
                lines.append(f"| {tech.name} | {tech.situation} | {tech.mechanism} |")
            lines.append("")
        
        # 推奨アクション
        if self.actions:
            lines.append("## 📈 推奨アクション")
            for i, action in enumerate(self.actions, 1):
                lines.append(f"{i}. {action}")
            lines.append("")
        
        return "\n".join(lines)


def extract_user_utterances(text: str) -> List[str]:
    """
    チャット履歴からユーザー発話を抽出
    
    対応フォーマット:
    - "User: ..." / "USER: ..."
    - "<USER_REQUEST>...</USER_REQUEST>"
    - ">>>" prefix
    """
    utterances = []
    
    # パターン1: User: プレフィックス
    pattern1 = re.findall(r'(?:User|USER):\s*(.+?)(?:\n|$)', text, re.MULTILINE)
    utterances.extend(pattern1)
    
    # パターン2: XML形式
    pattern2 = re.findall(r'<USER_REQUEST>(.*?)</USER_REQUEST>', text, re.DOTALL)
    utterances.extend(pattern2)
    
    # パターン3: >>> プレフィックス
    pattern3 = re.findall(r'>>>\s*(.+?)(?:\n|$)', text, re.MULTILINE)
    utterances.extend(pattern3)
    
    return [u.strip() for u in utterances if u.strip()]


def analyze_utterance(utterance: str, patterns: List[Pattern]) -> List[Improvement]:
    """単一発話を分析し、改善提案を生成"""
    improvements = []
    
    for pattern in patterns:
        if re.search(pattern.regex, utterance, re.IGNORECASE):
            # 追加の文脈チェック（オプション）
            if pattern.context_check:
                # 将来: より高度な文脈判定を実装
                pass
            
            improvements.append(Improvement(
                original=utterance,
                suggestion=pattern.suggestion,
                reason=pattern.reason,
                mechanism=pattern.mechanism,
            ))
    
    return improvements


def detect_missing_techniques(utterances: List[str]) -> List[TechniqueRecommendation]:
    """使用されていない技法を検出し、推奨"""
    recommendations = []
    combined = " ".join(utterances)
    
    for key, tech in TECHNIQUE_RECOMMENDATIONS.items():
        # 技法が使用されているかチェック
        if not re.search(tech.detection_pattern, combined, re.IGNORECASE):
            recommendations.append(TechniqueRecommendation(
                name=tech.name,
                situation=tech.situation,
                example=tech.example,
                mechanism=tech.mechanism,
            ))
    
    return recommendations


def generate_actions(
    improvements: List[Improvement],
    techniques: List[TechniqueRecommendation],
) -> List[str]:
    """改善提案と技法提案から具体的なアクションを生成"""
    actions = []
    
    # 最も頻出する問題パターンからアクションを生成
    if improvements:
        # 問題パターンをカウント
        pattern_counts: Dict[str, int] = {}
        for imp in improvements:
            key = imp.suggestion
            pattern_counts[key] = pattern_counts.get(key, 0) + 1
        
        # 上位2つをアクション化
        sorted_patterns = sorted(pattern_counts.items(), key=lambda x: -x[1])
        for pattern, count in sorted_patterns[:2]:
            actions.append(f"「{pattern}」の使用を意識する ({count}件検出)")
    
    # 技法推奨からアクションを生成
    if techniques:
        for tech in techniques[:2]:
            actions.append(f"{tech.name} を試す（例: {tech.example}）")
    
    return actions


def analyze_history(
    text: str,
    session_id: str = "unknown",
) -> FeedbackReport:
    """
    チャット履歴を分析し、フィードバックレポートを生成
    
    Args:
        text: チャット履歴テキスト
        session_id: セッション識別子
    
    Returns:
        FeedbackReport: 分析結果
    """
    # 1. ユーザー発話を抽出
    utterances = extract_user_utterances(text)
    
    # 2. 各発話を分析
    all_improvements: List[Improvement] = []
    for utterance in utterances:
        improvements = analyze_utterance(utterance, IMPROVEMENT_PATTERNS)
        all_improvements.extend(improvements)
    
    # 3. 不足技法を検出
    techniques = detect_missing_techniques(utterances)
    
    # 4. アクションを生成
    actions = generate_actions(all_improvements, techniques)
    
    # 5. レポート生成
    return FeedbackReport(
        session_id=session_id,
        utterance_count=len(utterances),
        analysis_date=datetime.now().strftime("%Y-%m-%d"),
        improvements=all_improvements,
        techniques=techniques,
        actions=actions,
    )


# --- CLI Interface ---

def main():
    """コマンドラインインターフェース"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m mekhane.ergasterion.prompt_literacy.feedback_analyzer <file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    
    report = analyze_history(text, session_id=filepath)
    print(report.to_markdown())


if __name__ == "__main__":
    main()
