"""
/tak - Task Orchestration Module
PHASE 1: INTAKE - 入力解析

雑多な入力をパースし、個別タスクに分離する
"""
import re
from datetime import datetime
from typing import Optional
from .models import RawTaskItem, ParsedTask, DeadlineBucket


# 箇条書きパターン
BULLET_PATTERNS = [
    r'^[-*•・□◻︎◯○●]\s*',  # - * • ・ □ など
    r'^\d+[.)]\s*',          # 1. 1) など
    r'^[a-zA-Z][.)]\s*',     # a. a) など
    r'^【.*?】\s*',          # 【項目】
]

# 緊急度キーワード
URGENCY_KEYWORDS = {
    "高": ["急ぎ", "緊急", "ASAP", "今すぐ", "至急", "ブロッカー", "blocker", "urgent"],
    "中": ["今週", "今日", "明日", "早めに"],
    "低": ["いつか", "余裕があれば", "できれば", "将来"],
}

# 期限推定パターン
DEADLINE_PATTERNS = {
    DeadlineBucket.TODAY: [r"今日", r"本日", r"today"],
    DeadlineBucket.THREE_DAYS: [r"明日", r"明後日", r"3日", r"三日"],
    DeadlineBucket.WEEK: [r"今週", r"週末まで", r"金曜", r"this week"],
    DeadlineBucket.THREE_WEEKS: [r"今月", r"月末", r"3週間", r"三週間"],
    DeadlineBucket.TWO_MONTHS: [r"来月", r"2ヶ月", r"二ヶ月"],
}

# 意図抽出パターン
INTENT_PATTERNS = [
    r"(.+?)したい",
    r"(.+?)する",
    r"(.+?)必要",
    r"(.+?)やる",
    r"(.+?)作る",
    r"(.+?)直す",
    r"(.+?)修正",
]


class TaskIntakeParser:
    """
    PHASE 1: INTAKE - 入力解析器
    
    雑多なテキストをパースして個別タスクに分離
    """
    
    def parse(self, raw_input: str, source: str = "chat") -> list[ParsedTask]:
        """
        生の入力テキストをパースしてタスクリストに変換
        
        Args:
            raw_input: 雑多な入力テキスト
            source: 入力元 (chat, file, api)
            
        Returns:
            パース済みタスクのリスト
        """
        # Step 1: 行分割
        lines = self._split_into_lines(raw_input)
        
        # Step 2: 箇条書き検出と分離
        items = self._extract_items(lines)
        
        # Step 3: 各アイテムをパース
        tasks = []
        for item in items:
            if not item.strip():
                continue
            task = self._parse_single_item(item, source)
            if task.title:  # 空でないタスクのみ追加
                tasks.append(task)
        
        return tasks
    
    def _split_into_lines(self, text: str) -> list[str]:
        """テキストを行分割"""
        # 改行で分割
        lines = text.split('\n')
        # 空行を除去しつつ、連続する行をマージ
        result = []
        for line in lines:
            stripped = line.strip()
            if stripped:
                result.append(stripped)
        return result
    
    def _extract_items(self, lines: list[str]) -> list[str]:
        """箇条書きアイテムを抽出"""
        items = []
        current_item = []
        
        for line in lines:
            is_new_item = any(re.match(p, line) for p in BULLET_PATTERNS)
            
            if is_new_item:
                # 前のアイテムを保存
                if current_item:
                    items.append(' '.join(current_item))
                # 箇条書き記号を除去して新規開始
                cleaned = line
                for pattern in BULLET_PATTERNS:
                    cleaned = re.sub(pattern, '', cleaned)
                current_item = [cleaned.strip()]
            else:
                # 継続行として追加
                if current_item:
                    current_item.append(line)
                else:
                    # 箇条書きなしで始まる場合
                    current_item = [line]
        
        # 最後のアイテム
        if current_item:
            items.append(' '.join(current_item))
        
        # 箇条書きがなかった場合、句点で分割
        if len(items) == 1 and '。' in items[0]:
            items = [s.strip() for s in items[0].split('。') if s.strip()]
        
        return items
    
    def _parse_single_item(self, text: str, source: str) -> ParsedTask:
        """単一アイテムをパース"""
        task = ParsedTask(
            raw_text=text,
            title=self._extract_title(text),
            description=text,
            keywords=self._extract_keywords(text),
            implicit_deadline=self._detect_deadline(text),
        )
        
        # 緊急度を初期推定
        task.urgency = self._estimate_urgency(text)
        
        return task
    
    def _extract_title(self, text: str) -> str:
        """タイトルを抽出（最初の意味あるフレーズ）"""
        # 括弧内のコメントを除去
        cleaned = re.sub(r'[（(].+?[）)]', '', text)
        
        # 意図パターンでマッチ
        for pattern in INTENT_PATTERNS:
            match = re.search(pattern, cleaned)
            if match:
                return match.group(0).strip()
        
        # マッチしなければ最初の20文字
        return cleaned[:40].strip() if len(cleaned) > 40 else cleaned.strip()
    
    def _extract_keywords(self, text: str) -> list[str]:
        """キーワード抽出"""
        keywords = []
        
        # 技術用語
        tech_patterns = [
            r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b',  # CamelCase
            r'\b[A-Z]{2,}\b',                      # ACRONYMS
            r'\b[a-z]+_[a-z]+\b',                  # snake_case
        ]
        for pattern in tech_patterns:
            keywords.extend(re.findall(pattern, text))
        
        # 日本語の重要語（カタカナ）
        katakana = re.findall(r'[ァ-ヶー]+', text)
        keywords.extend([k for k in katakana if len(k) >= 2])
        
        return list(set(keywords))[:10]  # 最大10個
    
    def _detect_deadline(self, text: str) -> Optional[str]:
        """期限を検出"""
        for bucket, patterns in DEADLINE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return bucket.value
        return None
    
    def _estimate_urgency(self, text: str) -> int:
        """緊急度を推定 (0-100)"""
        text_lower = text.lower()
        
        # 高緊急
        for keyword in URGENCY_KEYWORDS["高"]:
            if keyword in text_lower or keyword in text:
                return 90
        
        # 中緊急
        for keyword in URGENCY_KEYWORDS["中"]:
            if keyword in text_lower or keyword in text:
                return 60
        
        # 低緊急
        for keyword in URGENCY_KEYWORDS["低"]:
            if keyword in text_lower or keyword in text:
                return 20
        
        # デフォルト
        return 50


def parse_tasks(raw_input: str, source: str = "chat") -> list[ParsedTask]:
    """便利関数: テキストからタスクをパース"""
    parser = TaskIntakeParser()
    return parser.parse(raw_input, source)
