#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/anamnesis/
"""
PROOF: [L3/ユーティリティ]

P3 → 簡易エクスポートが必要
   → 会話リストのみ抽出
   → export_simple が担う

Q.E.D.

---

シンプル版: 会話リストのみエクスポート（メッセージ抽出なし）
ファイル生成の動作確認用
"""

import asyncio
import re
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(r"M:\Brain\.hegemonikon\sessions")
CDP_PORT = 9222


# PURPOSE: CLI エントリポイント — 知識基盤の直接実行
async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[DEBUG] Output: {OUTPUT_DIR} (exists: {OUTPUT_DIR.exists()})")

    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}")

        # jetski-agent.html を探す（複数ある場合はボタン数が最も多いページを選択）
        agent_pages = []
        for ctx in browser.contexts:
            for pg in ctx.pages:
                if "jetski-agent" in pg.url:
                    try:
                        buttons = await pg.query_selector_all("button.select-none")
                        agent_pages.append((pg, len(buttons)))
                        print(f"[*] Found jetski-agent page: {len(buttons)} buttons")
                    except Exception:
                        pass  # TODO: Add proper error handling

        if not agent_pages:
            print("[!] Agent Manager not found")
            return

        # ボタン数が最も多いページを選択
        agent_pages.sort(key=lambda x: x[1], reverse=True)
        page = agent_pages[0][0]
        print(f"[✓] Selected Agent Manager: {agent_pages[0][1]} buttons")

        # 会話ボタンを取得
        items = await page.query_selector_all("button.select-none")

        conversations = []
        for idx, item in enumerate(items):
            title_el = await item.query_selector("span[data-testid], span.truncate")
            title = await title_el.text_content() if title_el else None
            if title:
                conversations.append({"id": f"conv_{idx}", "title": title.strip()})

        print(f"[*] Found {len(conversations)} conversations")

        # 各会話をファイルに保存
        for conv in conversations:
            title = conv["title"]
            # 改行、制御文字、バックスラッシュを除去
            safe_title = title.replace("\n", " ").replace("\r", " ").replace("\\", "_")
            # ASCII のみに変換
            safe_title = "".join(
                c if (ord(c) < 128 and ord(c) >= 32) else "_" for c in safe_title
            )
            # 危険な文字を除去
            safe_title = re.sub(r'[<>:"/|?*]', "", safe_title)
            # 複数のスペース/アンダースコアを1つにまとめる
            safe_title = (
                re.sub(r"[\s_]+", "_", safe_title).strip("_")[:60] or "untitled"
            )

            filename = f"{datetime.now().strftime('%Y-%m-%d')}_{conv['id'][:8]}_{safe_title}.md"
            filepath = OUTPUT_DIR / filename

            print(f"  Saving: {filename}")

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n")
                f.write(f"- **ID**: `{conv['id']}`\n")
                f.write(f"- **Exported**: {datetime.now().isoformat()}\n\n")
                f.write("---\n\n")
                f.write("*メッセージ内容は後で抽出予定*\n")

            print(f"    [✓] Saved")

        await browser.close()

    print(f"\n[✓] Complete: {len(conversations)} files")


if __name__ == "__main__":
    asyncio.run(main())
