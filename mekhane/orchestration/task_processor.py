"""
/tak - Task Orchestration Module
PHASE 2-7: Processing Pipeline

CLASSIFY → STRUCTURE → DEPEND → GAP → ESTIMATE → SCHEDULE
"""
from datetime import date, timedelta
from typing import Optional
from .models import (
    ParsedTask, 
    Classification, 
    DeadlineBucket,
    TaskLevel,
    TaskTree,
    Dependency,
    DependencyType,
    Gap,
    GapType,
    ScheduleBucket,
    TakResult,
)


class TaskClassifier:
    """
    PHASE 2: CLASSIFY - 優先度・緊急度分類
    
    Eisenhower Matrix 拡張: 緊急度 × 重要度
    """
    
    def classify(self, task: ParsedTask, context: Optional[dict] = None) -> ParsedTask:
        """
        タスクを分類して Classification と DeadlineBucket を設定
        """
        # 緊急度は既にINTAKEで設定済み
        urgency = task.urgency
        
        # 重要度を推定
        importance = self._estimate_importance(task, context)
        task.importance = importance
        
        # Eisenhower Matrixで分類 (閾値を60に調整)
        if urgency >= 60 and importance >= 50:
            task.classification = Classification.MUST
        elif importance >= 50:
            task.classification = Classification.SHOULD
        elif urgency >= 60:
            task.classification = Classification.MUST  # 緊急なものもMUSTに
        else:
            task.classification = Classification.SHOULD  # デフォルトはSHOULD (DEFERは使いにくい)
        
        # DeadlineBucketを設定
        task.deadline_bucket = self._determine_bucket(task)
        
        return task
    
    def _estimate_importance(self, task: ParsedTask, context: Optional[dict] = None) -> int:
        """
        重要度を推定 (0-100)
        
        重要度シグナル:
        - 目的との整合 (/bou 連携 - 将来実装)
        - 影響範囲
        - 価値創出度
        """
        importance = 60  # デフォルト (SHOULD相当)
        
        # キーワードベースの推定
        high_importance_keywords = [
            "重要", "必須", "本質", "コア", "基盤", "critical",
            "収益", "売上", "顧客", "ユーザー", "セキュリティ",
        ]
        low_importance_keywords = [
            "余裕", "できれば", "nice to have", "オプション",
            "実験", "試し", "勉強", "学習",
        ]
        
        text = f"{task.title} {task.description}".lower()
        
        for kw in high_importance_keywords:
            if kw in text:
                importance = min(100, importance + 20)
        
        for kw in low_importance_keywords:
            if kw in text:
                importance = max(0, importance - 15)
        
        return importance
    
    def _determine_bucket(self, task: ParsedTask) -> DeadlineBucket:
        """
        期限バケットを決定
        
        優先順位:
        1. 明示的な期限 (implicit_deadline)
        2. 緊急度ベース
        """
        # 明示的な期限がある場合
        if task.implicit_deadline:
            try:
                return DeadlineBucket(task.implicit_deadline)
            except ValueError:
                pass
        
        # 緊急度ベースで決定 (閾値を調整してより実用的に)
        if task.urgency >= 80:
            return DeadlineBucket.TODAY
        elif task.urgency >= 60:
            return DeadlineBucket.THREE_DAYS
        elif task.urgency >= 40:
            return DeadlineBucket.WEEK
        elif task.urgency >= 20:
            return DeadlineBucket.THREE_WEEKS
        else:
            return DeadlineBucket.TWO_MONTHS


class HierarchyBuilder:
    """
    PHASE 3: STRUCTURE - 階層化
    
    タスクをプロジェクト→エピック→タスク→サブタスクに構造化
    """
    
    def build(self, tasks: list[ParsedTask]) -> TaskTree:
        """
        タスクリストから階層構造を構築
        
        現在の実装: シンプルなフラット構造
        将来: キーワードクラスタリング
        """
        tree = TaskTree()
        
        # 全タスクをルートとして追加 (フェーズ1実装)
        for task in tasks:
            task.level = TaskLevel.TASK
            tree.root_tasks.append(task)
        
        return tree


class DependencyResolver:
    """
    PHASE 4: DEPEND - 依存関係解決
    """
    
    def resolve(self, tasks: list[ParsedTask]) -> list[Dependency]:
        """
        タスク間の依存関係を検出
        
        現在の実装: キーワードマッチング
        将来: 技術的依存の推論
        """
        dependencies = []
        
        # 依存キーワードパターン
        dep_patterns = [
            "の後に", "が終わったら", "に依存", "ブロック",
            "前提", "先に", "完了後",
        ]
        
        task_map = {t.id: t for t in tasks}
        
        for task in tasks:
            text = f"{task.title} {task.description}"
            
            # 他タスクへの言及を検出
            for other in tasks:
                if task.id == other.id:
                    continue
                
                # タイトルの一部が言及されているか
                if other.title[:10] in text:
                    for pattern in dep_patterns:
                        if pattern in text:
                            dependencies.append(Dependency(
                                from_task_id=other.id,
                                to_task_id=task.id,
                                dep_type=DependencyType.FS,
                            ))
                            break
        
        return dependencies


