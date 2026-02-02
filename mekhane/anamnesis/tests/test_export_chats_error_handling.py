import pytest
from pathlib import Path
from mekhane.anamnesis.export_chats import AntigravityChatExporter

class TestExportChatsErrorHandling:
    def test_process_raw_messages_invalid_section_idx(self, tmp_path):
        """Test that _process_raw_messages handles invalid section_idx gracefully."""
        exporter = AntigravityChatExporter(output_dir=tmp_path)

        # input with invalid section_idx
        raw_messages = [
            {
                "clean_text": "Hello",
                "raw_text": "Hello",
                "section_idx": "invalid_int"
            }
        ]

        # Should not raise exception
        processed = exporter._process_raw_messages(raw_messages)

        assert len(processed) == 1
        # Default role is assistant if heuristics don't match and index parsing fails
        assert processed[0]["role"] == "assistant"
        assert processed[0]["section_index"] == "invalid_int"

    def test_process_raw_messages_valid_section_idx(self, tmp_path):
        """Test that _process_raw_messages handles valid section_idx correctly."""
        exporter = AntigravityChatExporter(output_dir=tmp_path)

        # 0 -> user (even), 1 -> assistant (odd)
        raw_messages = [
            {
                "clean_text": "Hello",
                "raw_text": "Hello",
                "section_idx": "0"
            },
            {
                "clean_text": "Hi",
                "raw_text": "Hi",
                "section_idx": "1"
            }
        ]

        processed = exporter._process_raw_messages(raw_messages)

        assert len(processed) == 2
        assert processed[0]["role"] == "user"
        assert processed[1]["role"] == "assistant"
