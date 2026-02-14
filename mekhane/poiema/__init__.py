# PROOF: [L2/インフラ] <- mekhane/poiema/ O4→創造機能が必要
# Hegemonikón poiēma (ποίημα) Layer
# Products built using Hegemonikón design principles
"""
Poiema — 構造化出力の生成エンジン

統合 facade: flow/ の全モジュールを re-export し、
パッケージレベルの便利関数 (generate, mask_pii) を提供する。

Usage::

    from mekhane.poiema import generate, mask_pii, MetronResolver

    # テキスト処理パイプライン
    result = generate("入力テキスト", metron_level=60)

    # PII マスキング
    masked, mapping = mask_pii("氏名: 田中太郎")
"""

from .flow import (
    MetronResolver,
    EpocheShield,
    EpocheScanner,
    EnergeiaCoreResolver,
    DoxaCache,
    NoesisClient,
)

__all__ = [
    # flow/ re-exports
    "MetronResolver",
    "EpocheShield",
    "EpocheScanner",
    "EnergeiaCoreResolver",
    "DoxaCache",
    "NoesisClient",
    # convenience functions
    "generate",
    "mask_pii",
]


# PURPOSE: テキスト処理パイプラインの統合エントリポイント
def generate(
    text: str,
    metron_level: int = 60,
    privacy_mode: bool = True,
    settings: dict | None = None,
) -> dict:
    """
    テキスト処理パイプラインの統合エントリポイント。

    EnergeiaCoreResolver のラッパーとして、
    Metron (尺度) → Epochē (PII保護) → Noēsis (AI生成) → Epochē (復元)
    の全処理を同期的に実行する。

    Args:
        text: 入力テキスト
        metron_level: 処理レベル (0-100)。
            0=LIGHT, 30=MEDIUM, 60=RICH, 100=DEEP
        privacy_mode: PII マスキングの有効化 (default: True)
        settings: カスタム設定辞書 (optional)

    Returns:
        dict: {"result": str, "metron_level": int, "model_used": str, ...}
              失敗時: {"error": str, "message": str}
    """
    cfg = settings or {}
    cfg.setdefault("PRIVACY_MODE", privacy_mode)

    core = EnergeiaCoreResolver(settings=cfg)
    return core.process_sync(text, metron_level=metron_level)


# PURPOSE: PII マスキングの convenience wrapper
def mask_pii(text: str) -> tuple[str, dict[str, str]]:
    """
    PII マスキングの convenience wrapper。

    EpocheShield を使用してテキスト内の個人情報を検出・マスクする。

    Args:
        text: マスク対象テキスト

    Returns:
        (masked_text, pii_mapping):
            masked_text: マスク後のテキスト
            pii_mapping: {placeholder: original_value} の辞書
    """
    shield = EpocheShield()
    return shield.mask(text)
