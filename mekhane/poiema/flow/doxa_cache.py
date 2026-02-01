# PROOF: [L2/インフラ] O4→創造機能が必要
"""
Doxa Cache — H4 Doxa Instantiation

Philosophical Reference:
    H4 Doxa (信念): 信念の永続化、経験の蓄積

Design Principle:
    処理結果をキャッシュし、再利用可能にする
    = 経験（信念）の蓄積と記憶

Original: Flow AI v5.0 CacheManager
Recast: Hegemonikón H4 Doxa vocabulary
"""

import logging
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Callable, List

from .metron_resolver import MetronResolver, METRON_LIGHT, METRON_MEDIUM, METRON_RICH

logger = logging.getLogger("doxa_cache")


class DoxaCache:
    """
    H4 Doxa の instantiation: 信念の永続化

    Philosophical Reference:
        Doxa (δόξα) = 「信念」「意見」
        過去の処理結果を「信念」として保存し、再利用する

    Design Principle:
        - TTL: 信念の賞味期限（古くなった信念は捨てる）
        - LRU: 最も使われていない信念を優先的に削除
        - 信頼度: エラー結果は「信念」として保存しない
    """

    @staticmethod
    def get_text_hash(text: str) -> str:
        """
        テキストのハッシュを生成

        Philosophical Reference:
            テキストのアイデンティティを抽出
        """
        return hashlib.sha256(text.encode()).hexdigest()[:32]

    @staticmethod
    def sanitize_log(text: str) -> str:
        """
        ログ用にテキストをサニタイズ（プライバシー保護）

        Philosophical Reference:
            A2 Epochē との連携（判断保留状態でのログ）
        """
        if not text:
            return "[empty]"
        text_hash = DoxaCache.get_text_hash(text)[:8]
        return f"[text:{text_hash}...len={len(text)}]"

    def __init__(self, settings: Dict = None):
        """
        Initialize DoxaCache

        Args:
            settings: Configuration with CACHE_TTL_HOURS, CACHE_MAX_ENTRIES
        """
        self.settings = settings or {
            "CACHE_TTL_HOURS": 24,
            "CACHE_MAX_ENTRIES": 1000,
        }
        # In-memory cache for standalone mode
        self._memory_cache: Dict[str, Dict] = {}

    def _check_ttl(self, cache_entry: Dict) -> bool:
        """
        TTL (賞味期限) チェック

        Philosophical Reference:
            古い信念は真実でない可能性がある
            K2 Chronos との連携（時間制約）

        Returns:
            True if expired (should be removed)
        """
        created_at = cache_entry.get("created_at")
        if not created_at:
            return False

        ttl_hours = self.settings.get("CACHE_TTL_HOURS", 24)
        deadline = created_at + timedelta(hours=ttl_hours)

        if datetime.utcnow() > deadline:
            logger.info(f"🗑️ Doxa Expired: {cache_entry.get('hash_id', 'unknown')[:8]}")
            return True
        return False

    def _enforce_limit(self):
        """
        LRU (容量制限) チェック

        Philosophical Reference:
            H3 Orexis との連携（必要な信念を優先）
            使われない信念より、活きた信念を保持
        """
        max_entries = self.settings.get("CACHE_MAX_ENTRIES", 1000)

        if len(self._memory_cache) > max_entries:
            # Sort by last_accessed_at and remove oldest
            sorted_keys = sorted(
                self._memory_cache.keys(),
                key=lambda k: self._memory_cache[k].get("last_accessed_at", datetime.min),
            )
            over = len(self._memory_cache) - max_entries
            for key in sorted_keys[:over]:
                del self._memory_cache[key]
            logger.info(f"🧹 Doxa Limit Enforced: removed {over} entries")

    def check_cache(self, text: str, metron_level: int, db_session: Any = None) -> Optional[Dict]:
        """
        キャッシュ検索: 信念の想起

        Philosophical Reference:
            Anamnēsis (想起): 過去の経験を思い出す

        Args:
            text: 入力テキスト
            metron_level: 処理レベル
            db_session: Optional database session

        Returns:
            Cached result or None
        """
        text_hash = self.get_text_hash(text)
        cache_key = f"metron_{metron_level}"

        # Memory cache check
        cache_entry = self._memory_cache.get(text_hash)

        if cache_entry:
            # TTL Check
            if self._check_ttl(cache_entry):
                del self._memory_cache[text_hash]
                return None

            results = cache_entry.get("results", {})
            if cache_key in results:
                cached_result = results[cache_key]

                # Don't trust error results
                if isinstance(cached_result, str) and cached_result.startswith("Error:"):
                    return None

                # Update access time (LRU)
                cache_entry["last_accessed_at"] = datetime.utcnow()

                logger.info(f"📦 Doxa Hit: {self.sanitize_log(cached_result)}")
                return {
                    "result": cached_result,
                    "metron_level": metron_level,
                    "from_cache": True,
                    "model_used": None,
                }

        return None

    def store_cache(
        self, text: str, metron_level: int, result: str, db_session: Any = None
    ) -> None:
        """
        キャッシュ保存: 信念の永続化

        Philosophical Reference:
            H4 Doxa: 経験を信念として保存
        """
        text_hash = self.get_text_hash(text)
        cache_key = f"metron_{metron_level}"

        if text_hash not in self._memory_cache:
            self._memory_cache[text_hash] = {
                "hash_id": text_hash,
                "original_text": text,
                "results": {},
                "created_at": datetime.utcnow(),
                "last_accessed_at": datetime.utcnow(),
            }

        self._memory_cache[text_hash]["results"][cache_key] = result
        self._memory_cache[text_hash]["last_accessed_at"] = datetime.utcnow()

        # Enforce limit after storing
        self._enforce_limit()

        logger.info(f"💾 Doxa Stored: {self.sanitize_log(result)}")

    async def warmup_from_list(
        self,
        templates: List[str],
        client: Any,
        privacy: Any,
        callback: Callable = None,
        force: bool = False,
        db_session: Any = None,
    ) -> Dict:
        """
        Warmup: 事前に信念を蓄積

        Philosophical Reference:
            K2 Chronos との連携（将来に備える）

        Args:
            templates: テンプレートリスト
            client: API client
            privacy: EpocheShield instance
            callback: Progress callback
            force: Force regeneration

        Returns:
            Statistics dict
        """
        stats = {"total": len(templates), "processed": 0, "skipped": 0, "errors": 0}
        levels = [METRON_LIGHT, METRON_MEDIUM, METRON_RICH]

        for i, text in enumerate(templates):
            text = text.strip()
            if not text:
                continue

            if callback:
                callback(i + 1, len(templates), text)

            try:
                text_hash = self.get_text_hash(text)
                cache_entry = self._memory_cache.get(text_hash)

                if cache_entry and not force:
                    if len(cache_entry.get("results", {})) >= 3:
                        stats["skipped"] += 1
                        continue

                for level in levels:
                    cache_key = f"metron_{level}"
                    if cache_entry and cache_key in cache_entry.get("results", {}) and not force:
                        continue

                    # Generate via API
                    masked, mapping = privacy.mask(text)
                    system_prompt = MetronResolver.get_system_prompt(level)

                    config = {"system": system_prompt, "params": {"temperature": 0.3}}

                    res = await client.generate_content(masked, config, model=None)

                    if res.get("success"):
                        final_text = res["result"]
                        if mapping:
                            final_text = privacy.unmask(final_text, mapping)

                        self.store_cache(text, level, final_text)
                        stats["processed"] += 1

                        # Rate limit protection
                        await asyncio.sleep(1.5)
                    else:
                        stats["errors"] += 1

            except Exception as e:
                logger.error(f"Warmup failed for {self.sanitize_log(text)}: {e}")
                stats["errors"] += 1

        return stats


# Backward compatibility alias
CacheManager = DoxaCache
