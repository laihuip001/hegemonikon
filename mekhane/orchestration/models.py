"""
/tak - Task Orchestration Module
Data Models

Hegemonikón: K2 Chronos × O2 Boulēsis × S3 Stathmos
"""
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Optional
from uuid import uuid4


class DeadlineBucket(Enum):
    """期限区分"""
    TODAY = "today"          # 🔴 今日中
    THREE_DAYS = "3days"     # 🟠 三日以内  
    WEEK = "week"            # 🟡 今週中
    THREE_WEEKS = "3weeks"   # 🟢 3週間以内
    TWO_MONTHS = "2months"   # 🔵 2ヶ月以内
    BACKLOG = "backlog"      # ⚫ 未定


class Classification(Enum):
    """Eisenhower Matrix Classification"""
    MUST = "must"        # 緊急 × 重要
    SHOULD = "should"    # 重要
    DELEGATE = "delegate"  # 緊急
    DEFER = "defer"      # それ以外


class TaskLevel(Enum):
    """階層レベル"""
    PROJECT = "project"
    EPIC = "epic"
    STORY = "story"
    TASK = "task"
    SUBTASK = "subtask"


class DependencyType(Enum):
    """依存タイプ"""
    FS = "finish-to-start"  # A終了後にB開始
    SS = "start-to-start"   # A開始後にB開始可
    FF = "finish-to-finish" # A終了後にB終了
    BLOCKER = "blocker"     # A完了までB着手不可


class GapType(Enum):
    """不足情報カテゴリ"""
    SCOPE = "scope"         # ゴールが曖昧
    TECHNICAL = "technical" # 技術選定未定
    RESOURCE = "resource"   # 担当者未定
    DEADLINE = "deadline"   # 期限未設定
    DEPENDENCY = "dependency"  # 前提条件不明


@dataclass
class RawTaskItem:
    """生の入力アイテム"""
    text: str
    source: str = "chat"
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ParsedTask:
    """パース済みタスク"""
    id: str = field(default_factory=lambda: str(uuid4())[:8])
    title: str = ""
    description: str = ""
    raw_text: str = ""
    keywords: list[str] = field(default_factory=list)
    implicit_deadline: Optional[str] = None
    level: TaskLevel = TaskLevel.TASK
    
    # 分類結果 (CLASSIFY フェーズで設定)
    urgency: int = 50       # 0-100
    importance: int = 50    # 0-100
    classification: Classification = Classification.DEFER
    deadline_bucket: DeadlineBucket = DeadlineBucket.BACKLOG
    
    # 見積 (ESTIMATE フェーズで設定)
    estimate_hours: Optional[float] = None
    t_shirt_size: str = "M"


@dataclass
class Dependency:
    """依存関係"""
    from_task_id: str
    to_task_id: str
    dep_type: DependencyType = DependencyType.FS


@dataclass
class Gap:
    """不足情報"""
    task_id: str
    gap_type: GapType
    question: str
    auto_collectible: bool = False
    collector_workflow: Optional[str] = None  # e.g., "/sop"
    resolved: bool = False
    resolution: Optional[str] = None


@dataclass
class TaskTree:
    """タスク階層構造"""
    root_tasks: list[ParsedTask] = field(default_factory=list)
    children: dict[str, list[str]] = field(default_factory=dict)  # parent_id -> [child_ids]
    
    def add_child(self, parent_id: str, child_id: str):
        if parent_id not in self.children:
            self.children[parent_id] = []
        self.children[parent_id].append(child_id)


@dataclass
class ScheduleBucket:
    """期限バケット"""
    deadline: DeadlineBucket
    must_tasks: list[ParsedTask] = field(default_factory=list)
    should_tasks: list[ParsedTask] = field(default_factory=list)
    total_hours: float = 0.0
    available_hours: float = 0.0
    is_overflowed: bool = False


@dataclass
class TakResult:
    """
    /tak ワークフロー最終出力
    
    8フェーズの処理結果を統合
    """
    # Input stats
    raw_count: int = 0
    parsed_count: int = 0
    
    # Structured data
    tasks: list[ParsedTask] = field(default_factory=list)
    tree: TaskTree = field(default_factory=TaskTree)
    dependencies: list[Dependency] = field(default_factory=list)
    gaps: list[Gap] = field(default_factory=list)
    
    # Schedule
    buckets: dict[DeadlineBucket, ScheduleBucket] = field(default_factory=dict)
    
    # Metadata
    processed_at: datetime = field(default_factory=datetime.now)
    
    def summary(self) -> str:
        """サマリー文字列生成"""
        must_count = sum(1 for t in self.tasks if t.classification == Classification.MUST)
        should_count = sum(1 for t in self.tasks if t.classification == Classification.SHOULD)
        gaps_unresolved = sum(1 for g in self.gaps if not g.resolved)
        total_hours = sum(t.estimate_hours or 0 for t in self.tasks)
        
        return (
            f"投入: {self.raw_count} → 整理後: {self.parsed_count}タスク | "
            f"Must: {must_count}, Should: {should_count} | "
            f"不足情報: {gaps_unresolved}件 | "
            f"総工数: {total_hours:.1f}h"
        )
