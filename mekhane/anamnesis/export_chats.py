#!/usr/bin/env python3
"""
Antigravity IDE チャット履歴エクスポートツール
==============================================

Playwright を使用して Antigravity の Agent Manager から
チャット履歴を DOM 経由で抽出し、Markdown / JSON 形式で保存する。

使用方法:
    python export_chats.py                    # 全会話をエクスポート
    python export_chats.py --output sessions/ # 出力先指定
    python export_chats.py --format json      # JSON 形式で出力

必要条件:
    pip install playwright
    playwright install chromium
"""

import asyncio
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import argparse


# ============================================================================
# 設定
# ============================================================================

DEFAULT_OUTPUT_DIR = Path(r"M:\Brain\.hegemonikon\sessions")
CDP_PORT = 9222  # Chrome DevTools Protocol ポート


# ============================================================================
# エクスポータークラス
# ============================================================================

class AntigravityChatExporter:
    """簡潔版: Antigravity IDE のチャット履歴をエクスポート"""
    
    def __init__(self, output_dir: Path = DEFAULT_OUTPUT_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.chats: List[Dict] = []
        self.browser = None
        self.page = None
        
        # デバッグ: 出力ディレクトリ確認
        print(f"[DEBUG] Output directory: {self.output_dir}")
        print(f"[DEBUG] Exists: {self.output_dir.exists()}")
    
    async def connect(self) -> bool:
        """CDP 経由で Antigravity のブラウザに接続"""
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            
            # CDP エンドポイントに接続
            cdp_url = f"http://localhost:{CDP_PORT}"
            print(f"[*] Connecting to CDP: {cdp_url}")
            
            self.browser = await self.playwright.chromium.connect_over_cdp(cdp_url)
            
            # 既存のコンテキストからページを取得
            contexts = self.browser.contexts
            if not contexts:
                print("[!] No browser context found")
                return False
            
            # jetski-agent.html (Agent Manager) を探す
            self.page = None
            for ctx in contexts:
                for page in ctx.pages:
                    if 'jetski-agent' in page.url:
                        self.page = page
                        print(f"[✓] Found Agent Manager: {page.url}")
                        break
                if self.page:
                    break
            
            if not self.page:
                # fallback: 最初のページ
                self.page = contexts[0].pages[0] if contexts[0].pages else None
                if self.page:
                    print(f"[!] Agent Manager not found, using: {self.page.url}")
                else:
                    print("[!] No pages found")
                    return False
            
            return True
            
        except Exception as e:
            print(f"[✗] Connection failed: {e}")
            print("    → Antigravity IDE が起動していることを確認してください")
            return False
    
    async def extract_conversation_list(self) -> List[Dict]:
        """会話リストを抽出"""
        conversations = []
        
        try:
            # Agent Manager (jetski-agent.html) の会話ボタンを待機
            # DOM調査結果: button.select-none.hover\:bg-list-hover
            await self.page.wait_for_selector(
                'button.select-none',
                timeout=5000
            )
            
            # 会話ボタンを取得（タイトルを含む span[data-testid] を持つもの）
            items = await self.page.query_selector_all(
                'button.select-none'
            )
            
            for idx, item in enumerate(items):
                try:
                    # タイトルを取得 (span[data-testid] または span.text-sm.grow.truncate)
                    title_el = await item.query_selector('span[data-testid], span.truncate')
                    title = await title_el.text_content() if title_el else None
                    
                    if not title:
                        continue  # タイトルがないボタンはスキップ
                    
                    conversations.append({
                        "id": f"conv_{idx}",
                        "title": title.strip(),
                        "element": item
                    })
                except Exception as e:
                    print(f"[!] Error extracting conversation item: {e}")
                    continue
            
            print(f"[*] Found {len(conversations)} conversations")
            return conversations
            
        except Exception as e:
            print(f"[!] Error finding conversations: {e}")
            return []
    
    async def extract_messages(self) -> List[Dict]:
        """現在表示されている会話のメッセージを抽出"""
        messages = []
        
        try:
            # メッセージコンテナを待機
            await self.page.wait_for_selector(
                '[data-testid="message"], .message, [role="log"] > div',
                timeout=3000
            )
            
            # メッセージ要素を取得
            msg_elements = await self.page.query_selector_all(
                '[data-testid="message"], .message, [role="log"] > div'
            )
            
            for msg_el in msg_elements:
                try:
                    # ロールを判定
                    role = "assistant"
                    role_attr = await msg_el.get_attribute('data-role')
                    classes = await msg_el.get_attribute('class') or ""
                    
                    if role_attr:
                        role = role_attr
                    elif 'user' in classes.lower():
                        role = "user"
                    elif 'human' in classes.lower():
                        role = "user"
                    
                    # コンテンツを取得
                    content = await msg_el.text_content()
                    if content and content.strip():
                        messages.append({
                            "role": role,
                            "content": content.strip()
                        })
                except Exception as e:
                    continue
            
            return messages
            
        except Exception as e:
            print(f"[!] Error extracting messages: {e}")
            return []
    
    async def export_all(self):
        """全会話をエクスポート"""
        if not await self.connect():
            return
        
        conversations = await self.extract_conversation_list()
        
        for idx, conv in enumerate(conversations, 1):
            print(f"[{idx}/{len(conversations)}] {conv['title']}")
            
            try:
                # 会話をクリック
                await conv['element'].click()
                
                # クリック後の安定化待機
                # networkidle だと終わらないことがあるため、タイムアウト付きで待機
                try:
                    await self.page.wait_for_load_state('networkidle', timeout=2000)
                except:
                    pass
                
                await asyncio.sleep(1.0)  # UI 更新を確実に待機
                
                # メッセージを抽出
                messages = await self.extract_messages()
                
                # 記録を保存
                chat_record = {
                    "id": conv['id'],
                    "title": conv['title'],
                    "exported_at": datetime.now().isoformat(),
                    "message_count": len(messages),
                    "messages": messages
                }
                self.chats.append(chat_record)
                
                # 逐次保存 (individualモードの場合)
                await self.save_single_chat(chat_record)
                
                print(f"    → {len(messages)} messages extracted")
                
            except Exception as e:
                print(f"    → Error: {e}")
                continue
        
        await self.close()
    
    def save_markdown(self, filename: Optional[str] = None):
        """Markdown 形式で保存"""
        if not filename:
            filename = f"antigravity_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# Antigravity IDE チャット履歴\n\n")
            f.write(f"- **エクスポート日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"- **会話数**: {len(self.chats)}\n")
            f.write(f"- **総メッセージ数**: {sum(c['message_count'] for c in self.chats)}\n\n")
            f.write("---\n\n")
            
            for chat in self.chats:
                f.write(f"## {chat['title']}\n\n")
                f.write(f"- **ID**: `{chat['id']}`\n")
                f.write(f"- **メッセージ数**: {chat['message_count']}\n\n")
                
                for msg in chat['messages']:
                    role_label = "👤 **User**" if msg['role'] == 'user' else "🤖 **Claude**"
                    f.write(f"### {role_label}\n\n")
                    f.write(f"{msg['content']}\n\n")
                
                f.write("---\n\n")
        
        print(f"[✓] Saved: {filepath}")
        return filepath
    
    def save_json(self, filename: Optional[str] = None):
        """JSON 形式で保存"""
        if not filename:
            filename = f"antigravity_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.chats, f, ensure_ascii=False, indent=2)
        
        print(f"[✓] Saved: {filepath}")
        return filepath
    
    def _save_single_chat_sync(self, chat: Dict):
        """Sync implementation of saving a single chat"""
        # ファイル名をサニタイズ（ASCII のみ許可）
        title = chat['title']
        # 危険な文字を削除
        safe_title = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', title)
        # ASCII 以外の文字をアンダースコアに置換
        safe_title = ''.join(c if ord(c) < 128 else '_' for c in safe_title)
        # 複数のアンダースコアを1つにまとめる
        safe_title = re.sub(r'_+', '_', safe_title).strip('_')[:60]
        
        if not safe_title:
            safe_title = "untitled"
        
        date_prefix = datetime.now().strftime('%Y-%m-%d')
        id_prefix = chat['id'][:8] if chat['id'] else 'noname'
        
        filename = f"{date_prefix}_{id_prefix}_{safe_title}.md"
        filepath = self.output_dir / filename
        
        print(f"[DEBUG] Saving to: {filepath}")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {chat['title']}\n\n")
                f.write(f"- **ID**: `{chat['id']}`\n")
                f.write(f"- **エクスポート日時**: {chat['exported_at']}\n\n")
                f.write("---\n\n")
                
                for msg in chat['messages']:
                    role_label = "## 👤 User" if msg['role'] == 'user' else "## 🤖 Claude"
                    f.write(f"{role_label}\n\n")
                    f.write(f"{msg['content']}\n\n")
            
            print(f"  [✓] Saved: {filename}")
        except Exception as e:
            print(f"  [!] Error saving file {filename}: {e}")
            import traceback
            traceback.print_exc()

    async def save_single_chat(self, chat: Dict):
        """1つの会話を保存 (非同期)"""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._save_single_chat_sync, chat)

    async def save_individual(self):
        """（非推奨：逐次保存を使用）各会話を個別ファイルとして保存"""
        print("[*] Re-saving all chats...")
        for chat in self.chats:
            await self.save_single_chat(chat)
    
    async def close(self):
        """リソースを解放"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()


# ============================================================================
# メイン
# ============================================================================

async def main():
    parser = argparse.ArgumentParser(
        description="Antigravity IDE チャット履歴エクスポート"
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"出力ディレクトリ (default: {DEFAULT_OUTPUT_DIR})"
    )
    parser.add_argument(
        '--format', '-f',
        choices=['md', 'json', 'both', 'individual'],
        default='individual',
        help="出力形式 (default: individual)"
    )
    
    args = parser.parse_args()
    
    exporter = AntigravityChatExporter(output_dir=args.output)
    
    try:
        await exporter.export_all()
        
        if not exporter.chats:
            print("[!] No chats exported")
            return 1
        
        if args.format == 'md':
            exporter.save_markdown()
        elif args.format == 'json':
            exporter.save_json()
        elif args.format == 'both':
            exporter.save_markdown()
            exporter.save_json()
        elif args.format == 'individual':
            await exporter.save_individual()
        
        print(f"\n[✓] Export complete: {len(exporter.chats)} conversations")
        return 0
        
    except Exception as e:
        print(f"[✗] Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