class GapAnalyzer:
    """
    PHASE 5: GAP - 不足情報分析
    """
    
    def analyze(self, tasks: list[ParsedTask]) -> list[Gap]:
        """
        各タスクの不足情報を分析
        """
        gaps = []
        
        for task in tasks:
            # スコープ不足
            if len(task.title) < 10 or "?" in task.title:
                gaps.append(Gap(
                    task_id=task.id,
                    gap_type=GapType.SCOPE,
                    question=f"「{task.title}」のゴールは何ですか？",
                    auto_collectible=False,
                ))
            
            # 期限未設定
            if task.deadline_bucket == DeadlineBucket.BACKLOG:
                gaps.append(Gap(
                    task_id=task.id,
                    gap_type=GapType.DEADLINE,
                    question=f"「{task.title}」の期限は？",
                    auto_collectible=False,
                ))
            
            # 技術的不明点 (キーワードベース)
            tech_uncertain = ["選定", "検討", "調査", "どう", "何を使う"]
            for kw in tech_uncertain:
                if kw in task.description:
                    gaps.append(Gap(
                        task_id=task.id,
                        gap_type=GapType.TECHNICAL,
                        question=f"「{task.title}」の技術選定は？",
                        auto_collectible=True,
                        collector_workflow="/sop",
                    ))
                    break
        
        return gaps


class EffortEstimator:
    """
    PHASE 6: ESTIMATE - 工数見積
    """
    
    def estimate(self, task: ParsedTask) -> ParsedTask:
        """
        タスクの工数を見積もり
        
        現在の実装: キーワードベースの簡易見積
        将来: 類似タスク参照、3点見積
        """
        text = f"{task.title} {task.description}".lower()
        
        # 工数シグナル
        if any(kw in text for kw in ["簡単", "すぐ", "小さい", "micro"]):
            hours = 0.5
            size = "XS"
        elif any(kw in text for kw in ["修正", "バグ", "fix", "調整"]):
            hours = 2.0
            size = "S"
        elif any(kw in text for kw in ["実装", "作る", "新規", "機能"]):
            hours = 4.0
            size = "M"
        elif any(kw in text for kw in ["設計", "アーキテクチャ", "大規模"]):
            hours = 8.0
            size = "L"
        elif any(kw in text for kw in ["プロジェクト", "全体", "移行"]):
            hours = 16.0
            size = "XL"
        else:
            hours = 2.0
            size = "M"
        
        task.estimate_hours = hours
        task.t_shirt_size = size
        
        return task


class ScheduleMatcher:
    """
    PHASE 7: SCHEDULE - スケジュール照合
    """
    
    def match(
        self, 
        tasks: list[ParsedTask],
        available_hours_per_day: float = 6.0,
        today: Optional[date] = None,
    ) -> dict[DeadlineBucket, ScheduleBucket]:
        """
        タスクをスケジュールと照合し、期限バケットに分配
        """
        if today is None:
            today = date.today()
        
        # 各バケットの期限日と可用時間を計算
        bucket_config = {
            DeadlineBucket.TODAY: (0, available_hours_per_day),
            DeadlineBucket.THREE_DAYS: (3, available_hours_per_day * 3),
            DeadlineBucket.WEEK: (7, available_hours_per_day * 5),
            DeadlineBucket.THREE_WEEKS: (21, available_hours_per_day * 15),
            DeadlineBucket.TWO_MONTHS: (60, available_hours_per_day * 40),
        }
        
        buckets = {}
        
        for bucket, (days, available) in bucket_config.items():
            bucket_tasks = [t for t in tasks if t.deadline_bucket == bucket]
            
            must_tasks = [t for t in bucket_tasks if t.classification == Classification.MUST]
            should_tasks = [t for t in bucket_tasks if t.classification == Classification.SHOULD]
            
            total_hours = sum(t.estimate_hours or 0 for t in bucket_tasks)
            
            buckets[bucket] = ScheduleBucket(
                deadline=bucket,
                must_tasks=must_tasks,
                should_tasks=should_tasks,
                total_hours=total_hours,
                available_hours=available,
                is_overflowed=total_hours > available,
            )
        
        return buckets


class TaskOrchestrator:
    """
    /tak メインオーケストレーター
    
    8フェーズのパイプライン全体を統括
    """
    
    def __init__(self):
        self.classifier = TaskClassifier()
        self.hierarchy_builder = HierarchyBuilder()
        self.dependency_resolver = DependencyResolver()
        self.gap_analyzer = GapAnalyzer()
        self.effort_estimator = EffortEstimator()
        self.schedule_matcher = ScheduleMatcher()
    
    def process(self, tasks: list[ParsedTask]) -> TakResult:
        """
        パース済みタスクを全フェーズで処理
        
        Returns:
            TakResult: 統合された処理結果
        """
        result = TakResult()
        result.parsed_count = len(tasks)
        
        # PHASE 2: CLASSIFY
        for task in tasks:
            self.classifier.classify(task)
        
        # PHASE 3: STRUCTURE
        result.tree = self.hierarchy_builder.build(tasks)
        
        # PHASE 4: DEPEND
        result.dependencies = self.dependency_resolver.resolve(tasks)
        
        # PHASE 5: GAP
        result.gaps = self.gap_analyzer.analyze(tasks)
        
        # PHASE 6: ESTIMATE
        for task in tasks:
            self.effort_estimator.estimate(task)
        
        # PHASE 7: SCHEDULE
        result.buckets = self.schedule_matcher.match(tasks)
        
        # 最終結果
        result.tasks = tasks
        
        return result
