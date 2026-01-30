"""
H4 Doxa Persistence — 信念永続化モジュール

Hegemonikón H-series (Hormē) 定理: H4 Doxa
FEP層での信念の記録と永続化を担当。

Architecture:
- H4 Doxa = 信念の永続化 (pers/evol/arch)
- 他の H1-H3 は horme_evaluator.py で実装済み

References:
- /dox ワークフロー
- FEP: 信念 = 事後分布として更新される
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class DoxaDerivative(Enum):
    """H4 Doxa の派生モード"""
    PERSIST = "pers"    # 永続化 (保存)
    EVOLVE = "evol"     # 進化 (更新)
    ARCHIVE = "arch"    # アーカイブ (履歴化)


class BeliefStrength(Enum):
    """信念の強さ"""
    WEAK = "weak"         # 弱い (容易に変わる)
    MODERATE = "moderate"  # 中程度
    STRONG = "strong"     # 強い (変わりにくい)
    CORE = "core"         # 核心 (アイデンティティ)


@dataclass
class Belief:
    """信念オブジェクト
    
    Attributes:
        content: 信念の内容
        strength: 信念の強さ
        confidence: 確信度
        created_at: 作成日時
        updated_at: 更新日時
        evidence: 根拠
    """
    content: str
    strength: BeliefStrength
    confidence: float
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    evidence: List[str] = field(default_factory=list)
    
    @property
    def age_days(self) -> float:
        """信念の年齢（日数）"""
        return (datetime.now() - self.created_at).total_seconds() / 86400


@dataclass
class DoxaResult:
    """H4 Doxa 操作結果
    
    Attributes:
        belief: 対象の信念
        derivative: 派生モード
        action_taken: 実行したアクション
        previous_state: 前の状態 (進化時)
        success: 成功したか
    """
    belief: Belief
    derivative: DoxaDerivative
    action_taken: str
    previous_state: Optional[Belief]
    success: bool


class DoxaStore:
    """H4 Doxa 信念ストア
    
    信念の永続化を管理。ファイルに自動保存。
    """
    
    DEFAULT_PATH = "/home/laihuip001/oikos/mneme/.hegemonikon/doxa_beliefs.json"
    
    def __init__(self, path: Optional[str] = None):
        self._path = path or self.DEFAULT_PATH
        self._beliefs: Dict[str, Belief] = {}
        self._archive: List[Belief] = []
        self._load()
    
    def _load(self) -> None:
        """ファイルから信念を読み込み"""
        import json
        from pathlib import Path
        
        path = Path(self._path)
        if not path.exists():
            return
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for item in data.get("beliefs", []):
                belief = Belief(
                    content=item["content"],
                    strength=BeliefStrength(item["strength"]),
                    confidence=item["confidence"],
                    created_at=datetime.fromisoformat(item["created_at"]),
                    updated_at=datetime.fromisoformat(item["updated_at"]),
                    evidence=item.get("evidence", []),
                )
                self._beliefs[belief.content] = belief
            
            for item in data.get("archive", []):
                belief = Belief(
                    content=item["content"],
                    strength=BeliefStrength(item["strength"]),
                    confidence=item["confidence"],
                    created_at=datetime.fromisoformat(item["created_at"]),
                    updated_at=datetime.fromisoformat(item["updated_at"]),
                    evidence=item.get("evidence", []),
                )
                self._archive.append(belief)
        except Exception as e:
            print(f"⚠️ Doxa 読み込みエラー: {e}")
    
    def _save(self) -> None:
        """信念をファイルに保存"""
        import json
        from pathlib import Path
        
        path = Path(self._path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "beliefs": [
                {
                    "content": b.content,
                    "strength": b.strength.value,
                    "confidence": b.confidence,
                    "created_at": b.created_at.isoformat(),
                    "updated_at": b.updated_at.isoformat(),
                    "evidence": b.evidence,
                }
                for b in self._beliefs.values()
            ],
            "archive": [
                {
                    "content": b.content,
                    "strength": b.strength.value,
                    "confidence": b.confidence,
                    "created_at": b.created_at.isoformat(),
                    "updated_at": b.updated_at.isoformat(),
                    "evidence": b.evidence,
                }
                for b in self._archive
            ],
        }
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def persist(self, content: str, strength: BeliefStrength = BeliefStrength.MODERATE,
                confidence: float = 0.7, evidence: Optional[List[str]] = None) -> DoxaResult:
        """信念を永続化"""
        belief = Belief(
            content=content,
            strength=strength,
            confidence=confidence,
            evidence=evidence or [],
        )
        self._beliefs[content] = belief
        self._save()  # 自動保存
        
        return DoxaResult(
            belief=belief,
            derivative=DoxaDerivative.PERSIST,
            action_taken="永続化",
            previous_state=None,
            success=True,
        )
    
    def evolve(self, content: str, new_confidence: float,
               new_evidence: Optional[List[str]] = None) -> DoxaResult:
        """信念を進化（更新）"""
        if content not in self._beliefs:
            return DoxaResult(
                belief=Belief(content=content, strength=BeliefStrength.WEAK, confidence=0.0),
                derivative=DoxaDerivative.EVOLVE,
                action_taken="進化失敗（信念が存在しない）",
                previous_state=None,
                success=False,
            )
        
        previous = self._beliefs[content]
        updated = Belief(
            content=content,
            strength=previous.strength,
            confidence=new_confidence,
            created_at=previous.created_at,
            updated_at=datetime.now(),
            evidence=previous.evidence + (new_evidence or []),
        )
        
        # 確信度に基づいて強さを調整
        if new_confidence >= 0.9:
            updated.strength = BeliefStrength.STRONG
        elif new_confidence >= 0.7:
            updated.strength = BeliefStrength.MODERATE
        else:
            updated.strength = BeliefStrength.WEAK
        
        self._beliefs[content] = updated
        self._save()  # 自動保存
        
        return DoxaResult(
            belief=updated,
            derivative=DoxaDerivative.EVOLVE,
            action_taken="進化",
            previous_state=previous,
            success=True,
        )
    
    def archive(self, content: str) -> DoxaResult:
        """信念をアーカイブ（履歴化）"""
        if content not in self._beliefs:
            return DoxaResult(
                belief=Belief(content=content, strength=BeliefStrength.WEAK, confidence=0.0),
                derivative=DoxaDerivative.ARCHIVE,
                action_taken="アーカイブ失敗",
                previous_state=None,
                success=False,
            )
        
        belief = self._beliefs.pop(content)
        self._archive.append(belief)
        self._save()  # 自動保存
        
        return DoxaResult(
            belief=belief,
            derivative=DoxaDerivative.ARCHIVE,
            action_taken="アーカイブ",
            previous_state=None,
            success=True,
        )
    
    def get(self, content: str) -> Optional[Belief]:
        """信念を取得"""
        return self._beliefs.get(content)
    
    def list_all(self) -> List[Belief]:
        """全信念をリスト"""
        return list(self._beliefs.values())
    
    def list_archived(self) -> List[Belief]:
        """アーカイブ済みをリスト"""
        return self._archive


# グローバルストア (遅延初期化)
_global_store: Optional[DoxaStore] = None


def get_store() -> DoxaStore:
    """グローバルストアを取得"""
    global _global_store
    if _global_store is None:
        _global_store = DoxaStore()
    return _global_store



def format_doxa_markdown(result: DoxaResult) -> str:
    """H4 Doxa 結果をMarkdown形式でフォーマット"""
    success_emoji = "✅" if result.success else "❌"
    lines = [
        "┌─[H4 Doxa 信念永続化]────────────────────────────────┐",
        f"│ 派生: {result.derivative.value}",
        f"│ 内容: {result.belief.content[:40]}",
        f"│ 強さ: {result.belief.strength.value}",
        f"│ 確信度: {result.belief.confidence:.0%}",
        f"│ アクション: {success_emoji} {result.action_taken}",
        "└──────────────────────────────────────────────────┘",
    ]
    return "\n".join(lines)


def encode_doxa_observation(result: DoxaResult) -> dict:
    """FEP観察空間へのエンコード"""
    # 強さ → confidence
    strength_map = {
        BeliefStrength.WEAK: 0.3,
        BeliefStrength.MODERATE: 0.5,
        BeliefStrength.STRONG: 0.7,
        BeliefStrength.CORE: 0.9,
    }
    confidence = strength_map[result.belief.strength]
    
    # 信念の年齢 → context_clarity (古い信念は高clarity)
    context_clarity = min(1.0, 0.5 + result.belief.age_days * 0.01)
    
    # 派生 → urgency
    urgency_map = {
        DoxaDerivative.PERSIST: 0.3,
        DoxaDerivative.EVOLVE: 0.5,
        DoxaDerivative.ARCHIVE: 0.2,
    }
    urgency = urgency_map[result.derivative]
    
    return {
        "context_clarity": context_clarity,
        "urgency": urgency,
        "confidence": confidence,
    }
