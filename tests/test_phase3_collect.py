import sys
import os
import asyncio
import importlib.util
import tempfile
import shutil
import pytest
from unittest.mock import MagicMock, patch

# Import the script module
spec = importlib.util.spec_from_file_location("phase3_collect", "mekhane/peira/scripts/phase3-fast-collect.py")
phase3_collect = importlib.util.module_from_spec(spec)
sys.modules["phase3_collect"] = phase3_collect
spec.loader.exec_module(phase3_collect)

@pytest.fixture
def temp_root():
    temp_dir = tempfile.mkdtemp()
    original_root = phase3_collect.ROOT_DIR
    phase3_collect.ROOT_DIR = temp_dir

    # Create necessary subdirs
    os.makedirs(os.path.join(temp_dir, "_index"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "2023", "01"), exist_ok=True)

    yield temp_dir

    phase3_collect.ROOT_DIR = original_root
    shutil.rmtree(temp_dir)

@pytest.mark.asyncio
async def test_process_urls_async_success(temp_root):
    # Mock dependencies
    with patch("phase3_collect.fetch_html_async") as mock_fetch, \
         patch("phase3_collect.parse_article_content") as mock_parse, \
         patch("phase3_collect.save_markdown_file") as mock_save:

        # Configure side_effect or return_value based on url if needed
        # Here simple return value
        mock_fetch.return_value = {"status": "success", "content": "<html></html>", "url": "http://example.com/1"}
        mock_parse.return_value = {
            "status": "success",
            "url": "http://example.com/1",
            "title": "Test Title",
            "markdown": "content",
            "year": "2023", "month": "01"
        }
        mock_save.return_value = os.path.join(temp_root, "2023", "01", "1.md")

        target_urls = ["http://example.com/1", "http://example.com/2"]
        batch_id = "test"

        # Run
        await phase3_collect.process_urls_async(target_urls, batch_id)

        # Verify manifest
        manifest_path = os.path.join(temp_root, "_index", f"manifest_fast_{batch_id}.jsonl")
        assert os.path.exists(manifest_path)
        with open(manifest_path, "r") as f:
            lines = f.readlines()
            # Since fetch returns same obj for both, we expect 2 lines
            assert len(lines) == 2
            data = phase3_collect.json.loads(lines[0])
            assert data["url"] == "http://example.com/1"
            assert data["batch_id"] == "test"

@pytest.mark.asyncio
async def test_process_urls_async_failure(temp_root):
    # Mock dependencies
    with patch("phase3_collect.fetch_html_async") as mock_fetch:

        mock_fetch.return_value = {"status": "error", "url": "http://example.com/bad", "error": "404"}

        target_urls = ["http://example.com/bad"]
        batch_id = "test_fail"

        # Run
        await phase3_collect.process_urls_async(target_urls, batch_id)

        # Verify skip log
        skip_path = os.path.join(temp_root, "_index", f"skipped_fast_{batch_id}.txt")
        assert os.path.exists(skip_path)
        with open(skip_path, "r") as f:
            content = f.read()
            assert "http://example.com/bad" in content
            assert "404" in content
