"""
Gnōsis Memory Manager - Local Cache for Offline Vault Access
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union

# Optional YAML support
try:
    import yaml
except ImportError:
    yaml = None

# Default Configuration
DEFAULT_VAULT_ROOT = Path("M:/Brain")
CACHE_DIR = Path(__file__).parent.parent.parent / "gnosis_data" / "cache"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Manages access to long-term memory files (Vault) with local caching.
    Ensures the agent can function even when the Vault (network drive) is inaccessible.
    """

    def __init__(self, vault_root: Optional[Union[str, Path]] = None, cache_dir: Optional[Union[str, Path]] = None):
        # Resolve Vault Path
        if vault_root:
            self.vault_root = Path(vault_root)
        else:
            env_path = os.getenv("HEGEMONIKON_VAULT_PATH")
            self.vault_root = Path(env_path) if env_path else DEFAULT_VAULT_ROOT

        self.hegemonikon_dir = self.vault_root / ".hegemonikon"

        # Resolve Cache Path
        self.cache_dir = Path(cache_dir) if cache_dir else CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def is_vault_accessible(self) -> bool:
        """Check if the Vault directory exists and is accessible."""
        return self.hegemonikon_dir.exists()

    def _get_paths(self, filename: str):
        vault_path = self.hegemonikon_dir / filename
        cache_path = self.cache_dir / filename
        return vault_path, cache_path

    def load(self, filename: str, force_reload: bool = False) -> Any:
        """
        Load a file from Vault or Cache.

        Args:
            filename: Name of the file (e.g., 'patterns.yaml')
            force_reload: If True, ignore cache and try to read from Vault.

        Returns:
            Parsed content (if JSON/YAML) or string content. Returns None if not found.
        """
        vault_path, cache_path = self._get_paths(filename)
        content = None
        loaded_from = None

        # Try loading from Vault
        if self.is_vault_accessible() or force_reload:
            if vault_path.exists():
                try:
                    logger.info(f"Loading {filename} from Vault: {vault_path}")
                    content = vault_path.read_text(encoding='utf-8')
                    # Update cache
                    try:
                        cache_path.write_text(content, encoding='utf-8')
                        logger.debug(f"Updated cache for {filename}")
                    except Exception as e:
                        logger.warning(f"Failed to update cache for {filename}: {e}")
                    loaded_from = "vault"
                except Exception as e:
                    logger.warning(f"Failed to read from Vault {vault_path}: {e}")

        # Try loading from Cache if Vault failed or was skipped
        if content is None and cache_path.exists():
            try:
                logger.info(f"Loading {filename} from Cache: {cache_path}")
                content = cache_path.read_text(encoding='utf-8')
                loaded_from = "cache"
            except Exception as e:
                logger.error(f"Failed to read from Cache {cache_path}: {e}")

        if content is None:
            logger.warning(f"Could not load {filename} from Vault or Cache.")
            return None

        return self._parse(filename, content)

    def save(self, filename: str, data: Any) -> bool:
        """
        Save data to Cache and try to sync to Vault.

        Args:
            filename: Name of the file.
            data: Data to save (dict, list, or string).

        Returns:
            True if saved to at least Cache, False otherwise.
        """
        vault_path, cache_path = self._get_paths(filename)
        content = self._serialize(filename, data)
        success = False

        # Save to Cache
        try:
            cache_path.write_text(content, encoding='utf-8')
            logger.info(f"Saved {filename} to Cache")
            success = True
        except Exception as e:
            logger.error(f"Failed to write to Cache {cache_path}: {e}")

        # Save to Vault
        if self.is_vault_accessible():
             try:
                vault_path.write_text(content, encoding='utf-8')
                logger.info(f"Synced {filename} to Vault")
             except Exception as e:
                 logger.warning(f"Failed to write to Vault {vault_path}: {e}")
        else:
             logger.warning(f"Vault not accessible. {filename} saved to Cache only.")

        return success

    def sync_all(self, filenames: list[str] = None):
        """Sync specific files from Vault to Cache."""
        if filenames is None:
            filenames = ["patterns.yaml", "values.json", "trust_history.json"]

        results = {}
        for fname in filenames:
            data = self.load(fname, force_reload=True)
            results[fname] = "synced" if data is not None else "failed"
        return results

    def _parse(self, filename: str, content: str) -> Any:
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            if yaml:
                try:
                    return yaml.safe_load(content)
                except Exception as e:
                    logger.error(f"YAML parse error: {e}")
                    return content # Fallback to string
            else:
                return content # Fallback to string if no yaml lib
        elif filename.endswith('.json'):
            try:
                return json.loads(content)
            except Exception as e:
                logger.error(f"JSON parse error: {e}")
                return content
        return content

    def _serialize(self, filename: str, data: Any) -> str:
        if isinstance(data, str):
            return data

        if filename.endswith('.yaml') or filename.endswith('.yml'):
            if yaml:
                return yaml.dump(data, allow_unicode=True)
            else:
                return str(data) # Fallback
        elif filename.endswith('.json'):
            return json.dumps(data, indent=2, ensure_ascii=False)

        return str(data)
