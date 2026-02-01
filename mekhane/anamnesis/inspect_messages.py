#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] P3→DOM調査が必要→inspect_messages が担う
"""
会話を開いてからメッセージ要素を調査
"""

import asyncio
from pathlib import Path

CDP_PORT = 9222
OUTPUT_FILE = Path(r"M:\Hegemonikon\mekhane\anamnesis\message_elements.txt")


async def main():
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}")

        # jetski-agent.html を探す
        page = None
        for ctx in browser.contexts:
            for pg in ctx.pages:
                if "jetski-agent" in pg.url:
                    page = pg
                    print(f"[*] Found Agent Manager: {pg.url}")
                    break

        if not page:
            print("[!] Agent Manager not found")
            return

        lines = ["=== Message Elements Analysis ===\n"]

        # 1. まず会話ボタンを探す
        print("[*] Looking for conversation buttons...")
        conv_buttons = await page.query_selector_all("button.select-none")
        lines.append(f"Found {len(conv_buttons)} buttons with class 'select-none'")

        # 会話をクリックして開く
        clicked = False
        for btn in conv_buttons:
            try:
                title_el = await btn.query_selector("span[data-testid], span.truncate")
                if title_el:
                    title = await title_el.text_content()
                    if title and "Inbox" not in title and "Start" not in title:
                        print(f"[*] Clicking conversation: {title[:40]}")

                        # force オプションでクリック
                        await btn.click(force=True)
                        await asyncio.sleep(2)  # ロード待機
                        clicked = True
                        lines.append(f"\nClicked: {title[:60]}")
                        break
            except Exception as e:
                lines.append(f"Click error: {e}")
                continue

        if not clicked:
            lines.append("\n[!] Could not click any conversation")

        # 2. DOM を調査
        print("[*] Inspecting DOM after click...")

        # 全体のHTML長さ
        html = await page.content()
        lines.append(f"\nTotal HTML length: {len(html)}")

        # 様々なセレクタを試す
        selectors = [
            ".overflow-y-auto",
            ".overflow-auto",
            ".overflow-y-scroll",
            ".prose",
            ".markdown",
            '[role="log"]',
            '[role="feed"]',
            '[class*="message"]',
            '[class*="thread"]',
            "main",
            "article",
        ]

        for sel in selectors:
            try:
                elements = await page.query_selector_all(sel)
                if elements:
                    lines.append(f"\n=== {sel}: {len(elements)} matches ===")
                    for i, el in enumerate(elements[:3]):
                        tag = await el.evaluate("el => el.tagName")
                        classes = await el.get_attribute("class") or ""
                        text = await el.text_content()
                        lines.append(
                            f"  [{i}] <{tag}> class='{classes[:80]}' text_len={len(text) if text else 0}"
                        )
            except Exception:
                pass  # TODO: Add proper error handling

        # 3. テキストが長いdivを探す（メッセージコンテナ候補）
        lines.append("\n\n=== Large divs (text > 1000) ===")
        all_divs = await page.query_selector_all("div")
        large_divs = []

        for div in all_divs[:500]:
            try:
                text = await div.text_content()
                if text and len(text) > 1000:
                    classes = await div.get_attribute("class") or ""
                    children = await div.evaluate("el => el.children.length")
                    large_divs.append((classes, len(text), children))
            except Exception:
                pass  # TODO: Add proper error handling

        large_divs.sort(key=lambda x: x[1], reverse=True)

        for i, (classes, text_len, children) in enumerate(large_divs[:15]):
            lines.append(f"[{i}] text_len={text_len}, children={children}")
            lines.append(f"    class='{classes[:120]}'")

        # 4. data属性を持つ要素
        lines.append("\n\n=== Elements with data-* attributes ===")
        data_elements = await page.query_selector_all(
            "[data-testid], [data-message-id], [data-role]"
        )
        lines.append(f"Found {len(data_elements)} elements")

        for i, el in enumerate(data_elements[:20]):
            try:
                tag = await el.evaluate("el => el.tagName")
                testid = await el.get_attribute("data-testid") or ""
                msg_id = await el.get_attribute("data-message-id") or ""
                role = await el.get_attribute("data-role") or ""
                classes = await el.get_attribute("class") or ""
                text = await el.text_content()
                text_preview = (
                    (text[:50] + "...") if text and len(text) > 50 else (text or "")
                )

                lines.append(
                    f"  [{i}] <{tag}> testid='{testid}' msg_id='{msg_id}' role='{role}'"
                )
                lines.append(f"       class='{classes[:60]}'")
                lines.append(f"       text='{text_preview}'")
            except Exception:
                pass  # TODO: Add proper error handling

        # 書き込み
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"[✓] Saved to: {OUTPUT_FILE}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
