#!/usr/bin/env python3
# PROOF: [L3/テスト] <- mekhane/anamnesis/ export_chats が存在→その検証が必要→test_extract_v2 が担う
"""
メッセージ抽出 v2（STYLE 除外版）

TreeWalker を使用して STYLE 要素のテキストを除外し、
正確なメッセージ内容を抽出する。
"""

import asyncio
import re
from datetime import datetime
from pathlib import Path

CDP_PORT = 9222
OUTPUT_DIR = Path(r"M:\Brain\.hegemonikon\sessions")


async def extract_text_without_style(element):
    """STYLE 要素を除外してテキストを取得"""
    return await element.evaluate("""
        el => {
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


async def extract_messages(page):
    """メッセージを抽出"""
    messages = []

    try:
        # メッセージコンテナを探す
        container = await page.query_selector(".flex.flex-col.gap-y-3.px-4.relative")
        if not container:
            container = await page.query_selector(".flex.flex-col.gap-y-3")

        if not container:
            print("    [!] Message container not found")
            return []

        # 直接の子要素を取得
        children = await container.query_selector_all(":scope > div")
        print(f"    Found {len(children)} child elements")

        for child in children:
            try:
                classes = await child.get_attribute("class") or ""
                if "bg-gray-500" in classes:
                    continue

                # STYLE を除外してテキストを取得
                clean_text = await extract_text_without_style(child)

                if not clean_text or len(clean_text.strip()) < 10:
                    continue

                # "Thought for Xs" を除去
                clean_text = re.sub(r"^Thought for \d+s\s*", "", clean_text.strip())

                if len(clean_text) < 10:
                    continue

                # ロール判定
                role = "assistant"

                # User メッセージの特徴
                user_patterns = [
                    "@",
                    "/",
                    "Continue",
                    "y",
                    "ok",
                    "続けて",
                    "はい",
                    "いいえ",
                    "実験",
                    "やってみ",
                    "試し",
                ]

                # 短いメッセージで特定のパターンがあれば User
                if len(clean_text) < 300:
                    if any(clean_text.startswith(p) for p in user_patterns):
                        role = "user"
                    # または ASCII 以外の文字が多くて短い場合（日本語コマンド）
                    if (
                        len([c for c in clean_text if ord(c) > 127])
                        > len(clean_text) * 0.3
                    ):
                        role = "user"

                messages.append({"role": role, "content": clean_text[:5000]})
                print(f"    Extracted: {role} ({len(clean_text)} chars)")

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

        # メッセージを抽出
        print("[*] Extracting messages...")
        messages = await extract_messages(page)
        print(f"[*] Extracted {len(messages)} messages")

        # ファイルに保存
        if messages:
            safe_title = "".join(
                c if (ord(c) < 128 and ord(c) >= 32) else "_" for c in conv_title
            )
            safe_title = re.sub(r'[<>:"/|?*\n\r]', "", safe_title)
            safe_title = (
                re.sub(r"[\s_]+", "_", safe_title).strip("_")[:50] or "untitled"
            )

            filename = f"test_v2_{datetime.now().strftime('%H%M%S')}_{safe_title}.md"
            filepath = OUTPUT_DIR / filename

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {conv_title}\n\n")
                f.write(f"- **Exported**: {datetime.now().isoformat()}\n")
                f.write(f"- **Messages**: {len(messages)}\n\n")
                f.write("---\n\n")

                for i, msg in enumerate(messages):
                    role_label = (
                        "## 👤 User" if msg["role"] == "user" else "## 🤖 Claude"
                    )
                    f.write(f"{role_label}\n\n")
                    f.write(f"{msg['content']}\n\n")
                    if i < len(messages) - 1:
                        f.write("---\n\n")

            print(f"[✓] Saved: {filepath}")
        else:
            print("[!] No messages extracted")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
