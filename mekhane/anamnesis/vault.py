"""
Vault Manager - Secure Access to Hegemonikón Vault
"""

import os
import shutil
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Any, Optional, List, Union

class VaultManager:
    """
    Manages access to the Obsidian Vault with backup capabilities.
    """

    def __init__(self, vault_root: Union[str, Path]):
        self.root = Path(vault_root)
        self.hegemonikon_dir = self.root / ".hegemonikon"
        self.backup_dir = self.hegemonikon_dir / "backups"
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Ensure necessary directories exist."""
        self.hegemonikon_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _create_backup(self, filepath: Path) -> Optional[Path]:
        """
        Create a backup of the given file.
        Returns the path to the backup if created, else None.
        """
        if not filepath.exists():
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{filepath.name}.{timestamp}.bak"
        backup_path = self.backup_dir / backup_name

        try:
            shutil.copy2(filepath, backup_path)
            return backup_path
        except Exception as e:
            print(f"[VaultManager] Backup failed for {filepath}: {e}")
            return None

    def write_file(self, filename: str, content: str) -> Path:
        """Write text content to a file, creating a backup first."""
        filepath = self.hegemonikon_dir / filename
        self._create_backup(filepath)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath

    def read_file(self, filename: str) -> Optional[str]:
        """Read text content from a file."""
        filepath = self.hegemonikon_dir / filename
        if not filepath.exists():
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def write_json(self, filename: str, data: Any) -> Path:
        """Write JSON data to a file, creating a backup first."""
        filepath = self.hegemonikon_dir / filename
        self._create_backup(filepath)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return filepath

    def read_json(self, filename: str) -> Any:
        """Read JSON data from a file."""
        filepath = self.hegemonikon_dir / filename
        if not filepath.exists():
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"[VaultManager] Error decoding JSON: {filename}")
            return None

    def write_yaml(self, filename: str, data: Any) -> Path:
        """Write YAML data to a file, creating a backup first."""
        filepath = self.hegemonikon_dir / filename
        self._create_backup(filepath)

        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)

        return filepath

    def read_yaml(self, filename: str) -> Any:
        """Read YAML data from a file."""
        filepath = self.hegemonikon_dir / filename
        if not filepath.exists():
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"[VaultManager] Error decoding YAML: {filename} - {e}")
            return None

    def list_backups(self, filename: str) -> List[Path]:
        """List all backups for a specific file, sorted by date (newest first)."""
        backups = []
        for p in self.backup_dir.glob(f"{filename}.*.bak"):
            backups.append(p)

        # Sort by modification time (or name which contains timestamp)
        backups.sort(key=lambda x: x.name, reverse=True)
        return backups

    def restore_backup(self, filename: str, backup_path: Optional[Path] = None) -> bool:
        """
        Restore a file from a backup.
        If backup_path is provided, restore from it.
        Otherwise, restore from the latest backup.
        """
        target_path = self.hegemonikon_dir / filename

        if backup_path is None:
            backups = self.list_backups(filename)
            if not backups:
                print(f"[VaultManager] No backups found for {filename}")
                return False
            backup_path = backups[0]

        if not backup_path.exists():
            print(f"[VaultManager] Backup file not found: {backup_path}")
            return False

        try:
            # Create a backup of the CURRENT broken state just in case, before overwriting?
            if target_path.exists():
                broken_backup = self.backup_dir / f"{filename}.broken.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
                shutil.copy2(target_path, broken_backup)

            shutil.copy2(backup_path, target_path)
            print(f"[VaultManager] Restored {filename} from {backup_path}")
            return True
        except Exception as e:
            print(f"[VaultManager] Restore failed: {e}")
            return False
