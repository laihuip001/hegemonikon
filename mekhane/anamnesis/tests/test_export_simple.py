# PROOF: [L3/Test]
import asyncio
import sys
import unittest.mock
from unittest.mock import AsyncMock, patch
import pytest

# We mock playwright first to avoid ImportError if not installed
sys.modules["playwright"] = unittest.mock.MagicMock()
sys.modules["playwright.async_api"] = unittest.mock.MagicMock()

# Now import the module under test
from mekhane.anamnesis import export_simple

async def run_test(capsys):
    # Setup mocks
    # We need to mock what async_playwright context manager returns
    mock_playwright_instance = AsyncMock()
    mock_browser = AsyncMock()

    # Configure browser contexts and pages
    mock_context = AsyncMock()

    # Page 1: Fails query_selector_all
    mock_page_fail = AsyncMock()
    mock_page_fail.url = "http://jetski-agent/fail"
    mock_page_fail.query_selector_all.side_effect = Exception("Simulated failure")

    # Page 2: Succeeds query_selector_all
    mock_page_success = AsyncMock()
    mock_page_success.url = "http://jetski-agent/success"
    mock_button = AsyncMock()
    mock_button.query_selector.return_value = AsyncMock()
    mock_button.query_selector.return_value.text_content.return_value = "Test Conversation"

    # We need query_selector on the button to simulate title extraction later in the script
    mock_page_success.query_selector_all.return_value = [mock_button]

    # Set context pages
    mock_context.pages = [mock_page_fail, mock_page_success]
    mock_browser.contexts = [mock_context]

    # Connect mock browser to playwright instance
    mock_playwright_instance.chromium.connect_over_cdp.return_value = mock_browser

    # Now patch where it is used. Since we mocked the module 'playwright.async_api',
    # we need to configure the mock object in sys.modules.
    mock_module = sys.modules["playwright.async_api"]
    mock_module.async_playwright.return_value.__aenter__.return_value = mock_playwright_instance

    # Run main
    # We might need to mock open() calls because the script tries to save files.
    with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
        await export_simple.main()

    # Capture output
    captured = capsys.readouterr()

    # Verify behavior
    # Page 2 should be processed and "Found jetski-agent page" printed
    assert "[*] Found jetski-agent page: 1 buttons" in captured.out

    # Page 1 failure should now be logged
    assert "Error checking page" in captured.out

def test_export_simple_error_handling(capsys):
    asyncio.run(run_test(capsys))
