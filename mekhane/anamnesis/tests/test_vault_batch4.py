#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/anamnesis/tests/
# PURPOSE: VaultManager の包括テスト
"""Anamnesis Vault Tests — Batch 4"""

import pytest
from pathlib import Path
from mekhane.anamnesis.vault import VaultManager


# PURPOSE: Test suite validating vault write safe correctness
class TestVaultWriteSafe:
    """VaultManager.write_safe のテスト"""

    # PURPOSE: Verify write new file behaves correctly
    def test_write_new_file(self, tmp_path):
        """Verify write new file behavior."""
        target = tmp_path / "test.txt"
        result = VaultManager.write_safe(target, "Hello")
        assert result == target
        assert target.read_text() == "Hello"

    # PURPOSE: Verify write creates dirs behaves correctly
    def test_write_creates_dirs(self, tmp_path):
        """Verify write creates dirs behavior."""
        target = tmp_path / "a" / "b" / "c" / "test.txt"
        VaultManager.write_safe(target, "Deep")
        assert target.read_text() == "Deep"

    # PURPOSE: Verify write with backup behaves correctly
    def test_write_with_backup(self, tmp_path):
        """Verify write with backup behavior."""
        target = tmp_path / "test.txt"
        target.write_text("Original")
        VaultManager.write_safe(target, "Updated")
        assert target.read_text() == "Updated"
        backup = target.with_suffix(".txt.bak")
        assert backup.exists()
        assert backup.read_text() == "Original"

    # PURPOSE: Verify write without backup behaves correctly
    def test_write_without_backup(self, tmp_path):
        """Verify write without backup behavior."""
        target = tmp_path / "test.txt"
        target.write_text("Original")
        VaultManager.write_safe(target, "Updated", backup=False)
        assert target.read_text() == "Updated"
        backup = target.with_suffix(".txt.bak")
        assert not backup.exists()

    # PURPOSE: Verify write returns path behaves correctly
    def test_write_returns_path(self, tmp_path):
        """Verify write returns path behavior."""
        target = tmp_path / "test.txt"
        result = VaultManager.write_safe(target, "Content")
        assert isinstance(result, Path)
        assert result == target

    # PURPOSE: Verify write utf8 behaves correctly
    def test_write_utf8(self, tmp_path):
        """Verify write utf8 behavior."""
        target = tmp_path / "test.txt"
        VaultManager.write_safe(target, "日本語テスト")
        assert target.read_text(encoding="utf-8") == "日本語テスト"

    # PURPOSE: Verify write overwrite behaves correctly
    def test_write_overwrite(self, tmp_path):
        """Verify write overwrite behavior."""
        target = tmp_path / "test.txt"
        VaultManager.write_safe(target, "First")
        VaultManager.write_safe(target, "Second")
        assert target.read_text() == "Second"

    # PURPOSE: Verify write empty behaves correctly
    def test_write_empty(self, tmp_path):
        """Verify write empty behavior."""
        target = tmp_path / "test.txt"
        VaultManager.write_safe(target, "")
        assert target.read_text() == ""

    # PURPOSE: Verify write multiline behaves correctly
    def test_write_multiline(self, tmp_path):
        """Verify write multiline behavior."""
        target = tmp_path / "test.txt"
        content = "Line 1\nLine 2\nLine 3\n"
        VaultManager.write_safe(target, content)
        assert target.read_text() == content


# PURPOSE: Test suite validating vault read safe correctness
class TestVaultReadSafe:
    """VaultManager.read_safe のテスト"""

    # PURPOSE: Verify read existing behaves correctly
    def test_read_existing(self, tmp_path):
        """Verify read existing behavior."""
        target = tmp_path / "test.txt"
        target.write_text("Content")
        result = VaultManager.read_safe(target)
        assert result == "Content"

    # PURPOSE: Verify read nonexistent behaves correctly
    def test_read_nonexistent(self, tmp_path):
        """Verify read nonexistent behavior."""
        target = tmp_path / "nonexistent.txt"
        with pytest.raises(FileNotFoundError):
            VaultManager.read_safe(target)

    # PURPOSE: Verify read from backup behaves correctly
    def test_read_from_backup(self, tmp_path):
        """Verify read from backup behavior."""
        target = tmp_path / "test.txt"
        backup = target.with_suffix(".txt.bak")
        backup.write_text("Backup content")
        result = VaultManager.read_safe(target)
        assert result == "Backup content"

    # PURPOSE: Verify read utf8 behaves correctly
    def test_read_utf8(self, tmp_path):
        """Verify read utf8 behavior."""
        target = tmp_path / "test.txt"
        target.write_text("日本語", encoding="utf-8")
        result = VaultManager.read_safe(target)
        assert result == "日本語"


# PURPOSE: Test suite validating vault roundtrip correctness
class TestVaultRoundtrip:
    """write_safe → read_safe ラウンドトリップテスト"""

    # PURPOSE: Verify roundtrip behaves correctly
    def test_roundtrip(self, tmp_path):
        """Verify roundtrip behavior."""
        target = tmp_path / "roundtrip.txt"
        content = "Round trip content with 日本語"
        VaultManager.write_safe(target, content)
        result = VaultManager.read_safe(target)
        assert result == content

    # PURPOSE: Verify roundtrip multiple behaves correctly
    def test_roundtrip_multiple(self, tmp_path):
        """Verify roundtrip multiple behavior."""
        for i in range(5):
            target = tmp_path / f"file_{i}.txt"
            content = f"Content {i}"
            VaultManager.write_safe(target, content)
            assert VaultManager.read_safe(target) == content
