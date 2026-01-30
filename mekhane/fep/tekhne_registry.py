"""
PROOF: このファイルは存在しなければならない

A0 → 認知には行為レパートリ (Tekhnē) がある
   → P4 で「できること」の語彙を定義
   → tekhne_registry が担う

Q.E.D.

---

P4 Tekhnē Registry — 行為レパートリ定義モジュール

Hegemonikón P-series (Perigraphē) 定理: P4 Tekhnē
FEP層での操作モデル (B行列) と行為語彙の定義を担当。

Architecture:
- P4 Tekhnē = 「できること」の空間定義 (行為の基底ベクトル群)
- S2 Mekhanē = 「その空間からどれを選ぶか」の戦略

References:
- /tek ワークフロー (技法選択)
- S2 Mekhanē (tekhne-maker) — 本モジュールの語彙を選択
- FEP: 操作モデル = B行列 (状態遷移の予測)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Any
from enum import Enum
from pathlib import Path
import json


class TechniqueQuadrant(Enum):
    """技法空間の4象限 (Explore/Exploit マトリクス)"""
    EXPERIMENTAL = "experimental"   # Explore × Explore: 実験的技法
    INNOVATIVE = "innovative"       # Explore × Exploit: 革新的応用
    APPLIED = "applied"             # Exploit × Explore: 応用的探索
    ESTABLISHED = "established"     # Exploit × Exploit: 確立技法


class ActionCategory(Enum):
    """行為カテゴリ"""
    COGNITIVE = "cognitive"         # 認知的行為 (/noe, /zet, /bou)
    CREATIVE = "creative"           # 創造的行為 (/mek, /tek)
    EVALUATIVE = "evaluative"       # 評価的行為 (/dia, /syn, /epo)
    EXECUTIVE = "executive"         # 実行的行為 (/ene, /flag)
    TEMPORAL = "temporal"           # 時間的行為 (/chr, /euk)
    PERSISTENCE = "persistence"     # 永続化行為 (/bye, /dox)


@dataclass
class Technique:
    """単一技法の定義
    
    Attributes:
        id: 技法識別子 (例: "noe", "zet", "mek")
        name: 技法名 (例: "Noēsis", "Zētēsis")
        description: 技法の説明
        category: 行為カテゴリ
        quadrant: 技法空間の象限
        prerequisites: 前提条件となる技法
        outputs: 産出物 (例: "insight", "question", "artifact")
        risk_level: リスクレベル (0.0-1.0)
        time_cost: 時間コスト (相対値 1-10)
        success_rate: 成功率の初期推定値 (0.0-1.0)
        keywords: 関連キーワード (検索用)
    """
    id: str
    name: str
    description: str
    category: ActionCategory
    quadrant: TechniqueQuadrant
    prerequisites: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    risk_level: float = 0.3
    time_cost: int = 3
    success_rate: float = 0.7
    keywords: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "quadrant": self.quadrant.value,
            "prerequisites": self.prerequisites,
            "outputs": self.outputs,
            "risk_level": self.risk_level,
            "time_cost": self.time_cost,
            "success_rate": self.success_rate,
            "keywords": self.keywords,
        }


# =============================================================================
# 標準技法レジストリ (Hegemonikón 定理に基づく)
# =============================================================================

STANDARD_TECHNIQUES: Dict[str, Technique] = {
    # O-series (Ousia: 本質)
    "noe": Technique(
        id="noe",
        name="Noēsis",
        description="深い認識・直観的理解",
        category=ActionCategory.COGNITIVE,
        quadrant=TechniqueQuadrant.EXPERIMENTAL,
        outputs=["insight", "pattern", "understanding"],
        risk_level=0.2,
        time_cost=5,
        success_rate=0.8,
        keywords=["認識", "本質", "理解", "直観", "noesis"],
    ),
    "bou": Technique(
        id="bou",
        name="Boulēsis",
        description="意志・目的の明確化",
        category=ActionCategory.COGNITIVE,
        quadrant=TechniqueQuadrant.ESTABLISHED,
        prerequisites=["noe"],
        outputs=["goal", "intention", "priority"],
        risk_level=0.1,
        time_cost=3,
        success_rate=0.9,
        keywords=["意志", "目的", "目標", "boulesis"],
    ),
    "zet": Technique(
        id="zet",
        name="Zētēsis",
        description="探求・問いの発見",
        category=ActionCategory.COGNITIVE,
        quadrant=TechniqueQuadrant.INNOVATIVE,
        outputs=["question", "hypothesis", "research_direction"],
        risk_level=0.3,
        time_cost=4,
        success_rate=0.7,
        keywords=["探求", "問い", "調査", "zetesis"],
    ),
    "ene": Technique(
        id="ene",
        name="Energeia",
        description="行為・実行",
        category=ActionCategory.EXECUTIVE,
        quadrant=TechniqueQuadrant.ESTABLISHED,
        prerequisites=["bou"],
        outputs=["artifact", "change", "result"],
        risk_level=0.4,
        time_cost=7,
        success_rate=0.75,
        keywords=["実行", "行為", "活動", "energeia"],
    ),
    
    # S-series (Schema: 戦略)
    "met": Technique(
        id="met",
        name="Metron",
        description="スケール・粒度の決定",
        category=ActionCategory.COGNITIVE,
        quadrant=TechniqueQuadrant.APPLIED,
        outputs=["scale", "granularity", "scope"],
        risk_level=0.1,
        time_cost=2,
        success_rate=0.85,
        keywords=["スケール", "粒度", "metron"],
    ),
    "mek": Technique(
        id="mek",
        name="Mekhanē",
        description="方法配置・スキル/WF生成",
        category=ActionCategory.CREATIVE,
        quadrant=TechniqueQuadrant.INNOVATIVE,
        outputs=["skill", "workflow", "template"],
        risk_level=0.3,
        time_cost=5,
        success_rate=0.7,
        keywords=["方法", "生成", "tekhne-maker", "mekhane"],
    ),
    "sta": Technique(
        id="sta",
        name="Stathmos",
        description="基準・ベンチマーク設定",
        category=ActionCategory.EVALUATIVE,
        quadrant=TechniqueQuadrant.ESTABLISHED,
        outputs=["criteria", "benchmark", "standard"],
        risk_level=0.1,
        time_cost=2,
        success_rate=0.9,
        keywords=["基準", "ベンチマーク", "stathmos"],
    ),
    "pra": Technique(
        id="pra",
        name="Praxis",
        description="実践・価値実現",
        category=ActionCategory.EXECUTIVE,
        quadrant=TechniqueQuadrant.APPLIED,
        outputs=["practice", "value", "realization"],
        risk_level=0.3,
        time_cost=5,
        success_rate=0.75,
        keywords=["実践", "価値", "praxis"],
    ),
    
    # K-series (Kairos: 時機)
    "euk": Technique(
        id="euk",
        name="Eukairia",
        description="好機判定",
        category=ActionCategory.TEMPORAL,
        quadrant=TechniqueQuadrant.ESTABLISHED,
        outputs=["timing", "opportunity", "readiness"],
        risk_level=0.1,
        time_cost=1,
        success_rate=0.8,
        keywords=["好機", "タイミング", "eukairia"],
    ),
    "chr": Technique(
        id="chr",
        name="Chronos",
        description="時間制約評価",
        category=ActionCategory.TEMPORAL,
        quadrant=TechniqueQuadrant.ESTABLISHED,
        outputs=["deadline", "timeline", "schedule"],
        risk_level=0.1,
        time_cost=1,
        success_rate=0.9,
        keywords=["時間", "期限", "chronos"],
    ),
    "tel": Technique(
        id="tel",
        name="Telos",
        description="目的整合確認",
        category=ActionCategory.EVALUATIVE,
        quadrant=TechniqueQuadrant.ESTABLISHED,
        outputs=["alignment", "direction", "purpose_check"],
        risk_level=0.1,
        time_cost=1,
        success_rate=0.85,
        keywords=["目的", "整合", "telos"],
    ),
    "sop": Technique(
        id="sop",
        name="Sophia",
        description="知恵・調査依頼",
        category=ActionCategory.COGNITIVE,
        quadrant=TechniqueQuadrant.INNOVATIVE,
        outputs=["research", "knowledge", "insight"],
        risk_level=0.2,
        time_cost=4,
        success_rate=0.75,
        keywords=["知恵", "調査", "sophia", "research"],
    ),
    
    # A-series (Akribeia: 精度)
    "dia": Technique(
        id="dia",
        name="Krisis",
        description="判定・検証",
        category=ActionCategory.EVALUATIVE,
        quadrant=TechniqueQuadrant.ESTABLISHED,
        outputs=["verdict", "validation", "decision"],
        risk_level=0.2,
        time_cost=3,
        success_rate=0.8,
        keywords=["判定", "検証", "krisis"],
    ),
    "syn": Technique(
        id="syn",
        name="Synedrion",
        description="偉人評議会・多角評価",
        category=ActionCategory.EVALUATIVE,
        quadrant=TechniqueQuadrant.EXPERIMENTAL,
        outputs=["critique", "perspectives", "consensus"],
        risk_level=0.3,
        time_cost=6,
        success_rate=0.7,
        keywords=["評議", "多角", "synedrion"],
    ),
    "epo": Technique(
        id="epo",
        name="Epochē",
        description="判断停止",
        category=ActionCategory.EVALUATIVE,
        quadrant=TechniqueQuadrant.ESTABLISHED,
        outputs=["suspension", "uncertainty_ack"],
        risk_level=0.1,
        time_cost=1,
        success_rate=0.95,
        keywords=["判断停止", "保留", "epoche"],
    ),
}


class TekhnēRegistry:
    """技法レジストリ
    
    行為可能空間の管理と検索を担当。
    S2 Mekhanē がこのレジストリから技法を選択する。
    """
    
    def __init__(self, techniques: Optional[Dict[str, Technique]] = None):
        """
        Args:
            techniques: カスタム技法辞書 (None で標準技法を使用)
        """
        self._techniques: Dict[str, Technique] = techniques or STANDARD_TECHNIQUES.copy()
        self._usage_counts: Dict[str, int] = {tid: 0 for tid in self._techniques}
        self._success_history: Dict[str, List[bool]] = {tid: [] for tid in self._techniques}
    
    @property
    def techniques(self) -> Dict[str, Technique]:
        """登録済み技法の辞書"""
        return self._techniques
    
    @property
    def size(self) -> int:
        """レジストリサイズ"""
        return len(self._techniques)
    
    def register(self, technique: Technique) -> None:
        """技法を登録
        
        Args:
            technique: 登録する技法
        """
        self._techniques[technique.id] = technique
        if technique.id not in self._usage_counts:
            self._usage_counts[technique.id] = 0
            self._success_history[technique.id] = []
    
    def get(self, technique_id: str) -> Optional[Technique]:
        """IDで技法を取得
        
        Args:
            technique_id: 技法ID
            
        Returns:
            Technique or None
        """
        return self._techniques.get(technique_id)
    
    def search(
        self,
        keyword: Optional[str] = None,
        category: Optional[ActionCategory] = None,
        quadrant: Optional[TechniqueQuadrant] = None,
        max_risk: Optional[float] = None,
        max_time: Optional[int] = None,
    ) -> List[Technique]:
        """条件で技法を検索
        
        Args:
            keyword: キーワード検索 (name, description, keywords に部分一致)
            category: カテゴリフィルタ
            quadrant: 象限フィルタ
            max_risk: 最大リスクレベル
            max_time: 最大時間コスト
            
        Returns:
            マッチした技法のリスト
        """
        results = []
        
        for tech in self._techniques.values():
            # キーワードマッチ
            if keyword:
                keyword_lower = keyword.lower()
                matched = (
                    keyword_lower in tech.name.lower() or
                    keyword_lower in tech.description.lower() or
                    any(keyword_lower in kw.lower() for kw in tech.keywords)
                )
                if not matched:
                    continue
            
            # カテゴリフィルタ
            if category and tech.category != category:
                continue
            
            # 象限フィルタ
            if quadrant and tech.quadrant != quadrant:
                continue
            
            # リスクフィルタ
            if max_risk is not None and tech.risk_level > max_risk:
                continue
            
            # 時間フィルタ
            if max_time is not None and tech.time_cost > max_time:
                continue
            
            results.append(tech)
        
        return results
    
    def get_by_category(self, category: ActionCategory) -> List[Technique]:
        """カテゴリ別に技法を取得"""
        return self.search(category=category)
    
    def get_by_quadrant(self, quadrant: TechniqueQuadrant) -> List[Technique]:
        """象限別に技法を取得"""
        return self.search(quadrant=quadrant)
    
    def record_usage(self, technique_id: str, success: bool) -> None:
        """技法使用を記録 (S2 Mekhanē の学習用)
        
        Args:
            technique_id: 使用した技法ID
            success: 成功したか
        """
        if technique_id in self._usage_counts:
            self._usage_counts[technique_id] += 1
            self._success_history[technique_id].append(success)
    
    def get_empirical_success_rate(self, technique_id: str) -> Optional[float]:
        """経験的成功率を取得
        
        Args:
            technique_id: 技法ID
            
        Returns:
            成功率 (履歴がない場合は None)
        """
        history = self._success_history.get(technique_id, [])
        if not history:
            return None
        return sum(history) / len(history)
    
    def get_statistics(self) -> Dict[str, Any]:
        """レジストリ統計を取得"""
        return {
            "total_techniques": self.size,
            "by_category": {
                cat.value: len(self.get_by_category(cat))
                for cat in ActionCategory
            },
            "by_quadrant": {
                quad.value: len(self.get_by_quadrant(quad))
                for quad in TechniqueQuadrant
            },
            "total_usage": sum(self._usage_counts.values()),
        }
    
    def to_json(self) -> str:
        """JSON形式でエクスポート"""
        data = {
            "techniques": {tid: tech.to_dict() for tid, tech in self._techniques.items()},
            "usage_counts": self._usage_counts,
            "success_history": self._success_history,
        }
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> "TekhnēRegistry":
        """JSONからインポート"""
        data = json.loads(json_str)
        techniques = {}
        for tid, tdata in data.get("techniques", {}).items():
            techniques[tid] = Technique(
                id=tdata["id"],
                name=tdata["name"],
                description=tdata["description"],
                category=ActionCategory(tdata["category"]),
                quadrant=TechniqueQuadrant(tdata["quadrant"]),
                prerequisites=tdata.get("prerequisites", []),
                outputs=tdata.get("outputs", []),
                risk_level=tdata.get("risk_level", 0.3),
                time_cost=tdata.get("time_cost", 3),
                success_rate=tdata.get("success_rate", 0.7),
                keywords=tdata.get("keywords", []),
            )
        registry = cls(techniques)
        registry._usage_counts = data.get("usage_counts", {})
        registry._success_history = data.get("success_history", {})
        return registry


# =============================================================================
# FEP Integration: B行列への変換
# =============================================================================

def encode_technique_as_b_matrix_entry(technique: Technique) -> Dict[str, float]:
    """技法をB行列エントリ (状態遷移確率) に変換
    
    FEP の B行列は「行為による状態遷移確率」を定義。
    技法の成功率とリスクレベルから遷移確率を推定。
    
    Args:
        technique: 技法
        
    Returns:
        {"transition_success": float, "transition_failure": float}
    """
    # 成功時の遷移確率 = success_rate * (1 - risk_level)
    p_success = technique.success_rate * (1 - technique.risk_level)
    p_failure = 1 - p_success
    
    return {
        "transition_success": p_success,
        "transition_failure": p_failure,
        "expected_time": technique.time_cost,
    }


def format_registry_markdown(registry: TekhnēRegistry) -> str:
    """レジストリをMarkdown形式でフォーマット
    
    Args:
        registry: TekhnēRegistry
        
    Returns:
        Markdown文字列
    """
    stats = registry.get_statistics()
    
    lines = [
        "┌─[P4 Tekhnē Registry]────────────────────────────┐",
        f"│ 登録技法数: {stats['total_techniques']}",
        "│",
        "│ カテゴリ別:",
    ]
    
    for cat, count in stats["by_category"].items():
        if count > 0:
            lines.append(f"│   {cat}: {count}")
    
    lines.extend([
        "│",
        "│ 象限別:",
    ])
    
    for quad, count in stats["by_quadrant"].items():
        if count > 0:
            lines.append(f"│   {quad}: {count}")
    
    lines.extend([
        f"│ 総使用回数: {stats['total_usage']}",
        "└──────────────────────────────────────────────────┘",
    ])
    
    return "\n".join(lines)


# Default global registry
_default_registry: Optional[TekhnēRegistry] = None


def get_registry() -> TekhnēRegistry:
    """デフォルトレジストリを取得"""
    global _default_registry
    if _default_registry is None:
        _default_registry = TekhnēRegistry()
    return _default_registry


def search_techniques(keyword: str, **kwargs) -> List[Technique]:
    """グローバルレジストリから技法を検索
    
    Convenience function for S2 Mekhanē integration.
    
    Args:
        keyword: 検索キーワード
        **kwargs: 追加フィルタ
        
    Returns:
        マッチした技法リスト
    """
    return get_registry().search(keyword=keyword, **kwargs)
