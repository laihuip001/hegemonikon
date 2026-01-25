import pytest
import shutil
import os
import time
from pathlib import Path
from mekhane.anamnesis.vault import VaultManager

@pytest.fixture
def temp_env(tmp_path):
    vault_root = tmp_path / "vault"
    cache_root = tmp_path / "cache"
    vault_heg = vault_root / ".hegemonikon"
    cache_heg = cache_root / ".hegemonikon"

    vault_heg.mkdir(parents=True)
    cache_heg.parent.mkdir(parents=True)

    return vault_root, cache_root, vault_heg, cache_heg

def test_is_online(temp_env):
    vault_root, cache_root, vault_heg, cache_heg = temp_env

    vm = VaultManager(vault_path=vault_heg, cache_path=cache_heg)

    assert vm.is_online()

    # Simulate offline
    shutil.rmtree(vault_root)
    assert not vm.is_online()

def test_sync_down(temp_env):
    vault_root, cache_root, vault_heg, cache_heg = temp_env
    vm = VaultManager(vault_path=vault_heg, cache_path=cache_heg)

    # Create file in vault
    (vault_heg / "test.txt").write_text("hello vault", encoding='utf-8')

    # Sync down
    res = vm.sync_down()
    assert res["status"] == "success"
    assert (cache_heg / "test.txt").exists()
    assert (cache_heg / "test.txt").read_text(encoding='utf-8') == "hello vault"

def test_sync_up(temp_env):
    vault_root, cache_root, vault_heg, cache_heg = temp_env
    vm = VaultManager(vault_path=vault_heg, cache_path=cache_heg)

    # Create file in cache
    if not cache_heg.exists():
        cache_heg.mkdir(parents=True)

    (cache_heg / "local.txt").write_text("hello local", encoding='utf-8')

    # Sync up
    res = vm.sync_up()
    assert res["status"] == "success"
    assert (vault_heg / "local.txt").exists()
    assert (vault_heg / "local.txt").read_text(encoding='utf-8') == "hello local"

def test_sync_conflict_resolution(temp_env):
    vault_root, cache_root, vault_heg, cache_heg = temp_env
    vm = VaultManager(vault_path=vault_heg, cache_path=cache_heg)

    if not cache_heg.exists():
        cache_heg.mkdir(parents=True)

    # File in both, vault is newer
    file_path = "conflict.txt"
    (cache_heg / file_path).write_text("old", encoding='utf-8')

    # Set mtime to past
    old_time = time.time() - 100
    os.utime(cache_heg / file_path, (old_time, old_time))

    # Ensure vault file is newer
    (vault_heg / file_path).write_text("new", encoding='utf-8')
    os.utime(vault_heg / file_path, (time.time(), time.time()))

    vm.sync_down()
    assert (cache_heg / file_path).read_text(encoding='utf-8') == "new"

    # File in both, cache is newer
    (vault_heg / file_path).write_text("older_in_vault", encoding='utf-8')
    # Set vault mtime to past
    vault_old_time = time.time() - 200
    os.utime(vault_heg / file_path, (vault_old_time, vault_old_time))

    (cache_heg / file_path).write_text("newest_in_cache", encoding='utf-8')
    # Ensure cache is newer
    os.utime(cache_heg / file_path, (time.time(), time.time()))

    vm.sync_down() # Should NOT overwrite cache
    assert (cache_heg / file_path).read_text(encoding='utf-8') == "newest_in_cache"

    vm.sync_up() # Should overwrite vault
    assert (vault_heg / file_path).read_text(encoding='utf-8') == "newest_in_cache"

def test_offline_behavior(temp_env):
    vault_root, cache_root, vault_heg, cache_heg = temp_env

    # Make offline
    shutil.rmtree(vault_root)

    vm = VaultManager(vault_path=vault_heg, cache_path=cache_heg)
    assert not vm.is_online()

    # Sync should fail gracefully
    res = vm.sync_down()
    assert res["status"] == "offline"

    # Get path should still return cache path
    p = vm.get_path("some/file.txt")
    assert p == cache_heg / "some/file.txt"
