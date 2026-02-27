#!/usr/bin/env python3
# PROOF: [L2/Infra] <- mekhane/symploke/basanos_bridge.py H3→Infra→Symploke
# PURPOSE: Basanos PerspectiveMatrix → Specialist v2 変換アダプタ
"""
Basanos Bridge — PerspectiveMatrix (480 perspectives) → Specialist v2 アダプタ

Basanos の構造化パースペクティブ (20 Domains × 24 Axes) を
Specialist v2 の形式に変換し、jules_daily_scheduler.py から利用可能にする。

Usage:
    from basanos_bridge import BasanosBridge

    bridge = BasanosBridge()
    specialists = bridge.get_perspectives_as_specialists(domains=["Resource", "Error"])
    # → run_slot_batch() に渡せる Specialist リスト
"""

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Optional

# Specialist v2 imports
try:
    from specialist_v2 import Specialist, Archetype, VerdictFormat
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from specialist_v2 import Specialist, Archetype, VerdictFormat

# Basanos imports
try:
    from mekhane.basanos.prompt_generator import PerspectiveMatrix, Perspective
except ImportError:
    import sys
    _basanos_path = str(Path(__file__).parent.parent / "basanos")
    if _basanos_path not in sys.path:
        sys.path.insert(0, _basanos_path)
    from prompt_generator import PerspectiveMatrix, Perspective


# === Constants ===
_PROJECT_ROOT = Path(__file__).parent.parent.parent
BASANOS_ROTATION_FILE = _PROJECT_ROOT / "synergeia" / "basanos_rotation_state.json"

# Axis → Archetype mapping
# O-series (認識・理想) → PRECISION
# S-series (戦略・方法) → AUTONOMY
# H-series (衝動・直感) → CREATIVE
# P-series (環境・境界) → SAFETY
# K-series (文脈・時機) → SPEED
# A-series (精度・判断) → PRECISION
_SERIES_ARCHETYPE: dict[str, Archetype] = {
    "Ousia": Archetype.PRECISION,
    "Schema": Archetype.AUTONOMY,
    "Hormē": Archetype.CREATIVE,
    "Perigraphē": Archetype.SAFETY,
    "Kairos": Archetype.SPEED,
    "Akribeia": Archetype.PRECISION,
}


# PURPOSE: Perspective → Specialist 変換
def perspective_to_specialist(perspective: Perspective) -> Specialist:
    """Basanos Perspective を Specialist v2 に変換する。

    Perspective (20 Domains × 24 Axes):
      domain_id, domain_name, domain_description, domain_keywords,
      axis_id, axis_name, axis_question, axis_focus, theorem

    → Specialist v2:
      id, name, category, archetype, domain, principle,
      perceives, blind_to, measure, verdict, severity_map
    """
    # Axis series からアーキタイプを導出
    # axis_id format: "O1", "S2", "H3" etc.
    series_key = perspective.axis_id[0]
    series_map = {
        "O": "Ousia",
        "S": "Schema",
        "H": "Hormē",
        "P": "Perigraphē",
        "K": "Kairos",
        "A": "Akribeia",
    }
    series_name = series_map.get(series_key, "Ousia")
    archetype = _SERIES_ARCHETYPE.get(series_name, Archetype.PRECISION)

    return Specialist(
        id=f"BP-{perspective.id}",  # BP = Basanos Perspective
        name=f"{perspective.domain_name} × {perspective.axis_name}",
        category=perspective.domain_id.lower(),
        archetype=archetype,
        domain=perspective.domain_description,
        principle=perspective.axis_focus,
        perceives=perspective.domain_keywords,
        blind_to=[],  # Basanos の直交性により、他ドメインは見えない
        measure=perspective.axis_question,
        verdict=VerdictFormat.REVIEW,
        severity_map={},
    )


