import os
import json
import shutil
from pathlib import Path
from typing import Optional, Union, Any

class VaultManager:
    """
    Manages access to the Vault with offline caching support.
    """
    def __init__(self, vault_root: Union[str, Path], cache_root: Optional[Union[str, Path]] = None):
        self.vault_root = Path(vault_root)
        if cache_root:
            self.cache_root = Path(cache_root)
        else:
            # Default cache location: ~/.hegemonikon/cache
            self.cache_root = Path.home() / ".hegemonikon" / "cache"

        self.cache_root.mkdir(parents=True, exist_ok=True)

    @property
    def is_online(self) -> bool:
        """Check if vault is accessible."""
        return self.vault_root.exists() and self.vault_root.is_dir()

    def get_path(self, relative_path: Union[str, Path], write: bool = False) -> Path:
        """
        Get the path for a file.

        Args:
            relative_path: Path relative to vault root.
            write: If True, determines where to write (Vault if online, Cache if offline).
                   If False, searches for file (Vault if online+exists, else Cache).
        """
        rel = Path(relative_path)
        vault_path = self.vault_root / rel
        cache_path = self.cache_root / rel

        if write:
            if self.is_online:
                return vault_path
            else:
                return cache_path
        else:
            if self.is_online and vault_path.exists():
                return vault_path
            return cache_path

    def save_text(self, relative_path: Union[str, Path], content: str) -> Path:
        """Save text content to Vault or Cache."""
        target_path = self.get_path(relative_path, write=True)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)

        status = "Online" if self.is_online and target_path == (self.vault_root / relative_path) else "Offline Cache"
        print(f"[VaultManager] Saved to: {target_path} ({status})")
        return target_path

    def save_json(self, relative_path: Union[str, Path], data: Any) -> Path:
        """Save JSON content to Vault or Cache."""
        target_path = self.get_path(relative_path, write=True)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        status = "Online" if self.is_online and target_path == (self.vault_root / relative_path) else "Offline Cache"
        print(f"[VaultManager] Saved to: {target_path} ({status})")
        return target_path

    def sync(self):
        """Sync cached files to vault if online."""
        if not self.is_online:
            print("[VaultManager] Vault is offline. Cannot sync.")
            return

        print(f"[VaultManager] Syncing cache to {self.vault_root}...")

        count = 0
        # Walk through cache directory
        for root, dirs, files in os.walk(self.cache_root):
            for file in files:
                cache_file_path = Path(root) / file
                relative_path = cache_file_path.relative_to(self.cache_root)
                vault_file_path = self.vault_root / relative_path

                # Copy to vault
                vault_file_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(cache_file_path, vault_file_path)
                    print(f"  Synced: {relative_path}")

                    # Remove from cache after successful sync
                    os.remove(cache_file_path)
                    count += 1
                except Exception as e:
                    print(f"  Error syncing {relative_path}: {e}")

            # Remove empty directories
            for d in dirs:
                dir_path = Path(root) / d
                if not any(dir_path.iterdir()):
                    try:
                        dir_path.rmdir()
                    except:
                        pass

        print(f"[VaultManager] Sync complete. {count} files synced.")
