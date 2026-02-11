import sys
import unittest
from unittest.mock import MagicMock, AsyncMock, patch, mock_open
import asyncio
from pathlib import Path
import os

# Create a dummy playwright module to mock before importing inspect_messages
sys.modules["playwright"] = MagicMock()
sys.modules["playwright.async_api"] = MagicMock()

# Now import the module
# We need to make sure we can import mekhane.anamnesis
# Assuming we are at the repo root
sys.path.append(os.getcwd())

from mekhane.anamnesis import inspect_messages

class TestInspectMessagesErrorHandling(unittest.TestCase):
    async def run_main(self):
        await inspect_messages.main()

    @patch("builtins.open", new_callable=mock_open)
    def test_error_handling(self, mock_file):
        # Setup the mock for async_playwright
        mock_playwright_module = sys.modules["playwright.async_api"]
        mock_p = AsyncMock()
        mock_playwright_module.async_playwright.return_value.__aenter__.return_value = mock_p

        mock_browser = AsyncMock()
        mock_p.chromium.connect_over_cdp.return_value = mock_browser

        mock_context = MagicMock()
        mock_page = AsyncMock()
        mock_page.url = "http://localhost:9222/jetski-agent"

        mock_context.pages = [mock_page]
        mock_browser.contexts = [mock_context]

        # Mock button
        mock_button = AsyncMock()
        mock_title = AsyncMock()
        mock_title.text_content.return_value = "Test Conversation"
        mock_button.query_selector.return_value = mock_title

        # Define side effect for query_selector_all
        async def query_selector_all_side_effect(selector):
            if selector == "button.select-none":
                return [mock_button]
            if selector == "div": # For large divs
                # Return a mock div that raises exception when accessed
                mock_div = AsyncMock()
                mock_div.text_content.side_effect = Exception("Simulated Div Error")
                return [mock_div]
            if selector == "[data-testid], [data-message-id], [data-role]":
                # Return a mock element that raises exception when accessed
                mock_el = AsyncMock()
                mock_el.evaluate.side_effect = Exception("Simulated Data Element Error")
                return [mock_el]

            # For the loop over selectors, raise exception immediately
            if selector in [".overflow-y-auto", ".overflow-auto", ".overflow-y-scroll", ".prose", ".markdown", '[role="log"]', '[role="feed"]', '[class*="message"]', '[class*="thread"]', "main", "article"]:
                 raise Exception(f"Simulated Selector Error: {selector}")

            return []

        mock_page.query_selector_all.side_effect = query_selector_all_side_effect

        # Run main
        try:
            asyncio.run(self.run_main())
        except Exception as e:
            self.fail(f"Script crashed with exception: {e}")

        # Check file output
        handle = mock_file()
        written_content = ""
        for call in handle.write.call_args_list:
            written_content += call.args[0]

        print(f"Written content length: {len(written_content)}")

        # Verify if error is logged
        # Check for each simulated error
        self.assertIn("Simulated Selector Error", written_content, "Selector Error was not logged")
        self.assertIn("Simulated Div Error", written_content, "Div Error was not logged")
        self.assertIn("Simulated Data Element Error", written_content, "Data Element Error was not logged")

if __name__ == "__main__":
    unittest.main()
