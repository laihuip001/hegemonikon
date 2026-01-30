"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

P3 → 記憶の永続化が必要
   → 安全な書き込み操作が必要
   → vault.py が担う

Q.E.D.

---

Vault Manager - Secure File Operations
======================================

Provides atomic write operations and backup mechanisms for Vault files.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Union, Optional
import logging

logger = logging.getLogger(__name__)

class VaultManager:
    """Manages secure file operations for the Vault."""

    @staticmethod
    def write_safe(
        filepath: Union[str, Path],
        content: str,
        encoding: str = "utf-8",
        backup: bool = True
    ) -> Path:
        """
        Writes content to a file safely with backup and atomic constraints.

        Args:
            filepath: Target file path.
            content: Content to write.
            encoding: File encoding (default: utf-8).
            backup: Whether to create a backup if file exists.

        Returns:
            Path: The path of the written file.

        Raises:
            IOError: If write fails.
        """
        target_path = Path(filepath)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # 1. Create Backup if exists
        if backup and target_path.exists():
            backup_path = target_path.with_suffix(target_path.suffix + ".bak")
            try:
                shutil.copy2(target_path, backup_path)
                logger.info(f"Backup created: {backup_path}")
            except Exception as e:
                logger.error(f"Failed to create backup: {e}")
                raise IOError(f"Failed to create backup for {target_path}: {e}")

        # 2. Write to Temp File
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode='w',
                dir=target_path.parent,
                delete=False,
                encoding=encoding
            ) as tmp_file:
                tmp_file.write(content)
                tmp_path = Path(tmp_file.name)

            # 3. Atomic Move
            tmp_path.replace(target_path)
            logger.info(f"Successfully wrote to {target_path}")
            return target_path

        except Exception as e:
            logger.error(f"Write failed for {target_path}: {e}")
            if tmp_path and tmp_path.exists():
                try:
                    tmp_path.unlink()
                except Exception:
                    pass
            raise IOError(f"Failed to write file safely: {e}")

    @staticmethod
    def read_safe(
        filepath: Union[str, Path],
        encoding: str = "utf-8"
    ) -> str:
        """
        Reads content from a file safely.
        If reading the primary file fails, attempts to read from the backup (.bak).

        Args:
            filepath: Target file path.
            encoding: File encoding.

        Returns:
            str: File content.

        Raises:
            FileNotFoundError: If neither file nor backup exists.
            IOError: If reading fails.
        """
        target_path = Path(filepath)
        backup_path = target_path.with_suffix(target_path.suffix + ".bak")

        # Attempt 1: Read original
        if target_path.exists():
            try:
                with open(target_path, 'r', encoding=encoding) as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Failed to read {target_path}: {e}")
                if not backup_path.exists():
                    raise IOError(f"Failed to read {target_path} and no backup found: {e}")
                # Fallthrough to backup
        elif not backup_path.exists():
             raise FileNotFoundError(f"File not found: {target_path}")

        # Attempt 2: Read backup
        if backup_path.exists():
            logger.warning(f"Attempting to read from backup: {backup_path}")
            try:
                with open(backup_path, 'r', encoding=encoding) as f:
                    return f.read()
            except Exception as e:
                raise IOError(f"Failed to read backup {backup_path}: {e}")

        raise IOError(f"Unknown error reading {target_path}")
