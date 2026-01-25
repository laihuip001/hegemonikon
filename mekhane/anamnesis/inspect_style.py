#!/usr/bin/env python3
"""
STYLE 要素の完全調査

TreeWalker が STYLE を除外できていない原因を特定する。
"""

import asyncio
from pathlib import Path


CDP_PORT = 9222
OUTPUT_FILE = Path(r"M:\Hegemonikon\mekhane\anamnesis\style_investigation.txt")


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
                    except:
                        pass
        
        if not agent_pages:
            print("[!] Agent Manager not found")
            return
        
        agent_pages.sort(key=lambda x: x[1], reverse=True)
        page = agent_pages[0][0]
        print(f"[✓] Selected: {agent_pages[0][1]} buttons")
        
        lines = ["=== STYLE Element Investigation ===\n"]
        
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
            except:
                continue
        
        # メッセージ要素を探す
        container = await page.query_selector('.flex.flex-col.gap-y-3.px-4.relative')
        if container:
            children = await container.query_selector_all(':scope > div')
            
            for i, child in enumerate(children):
                try:
                    classes = await child.get_attribute('class') or ""
                    if 'bg-gray-500' in classes:
                        continue
                    
                    text = await child.text_content()
                    if not text or len(text.strip()) < 50:
                        continue
                    
                    lines.append(f"\n=== Message {i} ===")
                    
                    # STYLE 要素を探す
                    style_elements = await child.query_selector_all('style')
                    lines.append(f"STYLE elements: {len(style_elements)}")
                    
                    for j, style in enumerate(style_elements):
                        style_text = await style.text_content()
                        lines.append(f"  STYLE[{j}] length: {len(style_text or '')}")
                        lines.append(f"  STYLE[{j}] preview: {(style_text or '')[:100]}...")
                    
                    # 改良版 TreeWalker で STYLE, SCRIPT, CODE を除外
                    clean_text = await child.evaluate("""
                        el => {
                            // より厳密なフィルタリング
                            const excludeTags = new Set(['STYLE', 'SCRIPT', 'CODE', 'PRE']);
                            
                            function getTextContent(node) {
                                let text = '';
                                for (const child of node.childNodes) {
                                    if (child.nodeType === Node.TEXT_NODE) {
                                        // 親が除外リストにあるか確認
                                        let parent = child.parentElement;
                                        while (parent) {
                                            if (excludeTags.has(parent.tagName)) {
                                                break;
                                            }
                                            parent = parent.parentElement;
                                        }
                                        if (!parent) {
                                            text += child.textContent;
                                        }
                                    } else if (child.nodeType === Node.ELEMENT_NODE) {
                                        if (!excludeTags.has(child.tagName)) {
                                            text += getTextContent(child);
                                        }
                                    }
                                }
                                return text;
                            }
                            
                            return getTextContent(el).trim();
                        }
                    """)
                    
                    lines.append(f"Clean text length (v2): {len(clean_text)}")
                    
                    # CSS が含まれているか確認
                    has_css = '/*' in clean_text or '@media' in clean_text or '.markdown' in clean_text
                    lines.append(f"Contains CSS: {has_css}")
                    
                    if has_css:
                        # CSS の位置を特定
                        idx = clean_text.find('/*')
                        if idx == -1:
                            idx = clean_text.find('@media')
                        if idx >= 0:
                            lines.append(f"CSS starts at position {idx}")
                            lines.append(f"Context: ...{clean_text[max(0,idx-30):idx+50]}...")
                    
                    # プレビュー
                    preview = clean_text[:200].replace('\n', ' ')
                    lines.append(f"Preview: {preview}")
                    
                    # 2つのメッセージだけ調査
                    if i > 135:
                        break
                    
                except Exception as e:
                    lines.append(f"Error: {e}")
                    continue
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"[✓] Saved to: {OUTPUT_FILE}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
