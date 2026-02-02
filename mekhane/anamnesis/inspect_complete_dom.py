#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- mekhane/anamnesis/ P3→DOM調査が必要→inspect_complete_dom が担う
"""
DOM 構造詳細調査 v3 — User/Claude 区別とツール呼び出し

「完全な」セッション履歴抽出のために：
1. User と Claude を区別する DOM 属性を特定
2. ツール呼び出しセクションの構造を特定
3. 空行の原因（表レイアウト）を特定
"""

import asyncio
from pathlib import Path

CDP_PORT = 9222
OUTPUT_FILE = Path(r"M:\Hegemonikon\mekhane\anamnesis\complete_dom_analysis.txt")


async def main():
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}")

        # 正しいページを選択
        agent_pages = []
        for ctx in browser.contexts:
            for pg in ctx.pages:
                if "jetski-agent" in pg.url:
                    try:
                        buttons = await pg.query_selector_all("button.select-none")
                        agent_pages.append((pg, len(buttons)))
                    except Exception:
                        pass  # TODO: Add proper error handling

        if not agent_pages:
            print("[!] Agent Manager not found")
            return

        agent_pages.sort(key=lambda x: x[1], reverse=True)
        page = agent_pages[0][0]
        print(f"[✓] Selected: {agent_pages[0][1]} buttons")

        lines = ["=== Complete DOM Analysis v3 ===\n"]

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

        # 1. User/Claude 区別の調査
        lines.append("\n=== User/Claude 区別調査 ===")

        container = await page.query_selector(".flex.flex-col.gap-y-3.px-4.relative")
        if container:
            children = await container.query_selector_all(":scope > div")

            for i, child in enumerate(children):
                try:
                    classes = await child.get_attribute("class") or ""
                    if "bg-gray-500" in classes:
                        continue

                    # テキスト長チェック
                    text = await child.text_content()
                    if not text or len(text.strip()) < 20:
                        continue

                    # 全属性を取得
                    all_attrs = await child.evaluate("""
                        el => {
                            const attrs = {};
                            for (const attr of el.attributes) {
                                attrs[attr.name] = attr.value;
                            }
                            return attrs;
                        }
                    """)

                    # data-role や aria-* を探す
                    lines.append(f"\n[Message {i}]")
                    lines.append(f"  all_attrs: {all_attrs}")

                    # 子要素の構造を調査
                    first_child = await child.query_selector(":scope > *")
                    if first_child:
                        fc_tag = await first_child.evaluate("el => el.tagName")
                        fc_class = await first_child.get_attribute("class") or ""
                        fc_attrs = await first_child.evaluate("""
                            el => {
                                const attrs = {};
                                for (const attr of el.attributes) {
                                    attrs[attr.name] = attr.value;
                                }
                                return attrs;
                            }
                        """)
                        lines.append(
                            f"  first_child: <{fc_tag}> class='{fc_class[:50]}'"
                        )
                        lines.append(f"  first_child_attrs: {fc_attrs}")

                        # さらに孫要素
                        grandchild = await first_child.query_selector(":scope > *")
                        if grandchild:
                            gc_tag = await grandchild.evaluate("el => el.tagName")
                            gc_class = await grandchild.get_attribute("class") or ""
                            lines.append(
                                f"  grandchild: <{gc_tag}> class='{gc_class[:50]}'"
                            )

                    # テキストプレビュー
                    preview = text[:100].replace("\n", " ").strip()
                    lines.append(f"  preview: '{preview}'")

                    # "Thought for" を含むか？
                    if "Thought for" in text:
                        lines.append(f"  [ASSISTANT INDICATOR: Contains 'Thought for']")

                    # 短いメッセージ（User の可能性）
                    if len(text.strip()) < 200:
                        lines.append(f"  [SHORT MESSAGE: {len(text.strip())} chars]")

                except Exception as e:
                    lines.append(f"  Error: {e}")
                    continue

        # 2. ツール呼び出しセクションの調査
        lines.append("\n\n=== ツール呼び出し調査 ===")

        # "Files Edited", "Task", "Progress" などのセクションを探す
        tool_indicators = [
            "Files Edited",
            "Task",
            "Progress",
            "run_command",
            "view_file",
            "write_to_file",
        ]

        for indicator in tool_indicators:
            elements = await page.query_selector_all(f':text("{indicator}")')
            lines.append(f"\n'{indicator}' found: {len(elements)} occurrences")

            for j, el in enumerate(elements[:2]):
                try:
                    parent = await el.evaluate(
                        "el => el.parentElement?.outerHTML?.slice(0, 200)"
                    )
                    lines.append(f"  [{j}] parent: {parent}")
                except Exception:
                    pass  # TODO: Add proper error handling

        # 3. data-testid を持つ要素の調査
        lines.append("\n\n=== data-testid 調査 ===")
        testid_elements = await page.query_selector_all("[data-testid]")

        testid_counts = {}
        for el in testid_elements:
            try:
                testid = await el.get_attribute("data-testid")
                if testid:
                    testid_counts[testid] = testid_counts.get(testid, 0) + 1
            except Exception:
                pass  # TODO: Add proper error handling

        for testid, count in sorted(testid_counts.items(), key=lambda x: -x[1])[:20]:
            lines.append(f"  {testid}: {count}")

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"[✓] Saved to: {OUTPUT_FILE}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
