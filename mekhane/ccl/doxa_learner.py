# PROOF: [L1/定理] CCL→CCLパーサーが必要→doxa_learner が担う
"""
Doxa Learner for CCL v2.0

Layer 2 of the 4-layer fallback system.
H4 Doxa integrated pattern learning - persists Creator's intent patterns.
"""

from dataclasses import dataclass, asdict
from typing import Optional, List
from pathlib import Path
import json


@dataclass
class LearnedPattern:
    """A learned intent-to-CCL mapping."""
    intent: str
    ccl: str
    confidence: float
    usage_count: int


class DoxaLearner:
    """
    H4 Doxa connected pattern learner (Layer 2).
    
    Persists successful intent-to-CCL conversions and retrieves them
    for future similar intents. Learning improves over time.
    """
    
    STORE_PATH = Path("/home/laihuip001/oikos/mneme/.hegemonikon/ccl_patterns.json")
    
    def __init__(self, store_path: Optional[Path] = None):
        """
        Initialize the learner.
        
        Args:
            store_path: Override default storage path
        """
        if store_path:
            self.store_path = store_path
        else:
            self.store_path = self.STORE_PATH
        self.patterns: List[LearnedPattern] = self._load()
    
    def _load(self) -> List[LearnedPattern]:
        """Load patterns from disk."""
        if self.store_path.exists():
            try:
                data = json.loads(self.store_path.read_text())
                return [LearnedPattern(**p) for p in data]
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    def _save(self):
        """Persist patterns to disk."""
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        data = [asdict(p) for p in self.patterns]
        self.store_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    
    def record(self, intent: str, ccl: str, confidence: float = 0.8):
        """
        Record a successful intent-to-CCL conversion.
        
        Args:
            intent: The natural language intent
            ccl: The CCL expression that was generated
            confidence: Initial confidence (0.0-1.0)
        """
        # Check for existing pattern
        existing = next((p for p in self.patterns if p.intent == intent), None)
        
        if existing:
            # Reinforce existing pattern
            existing.usage_count += 1
            existing.confidence = min(1.0, existing.confidence + 0.05)
            # Update CCL if different (latest wins)
            if existing.ccl != ccl:
                existing.ccl = ccl
        else:
            # Add new pattern
            self.patterns.append(LearnedPattern(
                intent=intent,
                ccl=ccl,
                confidence=confidence,
                usage_count=1
            ))
        
        self._save()
    
    def lookup(self, intent: str) -> Optional[str]:
        """
        Look up a similar pattern.
        
        Args:
            intent: The natural language intent to match
            
        Returns:
            CCL expression if found, None otherwise
        """
        # Simple substring matching (future: embedding similarity)
        for p in sorted(self.patterns, key=lambda x: -x.confidence):
            # Exact match
            if p.intent == intent:
                return p.ccl
            # Substring match (bidirectional)
            if len(p.intent) > 5 and len(intent) > 5:
                if p.intent in intent or intent in p.intent:
                    return p.ccl
        
        return None
    
    def get_stats(self) -> dict:
        """Get statistics about learned patterns."""
        if not self.patterns:
            return {"count": 0, "avg_confidence": 0.0, "total_usage": 0}
        
        return {
            "count": len(self.patterns),
            "avg_confidence": sum(p.confidence for p in self.patterns) / len(self.patterns),
            "total_usage": sum(p.usage_count for p in self.patterns),
        }
