# PROOF: [L2/ツール] <- mekhane/ergasterion/tekhne/ A0→ファイルベースAPIキャッシュ→Sweep高速化
# PURPOSE: LLM レスポンスのコンテンツアドレッサブルキャッシュ。
#   同一プロンプト×モデルの再呼出を回避する。
"""ResponseCache — content-addressable file cache for LLM responses.

Keyed by SHA-256(model + system_instruction + prompt).
Stored as JSON files in ~/.cache/hegemonikon/tekhne/.

Usage:
    cache = ResponseCache()

    # Check cache
    hit = cache.get(prompt="...", model="gemini-2.0-flash")
    if hit:
        return hit  # LLMResponse

    # Store
    cache.put(prompt="...", model="gemini-2.0-flash", response=resp)

    # Stats
    print(cache.stats())  # {'hits': 42, 'misses': 10, 'size_mb': 1.2}
"""

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DEFAULT_CACHE_DIR = Path.home() / ".cache" / "hegemonikon" / "tekhne"
DEFAULT_TTL = 86400 * 7  # 7 days
MAX_CACHE_SIZE_MB = 100  # Auto-evict oldest when exceeded


@dataclass
class CacheStats:
    """Cache usage statistics."""

    total_entries: int
    size_bytes: int
    hits: int
    misses: int
    oldest_age_hours: float

    @property
    def size_mb(self) -> float:
        return self.size_bytes / (1024 * 1024)

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def summary(self) -> str:
        return (
            f"Cache: {self.total_entries} entries, {self.size_mb:.1f} MB, "
            f"hit rate: {self.hit_rate:.0%} ({self.hits}/{self.hits + self.misses})"
        )


class ResponseCache:
    """Content-addressable file cache for LLM responses.

    Keys are SHA-256 hashes of (model + system_instruction + prompt).
    Values are JSON files with response text and metadata.
    """

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        ttl: int = DEFAULT_TTL,
        max_size_mb: float = MAX_CACHE_SIZE_MB,
    ):
        self.cache_dir = cache_dir or DEFAULT_CACHE_DIR
        # HGK_CACHE_TTL 環境変数で TTL を override 可能
        import os
        env_ttl = os.getenv("HGK_CACHE_TTL")
        self.ttl = int(env_ttl) if env_ttl else ttl
        self.max_size_mb = max_size_mb
        self._hits = 0
        self._misses = 0

        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def to_config_dict(self) -> dict:
        """Return current cache configuration as a dict."""
        return {
            "cache_dir": str(self.cache_dir),
            "ttl_seconds": self.ttl,
            "ttl_days": self.ttl / 86400,
            "max_size_mb": self.max_size_mb,
        }

    def _make_key(
        self,
        prompt: str,
        model: str,
        system_instruction: Optional[str] = None,
    ) -> str:
        """Generate cache key from prompt content."""
        parts = [model, system_instruction or "", prompt]
        content = "\n---\n".join(parts)
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _cache_path(self, key: str) -> Path:
        """Get file path for a cache key (2-level directory for filesystem perf)."""
        return self.cache_dir / key[:2] / f"{key}.json"

    def get(
        self,
        prompt: str,
        model: str,
        system_instruction: Optional[str] = None,
    ) -> Optional[dict]:
        """Retrieve cached response.

        Args:
            prompt: The prompt text
            model: Model name
            system_instruction: Optional system prompt

        Returns:
            dict with 'text', 'model', 'cached_at' if hit, None if miss
        """
        key = self._make_key(prompt, model, system_instruction)
        path = self._cache_path(key)

        if not path.exists():
            self._misses += 1
            return None

        try:
            data = json.loads(path.read_text(encoding="utf-8"))

            # Check TTL
            age = time.time() - data.get("cached_at", 0)
            if age > self.ttl:
                path.unlink(missing_ok=True)
                self._misses += 1
                logger.debug("Cache expired: %s (age: %.0fh)", key[:8], age / 3600)
                return None

            self._hits += 1
            logger.debug("Cache hit: %s", key[:8])
            return data

        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Cache read error for %s: %s", key[:8], e)
            path.unlink(missing_ok=True)
            self._misses += 1
            return None

    def put(
        self,
        prompt: str,
        model: str,
        response_text: str,
        system_instruction: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> str:
        """Store response in cache.

        Args:
            prompt: The prompt text
            model: Model name
            response_text: LLM response text
            system_instruction: Optional system prompt
            metadata: Optional extra metadata to store

        Returns:
            Cache key (SHA-256 hex)
        """
        key = self._make_key(prompt, model, system_instruction)
        path = self._cache_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "text": response_text,
            "model": model,
            "cached_at": time.time(),
            "prompt_hash": key,
        }
        if metadata:
            data["metadata"] = metadata

        try:
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            logger.debug("Cache stored: %s", key[:8])
        except OSError as e:
            logger.warning("Cache write error: %s", e)

        return key

    def invalidate(
        self,
        prompt: str,
        model: str,
        system_instruction: Optional[str] = None,
    ) -> bool:
        """Remove a specific cache entry.

        Returns:
            True if entry existed and was removed
        """
        key = self._make_key(prompt, model, system_instruction)
        path = self._cache_path(key)
        if path.exists():
            path.unlink()
            return True
        return False

    def clear(self) -> int:
        """Clear all cache entries.

        Returns:
            Number of entries removed
        """
        count = 0
        for f in self.cache_dir.rglob("*.json"):
            f.unlink(missing_ok=True)
            count += 1
        # Clean empty subdirectories
        for d in sorted(self.cache_dir.rglob("*"), reverse=True):
            if d.is_dir() and not any(d.iterdir()):
                d.rmdir()
        logger.info("Cache cleared: %d entries removed", count)
        return count

    def evict_oldest(self, target_mb: Optional[float] = None) -> int:
        """Evict oldest entries until under target size.

        Args:
            target_mb: Target max size in MB (default: self.max_size_mb * 0.8)

        Returns:
            Number of entries evicted
        """
        target = (target_mb or self.max_size_mb * 0.8) * 1024 * 1024

        # Collect all cache files with mtime
        entries = []
        for f in self.cache_dir.rglob("*.json"):
            try:
                stat = f.stat()
                entries.append((f, stat.st_mtime, stat.st_size))
            except OSError:
                continue

        # Sort by mtime (oldest first)
        entries.sort(key=lambda x: x[1])

        total_size = sum(e[2] for e in entries)
        evicted = 0

        while entries and total_size > target:
            path, _, size = entries.pop(0)
            try:
                path.unlink()
                total_size -= size
                evicted += 1
            except OSError:
                continue

        if evicted:
            logger.info("Evicted %d entries (%.1f MB freed)", evicted,
                       (sum(e[2] for e in entries) - total_size) / (1024 * 1024))

        return evicted

    def stats(self) -> CacheStats:
        """Get cache usage statistics."""
        entries = list(self.cache_dir.rglob("*.json"))
        total_size = 0
        oldest_mtime = time.time()

        for f in entries:
            try:
                stat = f.stat()
                total_size += stat.st_size
                oldest_mtime = min(oldest_mtime, stat.st_mtime)
            except OSError:
                continue

        oldest_age = (time.time() - oldest_mtime) / 3600 if entries else 0

        return CacheStats(
            total_entries=len(entries),
            size_bytes=total_size,
            hits=self._hits,
            misses=self._misses,
            oldest_age_hours=oldest_age,
        )
