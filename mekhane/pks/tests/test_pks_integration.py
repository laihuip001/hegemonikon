"""PKS Integration Test — 全モジュールの import + 機能テスト"""

import sys
sys.path.insert(0, ".")

print("=== PKS Import Test ===")

# 1. pks_engine
from mekhane.pks.pks_engine import (
    PKSEngine, RelevanceDetector, PushController, ContextTracker,
    KnowledgeNugget, SessionContext
)
print("[OK] pks_engine")

# 2. narrator
from mekhane.pks.narrator import PKSNarrator, Narrative, NarrativeSegment
print("[OK] narrator")

# 3. matrix_view
from mekhane.pks.matrix_view import PKSMatrixView
print("[OK] matrix_view")

# 4. link_engine
from mekhane.pks.links.link_engine import LinkEngine, Link, LinkIndex, WIKILINK_PATTERN
print("[OK] link_engine")

# 5. citation_graph
from mekhane.pks.links.citation_graph import CitationGraph, Citation, CitationType
print("[OK] citation_graph")

# 6. sync_watcher
from mekhane.pks.sync_watcher import SyncWatcher, FileChange
print("[OK] sync_watcher")

print("\n=== Functional Tests ===")

# Test KnowledgeNugget
nugget = KnowledgeNugget(
    title="Test FEP Paper", abstract="Active inference...",
    source="arxiv", relevance_score=0.85,
    push_reason="FEP topic"
)
assert "Test FEP Paper" in nugget.to_markdown()
print("[OK] KnowledgeNugget.to_markdown()")

# Test Narrator
narrator = PKSNarrator()
narrative = narrator.narrate(nugget)
assert len(narrative.segments) == 3
assert narrative.segments[0].speaker == "Advocate"
print("[OK] PKSNarrator.narrate()")

# Test MatrixView
matrix = PKSMatrixView()
table = matrix.generate([nugget])
assert "Test FEP" in table
print("[OK] PKSMatrixView.generate()")

# Test RelevanceDetector
detector = RelevanceDetector(threshold=0.5)
fake_results = [
    {"title": "FEP", "abstract": "AI", "source": "arxiv", "_distance": 0.3, "url": "#", "authors": "A"},
    {"title": "Other", "abstract": "Cook", "source": "x", "_distance": 1.8, "url": "#", "authors": "B"},
]
ctx = SessionContext(topics=["FEP"])
nuggets_list = detector.score(ctx, fake_results)
assert len(nuggets_list) >= 1
print(f"[OK] RelevanceDetector: {len(nuggets_list)} nuggets scored")

# Test WIKILINK regex
matches = WIKILINK_PATTERN.findall("[[target]] and [[a|b]]")
assert len(matches) == 2
print("[OK] WIKILINK_PATTERN")

# Test LinkEngine
from pathlib import Path
engine = LinkEngine(Path(".agent/workflows"))
idx = engine.build_index()
print(f"[OK] LinkEngine: {idx.total_files} files, {idx.total_links} links")

# Test CitationGraph
graph = CitationGraph()
graph.add_citation(Citation("a", "b", CitationType.SUPPORTS))
assert graph.get_stats("b").supporting_count == 1
print("[OK] CitationGraph")

# Test SyncWatcher
watcher = SyncWatcher(
    watch_dirs=[Path("mekhane/pks")],
    state_dir=Path("/tmp/pks_test")
)
changes = watcher.detect_changes()
print(f"[OK] SyncWatcher: {len(changes)} changes")

print("\n=== ALL TESTS PASSED ===")
