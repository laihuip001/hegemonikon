#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] P3→DOM調査が必要→inspect_message_v2 が担う
"""
メッセージ DOM 構造詳細調査 v2

CSS がどこから混入しているか特定し、
正確なメッセージ抽出セレクタを決定する。
"""

import asyncio
from pathlib import Path


CDP_PORT = 9222
OUTPUT_FILE = Path(r"M:\Hegemonikon\mekhane\anamnesis\message_dom_v2.txt")


async def main():
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}")
        
        # 正しいページを選択
        agent_pages = []
        for ctx in browser.contexts:
            for pg in ctx.pages:
                if 'jetski-agent' in pg.url:
                    try:
                        buttons = await pg.query_selector_all('button.select-none')
                        agent_pages.append((pg, len(buttons)))
                    except Exception:
                        pass  # TODO: Add proper error handling
        
        if not agent_pages:
            print("[!] Agent Manager not found")
            return
        
        agent_pages.sort(key=lambda x: x[1], reverse=True)
        page = agent_pages[0][0]
        print(f"[✓] Selected: {agent_pages[0][1]} buttons")
        
        lines = ["=== Message DOM Structure v2 ===\n"]
        
        # 会話をクリック
        buttons = await page.query_selector_all('button.select-none')
        for btn in buttons:
            try:
                title_el = await btn.query_selector('span[data-testid], span.truncate')
                if title_el:
                    title = await title_el.text_content()
                    if title and len(title.strip()) > 5 and 'Inbox' not in title:
                        print(f"[*] Clicking: {title[:40]}")
                        await btn.click(force=True)
                        await asyncio.sleep(3)
                        lines.append(f"Clicked: {title[:60]}\n")
                        break
            except Exception:
                continue
        
        # 1. .flex.flex-col.gap-y-3 内の構造を詳細調査
        container = await page.query_selector('.flex.flex-col.gap-y-3.px-4.relative')
        if not container:
            container = await page.query_selector('.flex.flex-col.gap-y-3')
        
        if container:
            lines.append(f"\n=== Message Container Found ===\n")
            
            # 直接の子要素
            children = await container.query_selector_all(':scope > div')
            lines.append(f"Direct children: {len(children)}")
            
            # テキストを持つ子要素のみ調査
            text_children = []
            for i, child in enumerate(children):
                try:
                    classes = await child.get_attribute('class') or ""
                    text = await child.text_content()
                    if text and len(text.strip()) > 50:
                        text_children.append((i, child, classes, len(text.strip())))
                except Exception:
                    pass  # TODO: Add proper error handling
            
            lines.append(f"\nChildren with text > 50 chars: {len(text_children)}")
            
            for idx, child, classes, text_len in text_children:
                lines.append(f"\n[{idx}] class='{classes[:80]}' text_len={text_len}")
                
                # 子要素の構造を詳細調査
                inner_html = await child.evaluate("el => el.innerHTML")
                
                # STYLE 要素があるか？
                style_elements = await child.query_selector_all('style')
                lines.append(f"  style elements: {len(style_elements)}")
                
                # テキストノードのみを取得（STYLE を除外）
                inner_text_without_style = await child.evaluate("""
                    el => {
                        // すべてのテキストノードを取得（style 要素を除く）
                        const walker = document.createTreeWalker(
                            el,
                            NodeFilter.SHOW_TEXT,
                            {
                                acceptNode: (node) => {
                                    if (node.parentElement.tagName === 'STYLE') {
                                        return NodeFilter.FILTER_REJECT;
                                    }
                                    return NodeFilter.FILTER_ACCEPT;
                                }
                            }
                        );
                        let text = '';
                        while (walker.nextNode()) {
                            text += walker.currentNode.textContent;
                        }
                        return text.trim();
                    }
                """)
                
                lines.append(f"  text without style: {len(inner_text_without_style)} chars")
                preview = inner_text_without_style[:200].replace('\n', ' ')
                lines.append(f"  preview: '{preview}'")
                
                # 孫要素の構造
                grandchildren = await child.query_selector_all(':scope > *')
                for j, gc in enumerate(grandchildren[:5]):
                    try:
                        gc_tag = await gc.evaluate("el => el.tagName")
                        gc_class = await gc.get_attribute('class') or ""
                        gc_text = await gc.text_content()
                        gc_len = len(gc_text.strip()) if gc_text else 0
                        lines.append(f"    [{j}] <{gc_tag}> class='{gc_class[:40]}' text_len={gc_len}")
                    except Exception:
                        pass  # TODO: Add proper error handling
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"[✓] Saved to: {OUTPUT_FILE}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
