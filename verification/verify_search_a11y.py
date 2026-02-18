from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            print("Navigating to http://localhost:1420...")
            page.goto("http://localhost:1420")

            # Wait for sidebar/navigation
            print("Waiting for Search button...")
            search_btn = page.locator("button", has_text="Search")
            expect(search_btn).to_be_visible(timeout=10000)

            # Click Search button
            print("Clicking Search button...")
            search_btn.click()

            # Wait for search view to load
            print("Waiting for search input...")
            search_input = page.locator("#symploke-search-input")
            expect(search_input).to_be_visible(timeout=5000)

            # 1. Verify aria-label on input
            label = search_input.get_attribute("aria-label")
            print(f"Input aria-label: {label}")
            if label != "検索キーワード":
                raise AssertionError(f"Expected '検索キーワード', but got '{label}'")

            # 2. Verify aria-pressed on filter chips
            print("Checking filter chips...")
            filter_chip = page.locator(".search-source-chip").first
            expect(filter_chip).to_be_visible()

            initial_pressed = filter_chip.get_attribute("aria-pressed")
            print(f"Initial chip aria-pressed: {initial_pressed}")
            if initial_pressed not in ["true", "false"]:
                raise AssertionError(f"Expected 'true' or 'false', but got '{initial_pressed}'")

            # 3. Toggle filter chip
            print("Toggling filter chip...")
            filter_chip.click()

            # Verify state change
            new_pressed = filter_chip.get_attribute("aria-pressed")
            print(f"New chip aria-pressed: {new_pressed}")
            if new_pressed == initial_pressed:
                 raise AssertionError("aria-pressed did not toggle!")
            if new_pressed not in ["true", "false"]:
                 raise AssertionError(f"Expected 'true' or 'false', but got '{new_pressed}'")

            # 4. Verify aria-live region
            print("Checking aria-live region...")
            results_div = page.locator("#symploke-search-results")
            aria_live = results_div.get_attribute("aria-live")
            print(f"Results aria-live: {aria_live}")
            if aria_live != "polite":
                 raise AssertionError(f"Expected 'polite', but got '{aria_live}'")

            # Take screenshot
            print("Taking screenshot...")
            page.screenshot(path="verification/search_a11y_verified.png")
            print("Verification successful! Screenshot saved.")

        except Exception as e:
            print(f"Verification failed: {e}")
            try:
                page.screenshot(path="verification/search_a11y_failed.png")
            except:
                pass
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    run()
