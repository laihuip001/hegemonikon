#!/usr/bin/env python3
"""
メッセージ要素詳細調査

.overflow-y-auto コンテナの子要素を詳細調査し、
個々のメッセージ要素のセレクタを特定する。
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
                if 'jetski-agent' in pg.url:
                    page = pg
                    print(f"[*] Found Agent Manager: {pg.url}")
                    break
        
        if not page:
            print("[!] Agent Manager not found")
            return
        
        print("[*] Inspecting message elements...")
        
        lines = ["=== Message Elements Analysis ===\n"]
        
        # 1. 会話コンテナを見つける
        containers = await page.query_selector_all('.overflow-y-auto')
        lines.append(f"Found {len(containers)} .overflow-y-auto containers\n")
        
        for i, container in enumerate(containers):
            text = await container.text_content()
            text_len = len(text) if text else 0
            
            # 一番大きなコンテナが会話ビュー
            if text_len > 2000:
                lines.append(f"\n=== Container {i}: text_len={text_len} ===")
                classes = await container.get_attribute('class') or ""
                lines.append(f"class='{classes}'")
                
                # 直接の子要素を調査
                children = await container.query_selector_all(':scope > *')
                lines.append(f"Direct children: {len(children)}")
                
                for j, child in enumerate(children):
                    try:
                        c_tag = await child.evaluate("el => el.tagName")
                        c_class = await child.get_attribute('class') or ""
                        c_text = await child.text_content()
                        c_len = len(c_text) if c_text else 0
                        
                        # 子要素の子も確認
                        grandchildren = await child.query_selector_all(':scope > *')
                        
                        lines.append(f"\n  [{j}] <{c_tag}> class='{c_class[:80]}' text_len={c_len} grandchildren={len(grandchildren)}")
                        
                        # テキストプレビュー
                        if c_text:
                            preview = c_text[:150].replace('\n', ' ')
                            lines.append(f"      preview: {preview}")
                        
                        # 孫要素も調査
                        for k, gc in enumerate(grandchildren[:5]):
                            try:
                                gc_tag = await gc.evaluate("el => el.tagName")
                                gc_class = await gc.get_attribute('class') or ""
                                gc_text = await gc.text_content()
                                gc_len = len(gc_text) if gc_text else 0
                                lines.append(f"        grandchild[{k}] <{gc_tag}> class='{gc_class[:50]}' text_len={gc_len}")
                            except:
                                pass
                    except Exception as e:
                        lines.append(f"  [{j}] Error: {e}")
                
                # このコンテナ内の特定パターンを探す
                lines.append("\n--- Looking for message patterns ---")
                
                # role属性を持つ要素
                role_elements = await container.query_selector_all('[role]')
                lines.append(f"Elements with role attribute: {len(role_elements)}")
                for el in role_elements[:10]:
                    role = await el.get_attribute('role')
                    tag = await el.evaluate("el => el.tagName")
                    lines.append(f"  <{tag}> role='{role}'")
                
                # data-* 属性
                data_elements = await container.query_selector_all('[data-testid], [data-message], [data-role]')
                lines.append(f"\nElements with data attributes: {len(data_elements)}")
                for el in data_elements[:10]:
                    tag = await el.evaluate("el => el.tagName")
                    testid = await el.get_attribute('data-testid') or ""
                    msg = await el.get_attribute('data-message') or ""
                    role = await el.get_attribute('data-role') or ""
                    lines.append(f"  <{tag}> testid='{testid}' msg='{msg}' role='{role}'")
                
                break  # 最初の大きなコンテナのみ調査
        
        # ファイルに書き込み
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"[✓] Saved to: {OUTPUT_FILE}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
