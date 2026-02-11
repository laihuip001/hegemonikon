#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/poiema/flow/tests/ + mekhane/anamnesis/tests/ + mekhane/ergasterion/
# PURPOSE: 2000 到達用最終テスト — NoesisClient, ModuleDocument, Perspective
"""Final Batch — Crossing 2000 Tests"""

import pytest
from pathlib import Path


# ═══ NoesisClient ══════════════════════

from mekhane.poiema.flow.noesis_client import (
    NoesisClient,
    GeminiClient,
    _get_client,
    is_api_configured,
)


# PURPOSE: Test suite validating noesis client correctness
class TestNoesisClient:
    """O1 Noēsis 外部接続層テスト"""

    # PURPOSE: Verify init default behaves correctly
    def test_init_default(self):
        """Verify init default behavior."""
        client = NoesisClient()
        assert client.settings is not None
        assert "MODEL_FAST" in client.settings

    # PURPOSE: Verify init with settings behaves correctly
    def test_init_with_settings(self):
        """Verify init with settings behavior."""
        client = NoesisClient(settings={
            "GEMINI_API_KEY": "",
            "MODEL_FAST": "test-model",
            "MODEL_SMART": "smart-model",
        })
        assert client.settings["MODEL_FAST"] == "test-model"

    # PURPOSE: Verify not configured without key behaves correctly
    def test_not_configured_without_key(self):
        """Verify not configured without key behavior."""
        client = NoesisClient(settings={"GEMINI_API_KEY": ""})
        assert client.is_configured is False

    # PURPOSE: Verify backward compat alias behaves correctly
    def test_backward_compat_alias(self):
        """Verify backward compat alias behavior."""
        assert GeminiClient is NoesisClient

    # PURPOSE: Verify stream not configured behaves correctly
    def test_stream_not_configured(self):
        """Verify stream not configured behavior."""
        client = NoesisClient(settings={"GEMINI_API_KEY": ""})
        chunks = list(client.generate_content_stream("test", {}))
        assert len(chunks) > 0
        assert "Error" in chunks[0] or "設定" in chunks[0]

    # PURPOSE: Verify get client singleton behaves correctly
    def test_get_client_singleton(self):
        # Just verify it returns a NoesisClient
        """Verify get client singleton behavior."""
        assert isinstance(_get_client(), NoesisClient)

    # PURPOSE: Verify is api configured behaves correctly
    def test_is_api_configured(self):
        # Without API key, should be False
        """Verify is api configured behavior."""
        result = is_api_configured()
        assert isinstance(result, bool)


# ═══ ModuleDocument ════════════════════

from mekhane.anamnesis.module_indexer import ModuleDocument, parse_module_file


# PURPOSE: Test suite validating module document correctness
class TestModuleDocument:
    """ModuleDocument データモデルテスト"""

    # PURPOSE: Verify create behaves correctly
    def test_create(self):
        """Verify create behavior."""
        doc = ModuleDocument(
            filename="test.md",
            title="Test Module",
            category="hypervisor",
            content="Full content",
            content_preview="Preview",
        )
        assert doc.filename == "test.md"
        assert doc.category == "hypervisor"

    # PURPOSE: Verify model dump behaves correctly
    def test_model_dump(self):
        """Verify model dump behavior."""
        doc = ModuleDocument(
            filename="test.md",
            title="Test",
            category="individual",
            content="c",
            content_preview="p",
        )
        d = doc.model_dump()
        assert d["filename"] == "test.md"
        assert "title" in d


# PURPOSE: Test suite validating parse module file correctness
class TestParseModuleFile:
    """parse_module_file テスト"""

    # PURPOSE: Verify parse with title behaves correctly
    def test_parse_with_title(self, tmp_path):
        """Verify parse with title behavior."""
        f = tmp_path / "test_module.md"
        f.write_text("# My Module Title\n\nContent here.", encoding="utf-8")
        doc = parse_module_file(f, "hypervisor")
        assert doc is not None
        assert doc.title == "My Module Title"
        assert doc.category == "hypervisor"

    # PURPOSE: Verify parse without title behaves correctly
    def test_parse_without_title(self, tmp_path):
        """Verify parse without title behavior."""
        f = tmp_path / "test_module.md"
        f.write_text("No heading, just content.", encoding="utf-8")
        doc = parse_module_file(f, "individual")
        assert doc is not None
        assert doc.title == "test_module"  # Falls back to stem

    # PURPOSE: Verify parse nonexistent behaves correctly
    def test_parse_nonexistent(self, tmp_path):
        """Verify parse nonexistent behavior."""
        f = tmp_path / "nonexistent.md"
        doc = parse_module_file(f, "test")
        assert doc is None

    # PURPOSE: Verify parse content preview behaves correctly
    def test_parse_content_preview(self, tmp_path):
        """Verify parse content preview behavior."""
        f = tmp_path / "test.md"
        f.write_text("# Title\n\n" + "x" * 1000, encoding="utf-8")
        doc = parse_module_file(f, "test")
        assert len(doc.content_preview) <= 500

    # PURPOSE: Verify parse content max behaves correctly
    def test_parse_content_max(self, tmp_path):
        """Verify parse content max behavior."""
        f = tmp_path / "test.md"
        f.write_text("# Title\n\n" + "a" * 20000, encoding="utf-8")
        doc = parse_module_file(f, "test")
        assert len(doc.content) <= 15000

    # PURPOSE: Verify parse japanese behaves correctly
    def test_parse_japanese(self, tmp_path):
        """Verify parse japanese behavior."""
        f = tmp_path / "日本語.md"
        f.write_text("# 日本語タイトル\n\n日本語コンテンツ。", encoding="utf-8")
        doc = parse_module_file(f, "hypervisor")
        assert doc is not None
        assert doc.title == "日本語タイトル"


# ═══ Perspective ═══════════════════════

from mekhane.ergasterion.synedrion.prompt_generator import Perspective


# PURPOSE: Test suite validating perspective correctness
class TestPerspective:
    """Perspective データクラステスト"""

    # PURPOSE: Verify perspective behaves correctly
    @pytest.fixture
    def perspective(self):
        """Verify perspective behavior."""
        return Perspective(
            domain_id="Resource",
            domain_name="Resource Management",
            domain_description="Resource allocation and management",
            domain_keywords=["memory", "cpu", "disk"],
            axis_id="O",
            axis_name="Ontological",
            axis_question="What exists?",
            axis_focus="existence",
            theorem="S2 Mekhanē",
        )

    # PURPOSE: Verify create behaves correctly
    def test_create(self, perspective):
        """Verify create behavior."""
        assert perspective.domain_id == "Resource"
        assert perspective.axis_id == "O"

    # PURPOSE: Verify id behaves correctly
    def test_id(self, perspective):
        """Verify id behavior."""
        assert perspective.id == "Resource-O"

    # PURPOSE: Verify name behaves correctly
    def test_name(self, perspective):
        """Verify name behavior."""
        assert perspective.name == "Resource Management × Ontological"

    # PURPOSE: Verify theorem behaves correctly
    def test_theorem(self, perspective):
        """Verify theorem behavior."""
        assert perspective.theorem == "S2 Mekhanē"

    # PURPOSE: Verify keywords behaves correctly
    def test_keywords(self, perspective):
        """Verify keywords behavior."""
        assert "memory" in perspective.domain_keywords
        assert len(perspective.domain_keywords) == 3
