import os
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Union, Optional

logger = logging.getLogger(__name__)

class VaultManager:
    """
    Manages access to the Vault (External Storage) and Local Cache.
    Handles offline scenarios by falling back to local cache and syncing when possible.
    """

    DEFAULT_VAULT_PATH = Path(r"M:\Brain\.hegemonikon")
    # Default cache path relative to this file: mekhane/anamnesis/cache/.hegemonikon
    DEFAULT_CACHE_PATH = Path(__file__).parent / "cache" / ".hegemonikon"

    def __init__(self, vault_path: Optional[Union[str, Path]] = None, cache_path: Optional[Union[str, Path]] = None):
        self.vault_path = Path(vault_path) if vault_path else self.DEFAULT_VAULT_PATH
        self.cache_path = Path(cache_path) if cache_path else self.DEFAULT_CACHE_PATH

        # Ensure cache parent directory exists
        if not self.cache_path.parent.exists():
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)

    def is_online(self) -> bool:
        """Check if Vault is accessible."""
        return self.vault_path.exists() and self.vault_path.is_dir()

    def get_path(self, rel_path: str) -> Path:
        """
        Get the path to a file or directory.
        Returns the cache path.
        Use ensure_sync() to make sure cache is up to date.
        """
        return self.cache_path / rel_path

    def sync_down(self) -> Dict[str, Union[str, List[str]]]:
        """
        Sync from Vault to Cache.
        """
        if not self.is_online():
            return {"status": "offline", "synced": []}

        synced_files = []

        try:
            # If cache doesn't exist at all, copy everything
            if not self.cache_path.exists():
                shutil.copytree(self.vault_path, self.cache_path)
                return {"status": "success", "message": "Full clone", "synced": ["ALL"]}

            # Walk vault
            for root, dirs, files in os.walk(self.vault_path):
                rel_root = Path(root).relative_to(self.vault_path)
                target_root = self.cache_path / rel_root

                if not target_root.exists():
                    target_root.mkdir(parents=True, exist_ok=True)

                for file in files:
                    vault_file = Path(root) / file
                    cache_file = target_root / file

                    should_copy = False
                    if not cache_file.exists():
                        should_copy = True
                    else:
                        # If vault file is newer than cache file
                        vault_mtime = vault_file.stat().st_mtime
                        cache_mtime = cache_file.stat().st_mtime
                        if vault_mtime > cache_mtime:
                            should_copy = True

                    if should_copy:
                        shutil.copy2(vault_file, cache_file)
                        synced_files.append(str(rel_root / file))

            return {"status": "success", "synced": synced_files}

        except Exception as e:
            logger.error(f"Sync down failed: {e}")
            return {"status": "error", "message": str(e)}

    def sync_up(self) -> Dict[str, Union[str, List[str]]]:
        """
        Sync from Cache to Vault.
        """
        if not self.is_online():
            return {"status": "offline", "synced": []}

        synced_files = []

        try:
            if not self.cache_path.exists():
                 return {"status": "empty_cache", "synced": []}

            # Walk cache
            for root, dirs, files in os.walk(self.cache_path):
                rel_root = Path(root).relative_to(self.cache_path)
                target_root = self.vault_path / rel_root

                if not target_root.exists():
                    target_root.mkdir(parents=True, exist_ok=True)

                for file in files:
                    cache_file = Path(root) / file
                    vault_file = target_root / file

                    should_copy = False
                    if not vault_file.exists():
                        should_copy = True
                    else:
                        # If cache file is newer than vault file
                        cache_mtime = cache_file.stat().st_mtime
                        vault_mtime = vault_file.stat().st_mtime
                        if cache_mtime > vault_mtime:
                            should_copy = True

                    if should_copy:
                        shutil.copy2(cache_file, vault_file)
                        synced_files.append(str(rel_root / file))

            return {"status": "success", "synced": synced_files}

        except Exception as e:
            logger.error(f"Sync up failed: {e}")
            return {"status": "error", "message": str(e)}

    def ensure_sync(self):
        """Try to sync both ways (Down then Up)."""
        if self.is_online():
            self.sync_down()
            self.sync_up()
