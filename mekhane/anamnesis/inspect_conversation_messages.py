#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] P3→DOM調査が必要→inspect_conversation_messages が担う
"""
会話ビュー メッセージ要素 詳細調査

Agent Manager で会話をクリックした後の DOM を調査し、
メッセージ要素のセレクタを特定する。
"""

import asyncio
from pathlib import Path


CDP_PORT = 9222
OUTPUT_FILE = Path(r"M:\Hegemonikon\mekhane\anamnesis\conversation_messages_dom.txt")


async def main():
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}")
        
        # 正しい Agent Manager ページを選択（ボタン数が最も多いページ）
        agent_pages = []
        for ctx in browser.contexts:
            for pg in ctx.pages:
                if 'jetski-agent' in pg.url:
                    try:
                        buttons = await pg.query_selector_all('button.select-none')
                        agent_pages.append((pg, len(buttons)))
                        print(f"[*] Found jetski-agent page: {len(buttons)} buttons")
                    except Exception:
                        pass
        
        if not agent_pages:
            print("[!] Agent Manager not found")
            return
        
        agent_pages.sort(key=lambda x: x[1], reverse=True)
        page = agent_pages[0][0]
        print(f"[✓] Selected Agent Manager: {agent_pages[0][1]} buttons")
        
        lines = ["=== Conversation Messages DOM Analysis ===\n"]
        
        # 会話をクリック
        buttons = await page.query_selector_all('button.select-none')
        clicked = False
        
        for btn in buttons:
            try:
                title_el = await btn.query_selector('span[data-testid], span.truncate')
                if title_el:
                    title = await title_el.text_content()
                    if title and len(title.strip()) > 5 and 'Inbox' not in title and 'Start' not in title:
                        print(f"[*] Clicking: {title[:40]}")
                        await btn.click(force=True)
                        await asyncio.sleep(3)  # 会話ロード待機
                        clicked = True
                        lines.append(f"Clicked: {title[:60]}\n")
                        break
            except Exception:
                continue
        
        if not clicked:
            lines.append("[!] Could not click any conversation\n")
        
        # DOM 調査
        print("[*] Inspecting conversation view DOM...")
        
        # 1. iframe を探す
        iframes = await page.query_selector_all('iframe')
        lines.append(f"\n=== iframes: {len(iframes)} ===")
        for i, iframe in enumerate(iframes[:5]):
            src = await iframe.get_attribute('src') or ""
            name = await iframe.get_attribute('name') or ""
            title_attr = await iframe.get_attribute('title') or ""
            lines.append(f"  [{i}] src='{src[:80]}' name='{name}' title='{title_attr}'")
        
        # 2. スクロール可能領域を探す
        scroll_areas = await page.query_selector_all('[class*="overflow-y"], [class*="scroll"]')
        large_scrolls = []
        for el in scroll_areas[:100]:
            try:
                text = await el.text_content()
                if text and len(text) > 500:
                    classes = await el.get_attribute('class') or ""
                    large_scrolls.append((el, classes, len(text)))
            except Exception:
                pass
        
        large_scrolls.sort(key=lambda x: x[2], reverse=True)
        lines.append(f"\n=== Large scroll areas (top 5): ===")
        
        for i, (el, classes, text_len) in enumerate(large_scrolls[:5]):
            lines.append(f"\n[Scroll {i}] text_len={text_len}")
            lines.append(f"  class='{classes[:120]}'")
            
            # 子要素の構造
            children = await el.query_selector_all(':scope > *')
            lines.append(f"  direct children: {len(children)}")
            
            # 各子要素を調査
            for j, child in enumerate(children[:10]):
                try:
                    c_tag = await child.evaluate("el => el.tagName")
                    c_class = await child.get_attribute('class') or ""
                    c_text = await child.text_content()
                    c_len = len(c_text) if c_text else 0
                    
                    # User/Assistant の手がかりを探す
                    role_hint = ""
                    if c_text:
                        text_lower = c_text[:200].lower()
                        if 'user' in text_lower or 'human' in text_lower:
                            role_hint = " [USER?]"
                        elif 'assistant' in text_lower or 'claude' in text_lower or 'agent' in text_lower:
                            role_hint = " [ASSISTANT?]"
                    
                    lines.append(f"    [{j}] <{c_tag}> class='{c_class[:50]}' text_len={c_len}{role_hint}")
                    
                    # プレビュー
                    if c_text and c_len > 0:
                        preview = c_text[:100].replace('\n', ' ').strip()
                        lines.append(f"        preview: '{preview}'")
                except Exception:
                    pass
        
        # 3. .prose/.markdown を探す
        prose_elements = await page.query_selector_all('.prose, .markdown, .markdown-body')
        lines.append(f"\n\n=== .prose/.markdown elements: {len(prose_elements)} ===")
        for i, el in enumerate(prose_elements[:10]):
            try:
                text = await el.text_content()
                parent_class = await el.evaluate("el => el.parentElement?.className || ''")
                lines.append(f"  [{i}] text_len={len(text) if text else 0}")
                lines.append(f"      parent_class='{parent_class[:60]}'")
                if text:
                    lines.append(f"      preview: '{text[:100].replace(chr(10), ' ')}'")
            except Exception:
                pass
        
        # 4. data-testid を持つ要素
        testid_elements = await page.query_selector_all('[data-testid]')
        lines.append(f"\n\n=== Elements with data-testid: {len(testid_elements)} ===")
        for i, el in enumerate(testid_elements[:30]):
            try:
                testid = await el.get_attribute('data-testid')
                tag = await el.evaluate("el => el.tagName")
                text = await el.text_content()
                text_preview = (text[:50] + "...") if text and len(text) > 50 else (text or "")
                lines.append(f"  [{i}] <{tag}> testid='{testid}' text='{text_preview.replace(chr(10), ' ')}'")
            except Exception:
                pass
        
        # ファイルに書き込み
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"[✓] Saved to: {OUTPUT_FILE}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
