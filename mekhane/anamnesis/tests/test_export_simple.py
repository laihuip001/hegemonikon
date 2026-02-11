import pytest
import asyncio
import sys
from unittest.mock import MagicMock, AsyncMock, patch

# Mock playwright module globally because it might not be installed
mock_playwright_module = MagicMock()
sys.modules["playwright"] = mock_playwright_module
sys.modules["playwright.async_api"] = mock_playwright_module

from mekhane.anamnesis import export_simple

def test_error_handling_logs_exception(capsys):
    async def _run_test():
        # Mock playwright context manager
        mock_playwright = AsyncMock()
        mock_browser = AsyncMock()
        mock_context = MagicMock()
        mock_page = AsyncMock()

        # Setup mocks
        mock_playwright.chromium.connect_over_cdp.return_value = mock_browser
        mock_browser.contexts = [mock_context]
        mock_context.pages = [mock_page]

        # Setup page to match URL condition
        mock_page.url = "http://localhost:9222/jetski-agent"

        # Make query_selector_all raise an exception
        mock_page.query_selector_all.side_effect = Exception("Simulated Error")

        # Mock OUTPUT_DIR.mkdir to avoid filesystem errors
        with patch("mekhane.anamnesis.export_simple.OUTPUT_DIR") as mock_dir:
            # We need to mock async_playwright context manager return value
            # Since we mocked sys.modules["playwright.async_api"], we can just configure that mock.
            # export_simple.main() does: from playwright.async_api import async_playwright
            # So it gets sys.modules["playwright.async_api"].async_playwright

            mock_ap_func = sys.modules["playwright.async_api"].async_playwright
            mock_ap_func.return_value.__aenter__.return_value = mock_playwright

            await export_simple.main()

    # Run the async test
    asyncio.run(_run_test())

    # Check output
    captured = capsys.readouterr()

    # We expect "Simulated Error" to be in stdout if we fixed it.
    assert "[!] Error" in captured.out
    assert "Simulated Error" in captured.out
