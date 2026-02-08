# noqa: AI-ALL
# PROOF: [L3/テスト] <- mekhane/tests_root/ 対象モジュールが存在→検証が必要
import os
import shutil
import tempfile
from pathlib import Path
import pytest
from mekhane.anamnesis.vault import VaultManager


# PURPOSE: dir をテストする
@pytest.fixture
def test_dir():  # noqa: AI-ALL
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


# PURPOSE: Test writing a new file
def test_write_new_file(test_dir):
    """Test writing a new file."""
    file_path = test_dir / "test.txt"
    content = "Hello, World!"

    VaultManager.write_safe(file_path, content)

    assert file_path.exists()
    assert file_path.read_text(encoding="utf-8") == content


# PURPOSE: Test overwriting an existing file creates a backup
def test_write_overwrite_backup(test_dir):
    """Test overwriting an existing file creates a backup."""
    file_path = test_dir / "test.txt"
    content1 = "Initial content"
    content2 = "New content"

    VaultManager.write_safe(file_path, content1)
    assert file_path.read_text(encoding="utf-8") == content1

    VaultManager.write_safe(file_path, content2)
    assert file_path.read_text(encoding="utf-8") == content2

    backup_path = file_path.with_suffix(".txt.bak")
    assert backup_path.exists()
    assert backup_path.read_text(encoding="utf-8") == content1


# PURPOSE: Test reading a file safely
def test_read_safe(test_dir):
    """Test reading a file safely."""
    file_path = test_dir / "read_test.txt"
    content = "Read me"

    VaultManager.write_safe(file_path, content)
    read_content = VaultManager.read_safe(file_path)

    assert read_content == content


# PURPOSE: Test reading from backup when main file is missing
def test_read_backup_when_main_missing(test_dir):
    """Test reading from backup when main file is missing."""
    file_path = test_dir / "missing.txt"
    backup_path = file_path.with_suffix(".txt.bak")
    content = "Backup content"

    # Write initial content
    VaultManager.write_safe(file_path, content)

    # Manually create backup and delete original to simulate corruption/loss
    # Note: write_safe creates backup on overwrite, but here we want to simulate
    # a state where backup exists and main is gone.
    shutil.copy2(file_path, backup_path)
    file_path.unlink()

    assert not file_path.exists()
    assert backup_path.exists()

    # Should read from backup
    read_content = VaultManager.read_safe(file_path)
    assert read_content == content


# PURPOSE: Test reading a non-existent file fails
def test_read_fail_no_file(test_dir):
    """Test reading a non-existent file fails."""
    file_path = test_dir / "non_existent.txt"

    with pytest.raises(FileNotFoundError):
        VaultManager.read_safe(file_path)
