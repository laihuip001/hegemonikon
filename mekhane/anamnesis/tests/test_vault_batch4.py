#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/anamnesis/tests/
# PURPOSE: VaultManager の包括テスト
"""Anamnesis Vault Tests — Batch 4"""

import pytest
from pathlib import Path
from mekhane.anamnesis.vault import VaultManager


class TestVaultWriteSafe:
    """VaultManager.write_safe のテスト"""

    def test_write_new_file(self, tmp_path):
        target = tmp_path / "test.txt"
        result = VaultManager.write_safe(target, "Hello")
        assert result == target
        assert target.read_text() == "Hello"

    def test_write_creates_dirs(self, tmp_path):
        target = tmp_path / "a" / "b" / "c" / "test.txt"
        VaultManager.write_safe(target, "Deep")
        assert target.read_text() == "Deep"

    def test_write_with_backup(self, tmp_path):
        target = tmp_path / "test.txt"
        target.write_text("Original")
        VaultManager.write_safe(target, "Updated")
        assert target.read_text() == "Updated"
        backup = target.with_suffix(".txt.bak")
        assert backup.exists()
        assert backup.read_text() == "Original"

    def test_write_without_backup(self, tmp_path):
        target = tmp_path / "test.txt"
        target.write_text("Original")
        VaultManager.write_safe(target, "Updated", backup=False)
        assert target.read_text() == "Updated"
        backup = target.with_suffix(".txt.bak")
        assert not backup.exists()

    def test_write_returns_path(self, tmp_path):
        target = tmp_path / "test.txt"
        result = VaultManager.write_safe(target, "Content")
        assert isinstance(result, Path)
        assert result == target

    def test_write_utf8(self, tmp_path):
        target = tmp_path / "test.txt"
        VaultManager.write_safe(target, "日本語テスト")
        assert target.read_text(encoding="utf-8") == "日本語テスト"

    def test_write_overwrite(self, tmp_path):
        target = tmp_path / "test.txt"
        VaultManager.write_safe(target, "First")
        VaultManager.write_safe(target, "Second")
        assert target.read_text() == "Second"

    def test_write_empty(self, tmp_path):
        target = tmp_path / "test.txt"
        VaultManager.write_safe(target, "")
        assert target.read_text() == ""

    def test_write_multiline(self, tmp_path):
        target = tmp_path / "test.txt"
        content = "Line 1\nLine 2\nLine 3\n"
        VaultManager.write_safe(target, content)
        assert target.read_text() == content


class TestVaultReadSafe:
    """VaultManager.read_safe のテスト"""

    def test_read_existing(self, tmp_path):
        target = tmp_path / "test.txt"
        target.write_text("Content")
        result = VaultManager.read_safe(target)
        assert result == "Content"

    def test_read_nonexistent(self, tmp_path):
        target = tmp_path / "nonexistent.txt"
        with pytest.raises(FileNotFoundError):
            VaultManager.read_safe(target)

    def test_read_from_backup(self, tmp_path):
        target = tmp_path / "test.txt"
        backup = target.with_suffix(".txt.bak")
        backup.write_text("Backup content")
        result = VaultManager.read_safe(target)
        assert result == "Backup content"

    def test_read_utf8(self, tmp_path):
        target = tmp_path / "test.txt"
        target.write_text("日本語", encoding="utf-8")
        result = VaultManager.read_safe(target)
        assert result == "日本語"


class TestVaultRoundtrip:
    """write_safe → read_safe ラウンドトリップテスト"""

    def test_roundtrip(self, tmp_path):
        target = tmp_path / "roundtrip.txt"
        content = "Round trip content with 日本語"
        VaultManager.write_safe(target, content)
        result = VaultManager.read_safe(target)
        assert result == content

    def test_roundtrip_multiple(self, tmp_path):
        for i in range(5):
            target = tmp_path / f"file_{i}.txt"
            content = f"Content {i}"
            VaultManager.write_safe(target, content)
            assert VaultManager.read_safe(target) == content
