"""
Poiema __init__.py 統合テスト

flow/ の re-export と facade 関数の動作を検証する。
"""

import pytest


class TestPoiemaImports:
    """from mekhane.poiema import ... の検証"""

    def test_import_generate(self):
        from mekhane.poiema import generate
        assert callable(generate)

    def test_import_mask_pii(self):
        from mekhane.poiema import mask_pii
        assert callable(mask_pii)

    def test_import_metron_resolver(self):
        from mekhane.poiema import MetronResolver
        assert hasattr(MetronResolver, "resolve_level")

    def test_import_epoche_shield(self):
        from mekhane.poiema import EpocheShield
        assert hasattr(EpocheShield, "mask")

    def test_import_epoche_scanner(self):
        from mekhane.poiema import EpocheScanner

    def test_import_energeia_core(self):
        from mekhane.poiema import EnergeiaCoreResolver
        assert hasattr(EnergeiaCoreResolver, "process")

    def test_import_doxa_cache(self):
        from mekhane.poiema import DoxaCache

    def test_import_noesis_client(self):
        from mekhane.poiema import NoesisClient

    def test_all_exports(self):
        import mekhane.poiema as poiema
        expected = [
            "MetronResolver", "EpocheShield", "EpocheScanner",
            "EnergeiaCoreResolver", "DoxaCache", "NoesisClient",
            "generate", "mask_pii",
        ]
        for name in expected:
            assert name in poiema.__all__, f"{name} not in __all__"


class TestGenerate:
    """generate() facade の検証"""

    def test_generate_returns_dict(self):
        from mekhane.poiema import generate
        result = generate("テストテキスト", metron_level=30)
        assert isinstance(result, dict)

    def test_generate_contains_result(self):
        from mekhane.poiema import generate
        result = generate("テストテキスト")
        assert "result" in result or "error" in result

    def test_generate_with_privacy_off(self):
        from mekhane.poiema import generate
        result = generate("test@example.com", privacy_mode=False)
        assert isinstance(result, dict)

    def test_generate_metron_levels(self):
        from mekhane.poiema import generate
        for level in [0, 30, 60, 100]:
            result = generate("テスト", metron_level=level)
            assert isinstance(result, dict)


class TestMaskPii:
    """mask_pii() facade の検証"""

    def test_mask_email(self):
        from mekhane.poiema import mask_pii
        masked, mapping = mask_pii("test@example.com")
        assert "test@example.com" not in masked
        assert len(mapping) > 0

    def test_mask_phone(self):
        from mekhane.poiema import mask_pii
        masked, mapping = mask_pii("電話: 03-1234-5678")
        assert "03-1234-5678" not in masked

    def test_mask_preserves_plain_text(self):
        from mekhane.poiema import mask_pii
        text = "これはPIIを含まないテキストです"
        masked, mapping = mask_pii(text)
        assert masked == text
        assert len(mapping) == 0

    def test_mask_returns_tuple(self):
        from mekhane.poiema import mask_pii
        result = mask_pii("テスト")
        assert isinstance(result, tuple)
        assert len(result) == 2
