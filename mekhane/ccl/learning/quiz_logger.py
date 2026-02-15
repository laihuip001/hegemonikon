# PROOF: [L2/インフラ] <- mekhane/ccl/learning/
# G4: クイズ効果ログ

"""
Quiz Effect Logger — クイズの生成・回答・効果を記録

目的:
- generate_quiz() が生成したクイズの追跡
- 回答有無と効果 (正解率、失敗回避) を記録
- 演算子ごとの理解度トレンドを可視化可能にする

Usage:
    from mekhane.ccl.learning.quiz_logger import QuizLogger, get_quiz_logger

    logger = get_quiz_logger()
    entry_id = logger.log_quiz_generated(ccl_expr="/noe!", operators={"!"})
    logger.log_quiz_answered(entry_id, answered=True, correct=True)
    logger.log_quiz_effect(entry_id, had_failure=False)

    stats = logger.get_operator_stats("!")
    print(stats)  # {"total": 5, "answered": 4, "correct": 3, "prevented_failures": 2}
"""

import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional


@dataclass
class QuizEntry:
    """クイズログの1エントリ"""
    id: str                          # ISO timestamp ベースの一意ID
    ccl_expr: str                    # 対象の CCL 式
    operators: List[str]             # クイズ対象の演算子群
    generated_at: str                # 生成日時
    answered: Optional[bool] = None  # 回答されたか
    correct: Optional[bool] = None   # 正解だったか
    had_failure: Optional[bool] = None  # その後の実行で失敗があったか
    notes: str = ""                  # 自由記述メモ


class QuizLogger:
    """クイズ効果ログの管理"""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (
            Path(__file__).parent.parent.parent.parent
            / "data" / "quiz_log.json"
        )
        self._entries: List[QuizEntry] = []
        self._load()

    def _load(self) -> None:
        """永続化ファイルから読み込み"""
        if self.db_path.exists():
            try:
                data = json.loads(self.db_path.read_text(encoding="utf-8"))
                self._entries = [QuizEntry(**e) for e in data]
            except (json.JSONDecodeError, TypeError, KeyError):
                self._entries = []

    def _save(self) -> None:
        """永続化ファイルに書き込み"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        data = [asdict(e) for e in self._entries]
        self.db_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def log_quiz_generated(
        self,
        ccl_expr: str,
        operators: set,
    ) -> str:
        """クイズ生成を記録し、エントリIDを返す"""
        entry_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        entry = QuizEntry(
            id=entry_id,
            ccl_expr=ccl_expr,
            operators=sorted(operators),
            generated_at=datetime.now().isoformat(),
        )
        self._entries.append(entry)
        self._save()
        return entry_id

    def log_quiz_answered(
        self,
        entry_id: str,
        answered: bool,
        correct: Optional[bool] = None,
    ) -> bool:
        """クイズ回答を記録"""
        for e in self._entries:
            if e.id == entry_id:
                e.answered = answered
                e.correct = correct
                self._save()
                return True
        return False

    def log_quiz_effect(
        self,
        entry_id: str,
        had_failure: bool,
        notes: str = "",
    ) -> bool:
        """クイズ後の実行効果を記録"""
        for e in self._entries:
            if e.id == entry_id:
                e.had_failure = had_failure
                if notes:
                    e.notes = notes
                self._save()
                return True
        return False

    def get_operator_stats(self, operator: str) -> Dict[str, int]:
        """演算子ごとの統計を取得"""
        relevant = [e for e in self._entries if operator in e.operators]
        total = len(relevant)
        answered = sum(1 for e in relevant if e.answered is True)
        correct = sum(1 for e in relevant if e.correct is True)
        prevented = sum(
            1 for e in relevant
            if e.answered is True and e.had_failure is False
        )
        return {
            "total": total,
            "answered": answered,
            "correct": correct,
            "prevented_failures": prevented,
        }

    def get_all_stats(self) -> Dict[str, Dict[str, int]]:
        """全演算子の統計を辞書で返す"""
        all_ops: set = set()
        for e in self._entries:
            all_ops.update(e.operators)
        return {op: self.get_operator_stats(op) for op in sorted(all_ops)}

    @property
    def entries(self) -> List[QuizEntry]:
        return list(self._entries)


# シングルトン
_instance: Optional[QuizLogger] = None


def get_quiz_logger(db_path: Optional[Path] = None) -> QuizLogger:
    """QuizLogger のシングルトンインスタンスを取得"""
    global _instance
    if _instance is None:
        _instance = QuizLogger(db_path)
    return _instance
