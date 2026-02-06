import sys
import unittest.mock as mock
import pytest
import logging

def test_semantic_matcher_initialization_error(caplog):
    # Mock modules before import
    mock_st_module = mock.Mock()
    mock_st_class = mock.Mock()
    mock_st_module.SentenceTransformer = mock_st_class

    # Make the constructor raise an exception
    mock_st_class.side_effect = Exception("Model download failed")

    mock_numpy = mock.Mock()

    # Patch sys.modules
    with mock.patch.dict(sys.modules, {
        'sentence_transformers': mock_st_module,
        'numpy': mock_numpy
    }):
        # We must ensure mekhane.ccl.semantic_matcher is not already imported
        # so that the try/except ImportError block runs again with our mocks
        if 'mekhane.ccl.semantic_matcher' in sys.modules:
            del sys.modules['mekhane.ccl.semantic_matcher']

        from mekhane.ccl.semantic_matcher import SemanticMacroMatcher

        caplog.set_level(logging.WARNING)

        # Instantiate
        # This should trigger the exception inside __init__
        matcher = SemanticMacroMatcher()

        # Check that model is None (graceful degradation)
        assert matcher.model is None

        # This assertion checks if the error was logged
        # Expected to fail before the fix
        assert "Failed to initialize SentenceTransformer" in caplog.text
        assert "Model download failed" in caplog.text
