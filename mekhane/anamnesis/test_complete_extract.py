#!/usr/bin/env python3
# PROOF: [L3/テスト] export_chats が存在→その検証が必要→test_complete_extract が担う
"""
完全版メッセージ抽出テスト v3

改良版テキスト抽出ロジック（STYLE/SCRIPT/CODE 再帰除外）を使用して
1つの会話を完全にエクスポートし、品質を検証する。
"""

import asyncio
import re
from datetime import datetime
from pathlib import Path

CDP_PORT = 9222
OUTPUT_DIR = Path(r"M:\Brain\.hegemonikon\sessions")


async def extract_text_without_noise(element):
    """STYLE, SCRIPT, CODE を再帰的に除外してテキストを取得"""
    return await element.evaluate("""
        el => {
            const excludeTags = new Set(['STYLE', 'SCRIPT', 'CODE', 'PRE']);
            
            function getTextContent(node) {
                let text = '';
                for (const child of node.childNodes) {
                    if (child.nodeType === Node.TEXT_NODE) {
                        let parent = child.parentElement;
                        let shouldExclude = false;
                        while (parent && parent !== el) {
                            if (excludeTags.has(parent.tagName)) {
                                shouldExclude = true;
                                break;
                            }
                            parent = parent.parentElement;
                        }
                        if (!shouldExclude) {
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


async def extract_messages(page):
    """完全版メッセージ抽出"""
    messages = []

    try:
        container = await page.query_selector(".flex.flex-col.gap-y-3.px-4.relative")
        if not container:
            container = await page.query_selector(".flex.flex-col.gap-y-3")

        if not container:
            print("    [!] Container not found")
            return []

        children = await container.query_selector_all(":scope > div")
        print(f"    Found {len(children)} child elements")

        for child in children:
            try:
                classes = await child.get_attribute("class") or ""
                if "bg-gray-500" in classes:
                    continue

                # 改良版テキスト抽出
                clean_text = await extract_text_without_noise(child)

                if not clean_text or len(clean_text) < 10:
                    continue

                # "Thought for" を除去
                clean_text = re.sub(r"^Thought for <?\\d+s\\s*", "", clean_text)

                # 連続する空白/改行を正規化
                clean_text = re.sub(r"\n{3,}", "\n\n", clean_text)
                clean_text = re.sub(r" {2,}", " ", clean_text)

                if len(clean_text) < 10:
                    continue

                # section index を取得
                section_idx = await child.get_attribute("data-section-index")

                # ロール判定
                role = "assistant"

                user_patterns = [
                    "@",
                    "/",
                    "Continue",
                    "y",
                    "Y",
                    "ok",
                    "OK",
                    "続けて",
                    "はい",
                    "いいえ",
                    "実験",
                    "やってみ",
                    '"完全"',
                    "完全",
                    "的に",
                    "なぜ",
                    "もう",
                    "確認",
                ]

                if len(clean_text) < 500:
                    if any(clean_text.startswith(p) for p in user_patterns):
                        role = "user"
                    elif len(clean_text) < 100:
                        role = "user"

                messages.append(
                    {"role": role, "content": clean_text, "section_index": section_idx}
                )
                print(f"    [{section_idx}] {role}: {len(clean_text)} chars")

            except Exception as e:
                continue

        return messages

    except Exception as e:
        print(f"    [!] Error: {e}")
        import traceback

        traceback.print_exc()
        return []


async def main():
    from playwright.async_api import async_playwright

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}")

        # ページ選択
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

        # 会話をクリック
        buttons = await page.query_selector_all("button.select-none")
        conv_title = None

        for btn in buttons:
            try:
                title_el = await btn.query_selector("span[data-testid], span.truncate")
                if title_el:
                    title = await title_el.text_content()
                    if title and len(title.strip()) > 5 and "Inbox" not in title:
                        conv_title = title.strip()
                        print(f"[*] Clicking: {conv_title[:50]}")
                        await btn.click(force=True)
                        await asyncio.sleep(3)
                        break
            except Exception:
                continue

        if not conv_title:
            print("[!] No conversation clicked")
            return

        # メッセージ抽出
        print("[*] Extracting messages...")
        messages = await extract_messages(page)
        print(f"[*] Extracted {len(messages)} messages")

        # CSS が含まれているか確認
        css_detected = False
        for msg in messages:
            if (
                "/*" in msg["content"]
                or "@media" in msg["content"]
                or ".markdown" in msg["content"]
            ):
                css_detected = True
                print(f"[!] CSS detected in message {msg['section_index']}")

        if css_detected:
            print("[!] WARNING: CSS still present in extracted content")
        else:
            print("[✓] No CSS detected - extraction is clean!")

        # ファイルに保存
        if messages:
            safe_title = "".join(
                c if (ord(c) < 128 and ord(c) >= 32) else "_" for c in conv_title
            )
            safe_title = re.sub(r'[<>:"/|?*\n\r]', "", safe_title)
            safe_title = (
                re.sub(r"[\s_]+", "_", safe_title).strip("_")[:50] or "untitled"
            )

            filename = f"complete_{datetime.now().strftime('%H%M%S')}_{safe_title}.md"
            filepath = OUTPUT_DIR / filename

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {conv_title}\n\n")
                f.write(f"- **Exported**: {datetime.now().isoformat()}\n")
                f.write(f"- **Messages**: {len(messages)}\n")
                f.write(f"- **CSS Clean**: {not css_detected}\n\n")
                f.write("---\n\n")

                for msg in messages:
                    role_label = (
                        "## 👤 User" if msg["role"] == "user" else "## 🤖 Claude"
                    )
                    f.write(f"{role_label}\n\n")
                    f.write(f"{msg['content']}\n\n")
                    f.write("---\n\n")

            print(f"[✓] Saved: {filepath}")
        else:
            print("[!] No messages extracted")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
