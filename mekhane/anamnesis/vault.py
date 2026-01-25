import os
import shutil
import json
import yaml
import logging
from pathlib import Path
from typing import Any, Union, Optional

logger = logging.getLogger(__name__)

class VaultManager:
    """
    Manager for Vault operations with backup and recovery mechanisms.
    Handles atomic writes and backup creation to prevent data loss.
    """

    def __init__(self, vault_root: Union[str, Path]):
        self.vault_root = Path(vault_root)

    def _resolve_path(self, rel_path: Union[str, Path]) -> Path:
        """Resolves relative path to absolute path within vault root."""
        return self.vault_root / rel_path

    def _backup_file(self, path: Path):
        """Creates a backup of the file by appending .bak extension."""
        if path.exists():
            backup_path = path.with_suffix(path.suffix + ".bak")
            try:
                shutil.copy2(path, backup_path)
                logger.info(f"Backup created: {backup_path}")
            except Exception as e:
                logger.error(f"Failed to create backup for {path}: {e}")
                # Log warning but proceed, as we prioritize the write operation
                pass

    def _write_atomic(self, path: Path, content: str, encoding: str = 'utf-8'):
        """Writes content to a temporary file and renames it to the target path."""
        temp_path = path.with_suffix(path.suffix + ".tmp")
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(temp_path, 'w', encoding=encoding) as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())

            # Atomic replace
            os.replace(temp_path, path)
        except Exception as e:
            logger.error(f"Failed to write atomic file {path}: {e}")
            if temp_path.exists():
                try:
                    os.remove(temp_path)
                except:
                    pass
            raise e

    def write_file(self, rel_path: Union[str, Path], content: str, backup: bool = True):
        """
        Writes text content to a file in the Vault.

        Args:
            rel_path: Relative path from vault root.
            content: Content to write.
            backup: Whether to create a backup of the existing file.
        """
        path = self._resolve_path(rel_path)

        if backup and path.exists():
            self._backup_file(path)

        self._write_atomic(path, content)

    def read_file(self, rel_path: Union[str, Path], backup_fallback: bool = True) -> str:
        """
        Reads text content from a file in the Vault.

        Args:
            rel_path: Relative path from vault root.
            backup_fallback: Whether to try reading the backup file if the main file fails.

        Returns:
            File content as string.

        Raises:
            FileNotFoundError: If neither file nor backup exists.
            IOError: If reading fails.
        """
        path = self._resolve_path(rel_path)

        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except (FileNotFoundError, IOError, UnicodeDecodeError) as e:
            if not backup_fallback:
                raise e

            backup_path = path.with_suffix(path.suffix + ".bak")
            if not backup_path.exists():
                raise e

            logger.warning(f"Failed to read {path}, falling back to backup {backup_path}: {e}")
            try:
                with open(backup_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as backup_error:
                logger.error(f"Failed to read backup {backup_path}: {backup_error}")
                raise e

    def write_json(self, rel_path: Union[str, Path], data: Any, backup: bool = True, indent: int = 2):
        """Writes data as JSON."""
        content = json.dumps(data, ensure_ascii=False, indent=indent)
        self.write_file(rel_path, content, backup=backup)

    def read_json(self, rel_path: Union[str, Path], backup_fallback: bool = True) -> Any:
        """Reads JSON data."""
        try:
            content = self.read_file(rel_path, backup_fallback=False)
            return json.loads(content)
        except (FileNotFoundError, IOError, UnicodeDecodeError, json.JSONDecodeError) as e:
            if not backup_fallback:
                raise e

            path = self._resolve_path(rel_path)
            backup_path = path.with_suffix(path.suffix + ".bak")

            if not backup_path.exists():
                raise e

            logger.warning(f"Error accessing/parsing {path}, falling back to backup: {e}")
            try:
                with open(backup_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                raise e

    def write_yaml(self, rel_path: Union[str, Path], data: Any, backup: bool = True):
        """Writes data as YAML."""
        content = yaml.dump(data, allow_unicode=True, default_flow_style=False)
        self.write_file(rel_path, content, backup=backup)

    def read_yaml(self, rel_path: Union[str, Path], backup_fallback: bool = True) -> Any:
        """Reads YAML data."""
        try:
            content = self.read_file(rel_path, backup_fallback=False)
            return yaml.safe_load(content)
        except (FileNotFoundError, IOError, UnicodeDecodeError, yaml.YAMLError) as e:
            if not backup_fallback:
                raise e

            path = self._resolve_path(rel_path)
            backup_path = path.with_suffix(path.suffix + ".bak")

            if not backup_path.exists():
                raise e

            logger.warning(f"Error accessing/parsing {path}, falling back to backup: {e}")
            try:
                with open(backup_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception:
                raise e
