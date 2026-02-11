#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- mekhane/anamnesis/ P3→DOM調査が必要→inspect_message_turns が担う
"""
メッセージターン調査

.flex.flex-col.gap-y-3 の子要素を調査し、
個々のメッセージターン（User/Assistant）を特定する。
"""

import asyncio
import logging
from pathlib import Path

CDP_PORT = 9222
OUTPUT_FILE = Path(r"M:\Hegemonikon\mekhane\anamnesis\message_turns.txt")


# PURPOSE: CLI エントリポイント — 知識基盤の直接実行
async def main():
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}")

        # 正しい Agent Manager ページを選択
        agent_pages = []
        for ctx in browser.contexts:
            for pg in ctx.pages:
                if "jetski-agent" in pg.url:
                    try:
                        buttons = await pg.query_selector_all("button.select-none")
                        agent_pages.append((pg, len(buttons)))
                    except Exception as e:
                        logging.warning(f"Failed to inspect page {pg.url}: {e}")

        if not agent_pages:
            print("[!] Agent Manager not found")
            return

        agent_pages.sort(key=lambda x: x[1], reverse=True)
        page = agent_pages[0][0]
        print(f"[✓] Selected: {agent_pages[0][1]} buttons")

        lines = ["=== Message Turns Analysis ===\n"]

        # 会話をクリック
        buttons = await page.query_selector_all("button.select-none")
        for btn in buttons:
            try:
                title_el = await btn.query_selector("span[data-testid], span.truncate")
                if title_el:
                    title = await title_el.text_content()
                    if title and len(title.strip()) > 5 and "Inbox" not in title:
                        print(f"[*] Clicking: {title[:40]}")
                        await btn.click(force=True)
                        await asyncio.sleep(3)
                        lines.append(f"Clicked: {title[:60]}\n")
                        break
            except Exception:
                continue

        # メッセージコンテナを探す
        print("[*] Looking for message turns...")

        # .flex.flex-col.gap-y-3 のコンテナを探す
        containers = await page.query_selector_all(".flex.flex-col.gap-y-3")
        lines.append(f"\n=== .flex.flex-col.gap-y-3 containers: {len(containers)} ===")

        for i, container in enumerate(containers):
            text = await container.text_content()
            if text and len(text) > 1000:  # 十分な量のテキストがあるコンテナ
                classes = await container.get_attribute("class") or ""
                lines.append(f"\n[Container {i}] text_len={len(text)}")
                lines.append(f"  class='{classes}'")

                # 直接の子要素（メッセージターン？）
                children = await container.query_selector_all(":scope > *")
                lines.append(f"  Direct children: {len(children)}")
                lines.append("\n  --- Children details ---")

                for j, child in enumerate(children):
                    try:
                        c_tag = await child.evaluate("el => el.tagName")
                        c_class = await child.get_attribute("class") or ""
                        c_text = await child.text_content()
                        c_len = len(c_text) if c_text else 0

                        # 位置で User/Assistant を推測（偶数=User, 奇数=Assistant など）
                        position_hint = "EVEN" if j % 2 == 0 else "ODD"

                        lines.append(
                            f"\n  [{j}] <{c_tag}> ({position_hint}) text_len={c_len}"
                        )
                        lines.append(f"      class='{c_class[:100]}'")

                        # テキストプレビュー
                        if c_text:
                            preview = c_text[:150].replace("\n", " ").strip()
                            lines.append(f"      preview: '{preview}'")

                        # さらに子要素を調査
                        grandchildren = await child.query_selector_all(":scope > *")
                        if grandchildren:
                            lines.append(f"      grandchildren: {len(grandchildren)}")
                            for k, gc in enumerate(grandchildren[:3]):
                                try:
                                    gc_tag = await gc.evaluate("el => el.tagName")
                                    gc_class = await gc.get_attribute("class") or ""
                                    gc_text = await gc.text_content()
                                    gc_len = len(gc_text) if gc_text else 0
                                    lines.append(
                                        f"        [{k}] <{gc_tag}> class='{gc_class[:50]}' text_len={gc_len}"
                                    )
                                except Exception as e:
                                    logging.warning(
                                        f"Failed to inspect grandchild element {k}: {e}"
                                    )
                    except Exception as e:
                        logging.warning(f"Failed to inspect child element {j}: {e}")

                break  # 最初の大きなコンテナのみ

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"[✓] Saved to: {OUTPUT_FILE}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
