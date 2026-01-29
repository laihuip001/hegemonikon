"""
Metron Resolver — S1 Metron Instantiation

Philosophical Reference:
    S1 Metron (尺度): 「どのスケールで考えるか」を決定する
    
Design Principle:
    連続値 (0-100) を離散段階 (Light/Medium/Rich) に正規化
    = 認知負荷の低減 + 柔軟性の維持

Original: Flow AI v4.1 SeasoningManager
Recast: Hegemonikón S1 Metron vocabulary
"""

# Metron Boundaries (尺度境界)
METRON_LIGHT_MAX = 40
METRON_MEDIUM_MAX = 70
METRON_RICH_MAX = 90  # 91-100 is Deep

# Resolved Metron Levels (3-Stage)
METRON_LIGHT = 30
METRON_MEDIUM = 60
METRON_RICH = 100


class MetronResolver:
    """
    S1 Metron の instantiation: 尺度解決器
    
    連続スペクトラム (0-100) を離散段階に正規化し、
    対応するシステムプロンプトを生成する。
    
    Philosophical Mapping:
        - resolve_level(): S1 Metron の核心機能
        - get_system_prompt(): O1 Noēsis との連携（認識の深度を決定）
    """

    @staticmethod
    def get_system_prompt(level: int = METRON_LIGHT_MAX, user_prompt: str = "") -> str:
        """
        システムプロンプト生成
        
        Philosophical Reference:
            O1 Noēsis (認識) の深度を決定する
            level が高いほど、より深い認識・再構築を行う
        """
        level = max(0, min(100, level))

        if level <= METRON_LIGHT_MAX:
            # Light: 最小限の整形。素材を最大限活かす
            # H1 Propatheia (前感情): 第一印象を大切に
            base = (
                "入力文を整形してください。\n"
                "・誤字脱字と句読点を修正\n"
                "・曖昧な表現を明確化\n"
                "・元の意図とトーンは維持\n"
                "出力は整形後のテキストのみ。説明不要。"
            )
        elif level <= METRON_MEDIUM_MAX:
            # Medium: 標準的な下処理
            # S2 Mekhanē (方法): 構造を整理
            base = (
                "入力文をプロンプトとして整形してください。\n"
                "・構造を整理し、要点を明確に\n"
                "・冗長な表現を簡潔に\n"
                "・必要なら箇条書きに変換\n"
                "出力は整形後のテキストのみ。説明不要。"
            )
        elif level <= METRON_RICH_MAX:
            # Rich: 積極的な補完
            # O3 Zētēsis (探求): 足りない情報を推測
            base = (
                "入力文を強化してください。\n"
                "・不足している情報を推測して補完\n"
                "・論理構造を改善\n"
                "・具体例や詳細を追加可\n"
                "出力は強化後のテキストのみ。説明不要。"
            )
        else:
            # Deep: 深い文脈理解
            # O1 Noēsis (認識): 行間を読み、真意を抽出
            base = (
                "入力文を深く解釈し再構築してください。\n"
                "・行間を読み、真意を抽出\n"
                "・欠けているリンクを推測\n"
                "・洞察を加えて昇華させる\n"
                "出力は再構築後のテキストのみ。説明不要。"
            )
        
        if user_prompt:
            return f"{base}\n\n追加指示: {user_prompt}"
        return base

    @staticmethod
    def get_level_label(level: int) -> str:
        """レベルの日本語ラベル"""
        if level <= METRON_LIGHT_MAX:
            return "Light（軽め）"
        if level <= METRON_MEDIUM_MAX:
            return "Medium（標準）"
        if level <= METRON_RICH_MAX:
            return "Rich（濃いめ）"
        return "Deep（深い）"

    @staticmethod
    def resolve_level(level: int) -> int:
        """
        S1 Metron 核心機能: 連続値を3段階に正規化
        
        Args:
            level: 0-100の入力
        
        Returns:
            30 (Light), 60 (Medium), or 100 (Rich)
        """
        if level <= 45:
            return METRON_LIGHT
        if level <= 75:
            return METRON_MEDIUM
        return METRON_RICH


# Backward compatibility alias
SeasoningManager = MetronResolver
