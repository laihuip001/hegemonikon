import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
from mekhane.anamnesis.vault import VaultManager

class TestVaultManagerCleanup(unittest.TestCase):

    @patch('mekhane.anamnesis.vault.logger')
    @patch('mekhane.anamnesis.vault.Path')
    @patch('mekhane.anamnesis.vault.tempfile.NamedTemporaryFile')
    def test_write_safe_cleanup_failure_logging(self, mock_named_temp_file, mock_path_cls, mock_logger):
        """
        Test that a warning is logged when temporary file cleanup fails
        during error recovery in write_safe.
        """
        # Setup mocks
        # 1. Mock NamedTemporaryFile context manager
        mock_temp_file = MagicMock()
        mock_temp_file.name = "/tmp/test_tmp_file"
        mock_named_temp_file.return_value.__enter__.return_value = mock_temp_file

        # 2. Mock Path instances
        # We need to handle multiple Path instantiations:
        # - Path(filepath) -> target_path
        # - Path(tmp_file.name) -> tmp_path

        mock_target_path = MagicMock()
        mock_target_path.exists.return_value = False # No backup needed

        mock_tmp_path = MagicMock()
        mock_tmp_path.exists.return_value = True # File exists to be cleaned up

        # Make tmp_path.replace raise the primary exception (triggering the except block)
        mock_tmp_path.replace.side_effect = IOError("Primary write error")

        # Make tmp_path.unlink raise the secondary exception (triggering the nested except block)
        mock_tmp_path.unlink.side_effect = PermissionError("Cleanup permission denied")

        # Configure Path constructor to return correct mocks
        def path_side_effect(arg):
            if arg == "/tmp/test_tmp_file":
                return mock_tmp_path
            return mock_target_path

        mock_path_cls.side_effect = path_side_effect

        # Execute
        with self.assertRaises(IOError) as cm:
            VaultManager.write_safe("some/file.txt", "content")

        # Verify primary exception is preserved
        self.assertIn("Primary write error", str(cm.exception))

        # Verify cleanup attempted
        mock_tmp_path.unlink.assert_called_once()

        # Verify warning logged for cleanup failure
        # checking specifically for warning level log
        mock_logger.warning.assert_called()

        # Optionally check message content
        args, _ = mock_logger.warning.call_args
        self.assertIn("cleanup", args[0].lower())

if __name__ == '__main__':
    unittest.main()
