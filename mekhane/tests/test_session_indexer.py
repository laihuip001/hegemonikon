# PROOF: [L2/品質] <- mekhane/tests/ A0→品質保証→セッションインデクサテスト
# PURPOSE: Test suite for mekhane/anamnesis/session_indexer.py

import sys
from pathlib import Path
import unittest

# Ensure we can import the module (repo root)
_HEGEMONIKON_ROOT = Path(__file__).parent.parent.parent
if str(_HEGEMONIKON_ROOT) not in sys.path:
    sys.path.insert(0, str(_HEGEMONIKON_ROOT))

from mekhane.anamnesis import session_indexer

class TestSessionIndexerStructure(unittest.TestCase):
    def test_typed_dicts(self):
        # Verify TypedDicts are defined
        self.assertTrue(hasattr(session_indexer, 'SessionInfo'))
        self.assertTrue(hasattr(session_indexer, 'HandoffRecord'))
        self.assertTrue(hasattr(session_indexer, 'StepInfo'))
        self.assertTrue(hasattr(session_indexer, 'ExportRecord'))
        self.assertTrue(hasattr(session_indexer, 'ConversationInfo'))

    def test_functions_exist(self):
        # Verify functions exist
        self.assertTrue(hasattr(session_indexer, 'parse_sessions_from_json'))
        self.assertTrue(hasattr(session_indexer, 'fetch_all_conversations'))
        self.assertTrue(hasattr(session_indexer, 'index_from_api'))

if __name__ == '__main__':
    unittest.main()