# PURPOSE: Basanos Bridge クラス
class BasanosBridge:
    """Basanos PerspectiveMatrix と Specialist v2 の統合ブリッジ。

    機能:
      - Perspective → Specialist 変換
      - ドメインサンプリング (ローテーション付き)
      - Basanos テンプレートを使ったプロンプト生成
    """

    def __init__(self, perspectives_path: Optional[Path] = None):
        """Initialize bridge with perspective matrix."""
        self._matrix = PerspectiveMatrix.load(perspectives_path)
        self._all_domains = self._matrix.domains
        self._all_axes = self._matrix.axes

    @property
    def total_perspectives(self) -> int:
        """Total number of available perspectives."""
        return self._matrix.total_perspectives

    @property
    def all_domains(self) -> list[str]:
        """All available domain IDs."""
        return list(self._all_domains)

    @property
    def all_axes(self) -> list[str]:
        """All available axis IDs."""
        return list(self._all_axes)

    # PURPOSE: Perspective を Specialist に変換して返す
    def get_perspectives_as_specialists(
        self,
        domains: Optional[list[str]] = None,
        axes: Optional[list[str]] = None,
    ) -> list[Specialist]:
        """指定ドメイン/軸の Perspective を Specialist 形式で返す。

        Args:
            domains: 対象ドメイン (None = 全ドメイン)
            axes: 対象軸 (None = 全軸)

        Returns:
            Specialist リスト (run_slot_batch 互換)
        """
        target_domains = domains or self._all_domains
        target_axes = axes or self._all_axes

        specialists = []
        for domain_id in target_domains:
            for axis_id in target_axes:
                try:
                    perspective = self._matrix.get(domain_id, axis_id)
                    specialists.append(perspective_to_specialist(perspective))
                except KeyError:
                    continue

        return specialists

    # PURPOSE: ローテーション付きドメインサンプリング
    def sample_domains(self, n: int, seed: Optional[int] = None) -> list[str]:
        """ローテーション付きでドメインをサンプリングする。

        前回選ばれたドメインを避け、未選択のドメインを優先的に選択する。

        Args:
            n: サンプリング数
            seed: ランダムシード (テスト用)

        Returns:
            選択されたドメイン ID のリスト
        """
        rotation = self._load_rotation()
        last_used = set(rotation.get("last_domains", []))
        all_domains = list(self._all_domains)

        # 前回使っていないドメインを優先
        fresh = [d for d in all_domains if d not in last_used]
        stale = [d for d in all_domains if d in last_used]

        if seed is not None:
            rng = random.Random(seed)
        else:
            rng = random.Random()

        rng.shuffle(fresh)
        rng.shuffle(stale)

        # fresh を先に、足りなければ stale から補充
        selected = (fresh + stale)[:n]

        # ローテーション更新
        rotation["last_domains"] = selected
        rotation["last_date"] = datetime.now().strftime("%Y-%m-%d")
        rotation["cycle"] = rotation.get("cycle", 0) + 1
        self._save_rotation(rotation)

        return selected

    # PURPOSE: Basanos テンプレートを使ったプロンプト生成
    def generate_perspective_prompt(
        self,
        domain_id: str,
        axis_id: str,
        target_file: str,
    ) -> str:
        """Basanos テンプレートを使ってレビュープロンプトを生成する。

        specialist_v2.generate_prompt() と互換の出力を返す。
        """
        perspective = self._matrix.get(domain_id, axis_id)
        base_prompt = self._matrix.generate_prompt(perspective)

        return (
            f"{base_prompt}\n\n"
            f"## Target File\n\n"
            f"Review the following file: `{target_file}`\n"
        )

    # PURPOSE: F8 Dynamic Perspective 統合
    def get_dynamic_perspectives(
        self,
        file_path: str,
        audit_issues: Optional[list[str]] = None,
        max_perspectives: int = 24,
    ) -> list[Specialist]:
        """ファイル特性に基づいて動的に Perspective を生成し Specialist 形式で返す。

        DynamicPerspectiveGenerator を内部で使い、ファイルの AST/pattern/issue に
        基づいた adaptive な Specialist セットを返す。

        Args:
            file_path: 対象ファイルパス
            audit_issues: AIAuditor が検出した issue コード (AI-xxx)
            max_perspectives: 最大 perspective 数

        Returns:
            Specialist リスト (run_slot_batch 互換)
        """
        try:
            from dynamic_perspective_generator import DynamicPerspectiveGenerator
        except ImportError:
            import sys as _sys
            _dpg_path = str(Path(__file__).parent)
            if _dpg_path not in _sys.path:
                _sys.path.insert(0, _dpg_path)
            from dynamic_perspective_generator import DynamicPerspectiveGenerator

        gen = DynamicPerspectiveGenerator(max_perspectives=max_perspectives)
        dynamic_perps = gen.generate_for_file(file_path, audit_issues=audit_issues)

        # DynamicPerspective → Specialist v2 変換
        specialists = []
        for dp in dynamic_perps:
            specialists.append(Specialist(
                id=dp.id,
                name=f"Dynamic: {dp.domain} — {dp.focus}",
                category=dp.domain.lower().replace("-", "_"),
                archetype=Archetype.PRECISION,
                domain=dp.domain,
                principle=dp.focus,
                perceives=[dp.focus],
                blind_to=[],
                measure=f"Evaluate {dp.focus} in this file",
                verdict=VerdictFormat.REVIEW,
                severity_map={},
            ))

        return specialists

    # --- Internal rotation state ---

    def _load_rotation(self) -> dict:
        """Load basanos rotation state."""
        if BASANOS_ROTATION_FILE.exists():
            try:
                return json.loads(BASANOS_ROTATION_FILE.read_text())
            except (json.JSONDecodeError, OSError):
                pass
        return {"last_domains": [], "cycle": 0}

    def _save_rotation(self, state: dict) -> None:
        """Save basanos rotation state."""
        BASANOS_ROTATION_FILE.parent.mkdir(parents=True, exist_ok=True)
        BASANOS_ROTATION_FILE.write_text(
            json.dumps(state, indent=2, ensure_ascii=False)
        )


# === CLI ===

if __name__ == "__main__":
    bridge = BasanosBridge()
    print(f"=== Basanos Bridge ===")
    print(f"Total perspectives: {bridge.total_perspectives}")
    print(f"Domains: {len(bridge.all_domains)}")
    print(f"Axes: {len(bridge.all_axes)}")
    print()

    # Sample 5 domains
    sampled = bridge.sample_domains(5, seed=42)
    print(f"Sampled domains: {sampled}")

    # Convert to specialists
    specs = bridge.get_perspectives_as_specialists(domains=sampled)
    print(f"Generated specialists: {len(specs)}")

    if specs:
        print(f"\nSample specialist:")
        s = specs[0]
        print(f"  ID: {s.id}")
        print(f"  Name: {s.name}")
        print(f"  Category: {s.category}")
        print(f"  Domain: {s.domain}")
        print(f"  Principle: {s.principle}")
        print(f"  Perceives: {s.perceives}")
