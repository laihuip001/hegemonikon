#!/usr/bin/env python3
# PROOF: [L2/インフラ]
"""
PROOF: [L3/ユーティリティ]

P3 → チャット履歴の保存が必要
   → Playwright による履歴抽出
   → export_chats が担う

Q.E.D.

---

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

# GCP/Linux 環境に対応
DEFAULT_OUTPUT_DIR = Path("/home/laihuip001/oikos/mneme/.hegemonikon/sessions")
CDP_PORT = 9222  # Chrome DevTools Protocol ポート

# メッセージ抽出の閾値
MIN_MESSAGE_LENGTH = 1        # 短い User 入力（y, /boot）も抽出
MIN_USER_MESSAGE_LENGTH = 100 # これより短い = User の可能性が高い
MAX_USER_MESSAGE_LENGTH = 500 # これより長い = Assistant の可能性が高い
MAX_MESSAGE_CONTENT = 10000   # 保存するメッセージの最大長

# プリコンパイル正規表現（パフォーマンス向上）
RE_THOUGHT_FOR = re.compile(r'^Thought for \u003c?\d+s\s*')
RE_FILES_EDITED = re.compile(r'Files Edited.*?(?=\n\n|\Z)', re.DOTALL)
RE_PROGRESS_UPDATES = re.compile(r'Progress Updates.*?(?=\n\n|\Z)', re.DOTALL)
RE_BACKGROUND_STEPS = re.compile(r'Background Steps.*?(?=\n\n|\Z)', re.DOTALL)
RE_UI_STATUS = re.compile(r'\b(Running\.\.\.?|Generating\.?|GoodBad|OpenProceed|Cancel)\b')
RE_MULTI_NEWLINE = re.compile(r'\n{3,}')
RE_MULTI_SPACE = re.compile(r' {2,}')
RE_UNSAFE_FILENAME = re.compile(r'[\u003c\u003e:\"/\\|?*\x00-\x1f]')
RE_MULTI_UNDERSCORE = re.compile(r'_+')


# ============================================================================
# エクスポータークラス
# ============================================================================

class AntigravityChatExporter:
    """簡潔版: Antigravity IDE のチャット履歴をエクスポート"""
    
    def __init__(self, output_dir: Path = DEFAULT_OUTPUT_DIR, limit: int = None):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.chats: List[Dict] = []
        self.browser = None
        self.page = None
        self.limit = limit  # エクスポート上限
        
        # デバッグ: 出力ディレクトリ確認
        print(f"[DEBUG] Output directory: {self.output_dir}")
        print(f"[DEBUG] Exists: {self.output_dir.exists()}")
        if limit:
            print(f"[DEBUG] Limit: {limit} conversations")
    
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
            # 複数ある場合は button.select-none が最も多いページを選択
            self.page = None
            agent_pages = []
            
            for ctx in contexts:
                for page in ctx.pages:
                    if 'jetski-agent' in page.url:
                        # 会話ボタンの数をカウント
                        buttons = await page.query_selector_all('button.select-none')
                        agent_pages.append((page, len(buttons)))
                        print(f"[*] Found jetski-agent page: {len(buttons)} buttons")
            
            if agent_pages:
                # ボタン数が最も多いページを選択
                agent_pages.sort(key=lambda x: x[1], reverse=True)
                self.page = agent_pages[0][0]
                print(f"[✓] Selected Agent Manager: {self.page.url} ({agent_pages[0][1]} buttons)")
            
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
                    
                    # タイトルを先頭行のみに限定（即度なサニタイズ）
                    title = title.strip().split('\n')[0].strip()[:100]
                    
                    if not title or len(title) < 3:
                        continue
                    
                    conversations.append({
                        "id": f"conv_{idx}",
                        "title": title,
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
    
    async def scroll_and_collect_messages(self) -> List[Dict]:
        """スクロールしながらメッセージを収集する
        
        仮想スクロールにより DOM からメッセージが消えるため、
        スクロールしながら逐次メッセージを収集し蓄積する。
        """
        all_messages = []
        seen_content_hashes = set()
        
        try:
            container = await self.page.query_selector('.flex.flex-col.gap-y-3.px-4.relative')
            if not container:
                container = await self.page.query_selector('.flex.flex-col.gap-y-3')
            
            if not container:
                print("    [!] Container not found")
                return []
            
            max_iterations = 500
            same_scroll_count = 0
            prev_scroll_pos = -1
            
            print("    [*] Scrolling and collecting messages...")
            
            # まず最上部にスクロール
            await self.page.evaluate("""
                () => {
                    const c = document.querySelector('.flex.flex-col.gap-y-3.px-4.relative')
                        || document.querySelector('.flex.flex-col.gap-y-3');
                    if (!c) return;
                    let el = c.parentElement;
                    while (el) {
                        const s = window.getComputedStyle(el);
                        if (s.overflowY === 'auto' || s.overflowY === 'scroll') {
                            el.scrollTop = 0;
                            return;
                        }
                        el = el.parentElement;
                    }
                }
            """)
            await asyncio.sleep(1.0)
            
            for i in range(max_iterations):
                # 現在表示されているメッセージを収集
                raw_data = await container.evaluate("""
                    container => {
                        const results = [];
                        const children = container.querySelectorAll(':scope > div');
                        const excludeTags = new Set(['STYLE', 'SCRIPT', 'CODE', 'PRE']);
                        
                        function getTextContent(node, root) {
                            let text = '';
                            for (const child of node.childNodes) {
                                if (child.nodeType === Node.TEXT_NODE) {
                                    let parent = child.parentElement;
                                    let shouldExclude = false;
                                    while (parent && parent !== root) {
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
                                        text += getTextContent(child, root);
                                    }
                                }
                            }
                            return text;
                        }
                        
                        for (const child of children) {
                            const text = getTextContent(child, child).trim();
                            if (text && text.length > 0) {
                                results.push({
                                    clean_text: text,
                                    raw_text: child.textContent || "",
                                    section_idx: child.getAttribute('data-section-index')
                                });
                            }
                        }
                        return results;
                    }
                """)
                
                # 新しいメッセージを蓄積（重複除去）
                new_count = 0
                for item in raw_data:
                    content = item['clean_text']
                    # ハッシュで重複チェック
                    content_hash = hash(content[:200])  # 先頭200文字でハッシュ
                    if content_hash not in seen_content_hashes:
                        seen_content_hashes.add(content_hash)
                        all_messages.append(item)
                        new_count += 1
                
                if i % 20 == 0:
                    print(f"    [*] Scroll {i}: collected {len(all_messages)} messages (+{new_count})")
                
                # 下方向にスクロール
                scroll_pos = await self.page.evaluate("""
                    () => {
                        const c = document.querySelector('.flex.flex-col.gap-y-3.px-4.relative')
                            || document.querySelector('.flex.flex-col.gap-y-3');
                        if (!c) return -1;
                        let el = c.parentElement;
                        while (el) {
                            const s = window.getComputedStyle(el);
                            if (s.overflowY === 'auto' || s.overflowY === 'scroll') {
                                el.scrollTop += 500;
                                return el.scrollTop;
                            }
                            el = el.parentElement;
                        }
                        return -1;
                    }
                """)
                
                # スクロール位置が変わらなければ終了
                if scroll_pos == prev_scroll_pos:
                    same_scroll_count += 1
                    if same_scroll_count >= 3:
                        break
                else:
                    same_scroll_count = 0
                    prev_scroll_pos = scroll_pos
                
                await asyncio.sleep(0.15)
            
            print(f"    [✓] Collected {len(all_messages)} total messages")
            return all_messages
            
        except Exception as e:
            print(f"    [!] Scroll/collect error: {e}")
            import traceback
            traceback.print_exc()
            return all_messages
    
    def _process_raw_messages(self, raw_messages: List[Dict]) -> List[Dict]:
        """収集したメッセージをロール判定してフォーマット"""
        messages = []
        
        # Claude 判定パターン
        claude_patterns = [
            'Thought for', 'Files Edited', 'Progress Updates', 'Background Steps',
            'Ran terminal command', 'Open Terminal', 'Exit code', 'Always Proceed',
            'RunningOpen', 'Analyzed', 'Edited', 'Generating', 'GoodBad', 'OpenProceed',
        ]
        
        # User 判定パターン
        user_start_patterns = [
            '@', '/', 'Continue', '続けて', 'はい', 'いいえ',
            'y\n', 'Y\n', 'ok', 'OK', '実験', 'やってみ',
            '改善', '修正', 'まずは', '1', '2', '3',
        ]
        
        for i, item in enumerate(raw_messages):
            content = item['clean_text']
            raw_text = item.get('raw_text', '')
            section_idx = item.get('section_idx')
            
            # ロール判定
            role = "assistant"  # デフォルト
            
            is_claude = any(p in raw_text for p in claude_patterns)
            is_user = (
                len(content) < 200 and
                any(content.strip().startswith(p) for p in user_start_patterns)
            )
            
            if is_claude:
                role = "assistant"
            elif is_user:
                role = "user"
            elif section_idx is not None:
                try:
                    idx_num = int(section_idx)
                    role = "user" if idx_num % 2 == 0 else "assistant"
                except Exception:
                    pass  # TODO: Add proper error handling
            
            messages.append({
                "role": role,
                "content": content[:10000],
                "section_index": section_idx
            })
        
        return messages
    
    async def extract_messages(self) -> List[Dict]:
        """現在表示されている会話のメッセージを抽出
        
        DOM 構造:
        - .flex.flex-col.gap-y-3.px-4.relative がメッセージコンテナ
        - その子 div で text_len > 0 の要素がメッセージ
        - STYLE 要素の内容は TreeWalker で除外
        """
        messages = []
        
        try:
            # メッセージコンテナを探す
            container = await self.page.query_selector('.flex.flex-col.gap-y-3.px-4.relative')
            
            if not container:
                container = await self.page.query_selector('.flex.flex-col.gap-y-3')
            
            if not container:
                print("    [!] Message container not found")
                return []
            
            # N+1問題を解決するため、全メッセージを一括で抽出
            raw_data_list = await container.evaluate("""
                container => {
                    const results = [];
                    const children = container.querySelectorAll(':scope > div');
                    const excludeTags = new Set(['STYLE', 'SCRIPT', 'CODE', 'PRE']);
                    
                    function getTextContent(node, root) {
                        let text = '';
                        for (const child of node.childNodes) {
                            if (child.nodeType === Node.TEXT_NODE) {
                                // 除外すべき親があるか再帰的に確認
                                let parent = child.parentElement;
                                let shouldExclude = false;
                                while (parent && parent !== root) {
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
                                    text += getTextContent(child, root);
                                }
                            }
                        }
                        return text;
                    }

                    for (const child of children) {
                        results.push({
                            classes: child.className || "",
                            clean_text: getTextContent(child, child).trim(),
                            raw_text: child.textContent || "",
                            section_idx: child.getAttribute('data-section-index')
                        });
                    }
                    return results;
                }
            """)

            print(f"    [DEBUG] Found {len(raw_data_list)} child elements in container")
            
            skipped_placeholder = 0
            skipped_empty = 0
            skipped_short = 0

            for item in raw_data_list:
                try:
                    # プレースホルダーをスキップ（無効化して検証）
                    # if 'bg-gray-500' in item['classes']:
                    #     skipped_placeholder += 1
                    #     continue

                    clean_text = item['clean_text']
                    
                    if not clean_text:
                        skipped_empty += 1
                        continue
                    
                    if len(clean_text) < MIN_MESSAGE_LENGTH:
                        skipped_short += 1
                        continue
                    
                    # 「Thought for Xs」のみ除去（思考過程は不要）
                    clean_text = RE_THOUGHT_FOR.sub('', clean_text)
                    
                    # 全文を保持: メタ情報フィルタを無効化
                    # clean_text = RE_FILES_EDITED.sub('', clean_text)
                    # clean_text = RE_PROGRESS_UPDATES.sub('', clean_text)
                    # clean_text = RE_BACKGROUND_STEPS.sub('', clean_text)
                    # clean_text = RE_UI_STATUS.sub('', clean_text)
                    
                    # 連続する空白/改行を正規化
                    clean_text = RE_MULTI_NEWLINE.sub('\n\n', clean_text)
                    clean_text = RE_MULTI_SPACE.sub(' ', clean_text)
                    clean_text = clean_text.strip()
                    
                    if len(clean_text) < MIN_MESSAGE_LENGTH:
                        continue
                    
                    # ロール判定（改善版 v2）
                    # 1. 元テキストに「Thought for」があれば Claude
                    # 2. UI 要素パターンがあれば Claude（ツール出力）
                    # 3. フォールバック: index ベース（偶数=User, 奇数=Claude）
                    
                    # 元テキストを取得（Thought for 判定用）
                    raw_text = item['raw_text']
                    
                    # data-section-index を取得（フォールバック用）
                    section_idx = item['section_idx']
                    
                    # Claude 検出パターン
                    claude_patterns = [
                        'Thought for',
                        'Files Edited',
                        'Progress Updates',
                        'Background Steps',
                        'Ran terminal command',
                        'Open Terminal',
                        'Exit code',
                        'Always Proceed',
                        'RunningOpen',
                        'Analyzed',
                        'Edited',
                        'Generating',
                        'GoodBad',
                        'OpenProceed',
                    ]
                    
                    # User 検出パターン（明示的な User 入力）
                    user_start_patterns = [
                        '@', '/', 'Continue', '続けて', 'はい', 'いいえ',
                        'y\n', 'Y\n', 'ok', 'OK', '実験', 'やってみ',
                        '改善', '修正', 'まずは', '1', '2', '3',
                    ]
                    
                    role = "assistant"  # デフォルト
                    
                    # Claude 判定: Thought for または UI 要素
                    is_claude = any(p in raw_text for p in claude_patterns)
                    
                    # User 判定: 短いメッセージ + User パターン
                    is_user = (
                        len(clean_text) < 200 and
                        any(clean_text.strip().startswith(p) for p in user_start_patterns)
                    )
                    
                    if is_claude:
                        role = "assistant"
                    elif is_user:
                        role = "user"
                    elif section_idx is not None:
                        # index ベースフォールバック（偶数=User, 奇数=Claude）
                        try:
                            idx_num = int(section_idx)
                            role = "user" if idx_num % 2 == 0 else "assistant"
                        except Exception:
                            pass  # TODO: Add proper error handling
                    
                    messages.append({
                        "role": role,
                        "content": clean_text[:10000],
                        "section_index": section_idx
                    })
                    
                except Exception as e:
                    continue
            
            print(f"    [DEBUG] Skipped: empty={skipped_empty}, short={skipped_short}")
            return messages
            
        except Exception as e:
            print(f"    [!] Error extracting messages: {e}")
            return []
    
    async def export_all(self):
        """全会話をエクスポート"""
        if not await self.connect():
            return
        
        try:
            conversations = await self.extract_conversation_list()
            
            # limit がある場合、会話リストを制限
            if self.limit:
                conversations = conversations[:self.limit]
                print(f"[*] Limiting to {self.limit} conversations")
            
            for idx, conv in enumerate(conversations, 1):
                print(f"[{idx}/{len(conversations)}] {conv['title']}")
                
                try:
                    # 前回のメッセージ内容を記録（重複検出用）
                    prev_first_message = None
                    if self.chats:
                        prev_msgs = self.chats[-1].get('messages', [])
                        if prev_msgs:
                            prev_first_message = prev_msgs[0].get('content', '')[:100]
                    
                    # 会話をクリック（force=True で UI 干渉を回避）
                    await conv['element'].click(force=True)
                    
                    # ネットワーク安定化を待機（最大15秒）
                    try:
                        await self.page.wait_for_load_state('networkidle', timeout=15000)
                    except Exception:
                        print("    [!] Network idle timeout, proceeding...")
                    
                    # 初期待機（UI安定化）
                    await asyncio.sleep(3.0)
                    
                    # メッセージコンテナが出現するまで待機
                    try:
                        await self.page.wait_for_selector(
                            '.flex.flex-col.gap-y-3.px-4.relative > div',
                            timeout=10000
                        )
                    except Exception:
                        print("    [!] Message container selector timeout, proceeding...")
                    
                    # コンテンツ変化を待機（最大15秒、500ms間隔でチェック）
                    content_changed = False
                    for _ in range(30):
                        messages = await self.extract_messages()
                        if messages:
                            first_msg = messages[0].get('content', '')[:100]
                            if first_msg != prev_first_message:
                                content_changed = True
                                break  # コンテンツが変化した
                        await asyncio.sleep(0.5)
                    
                    if not content_changed:
                        print("    [!] Content did not change, may be duplicate")
                    
                    # スクロールしながら全メッセージを収集
                    raw_messages = await self.scroll_and_collect_messages()
                    
                    # ロール判定とフォーマット
                    messages = self._process_raw_messages(raw_messages)
                    
                    # 重複チェック
                    if messages and prev_first_message:
                        first_msg = messages[0].get('content', '')[:100]
                        if first_msg == prev_first_message:
                            print("    [!] Duplicate content detected, skipping...")
                            continue
                    
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
                    self.save_single_chat(chat_record)
                    
                    print(f"    → {len(messages)} messages extracted")
                    
                except Exception as e:
                    print(f"    → Error: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
        finally:
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
    
    def save_single_chat(self, chat: Dict):
        """1つの会話を保存"""
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
                    # 連続3行以上の空行を1行に正規化
                    content = re.sub(r'\n{3,}', '\n\n', msg['content'])
                    f.write(f"{content}\n\n")
            
            print(f"  [✓] Saved: {filename}")
        except Exception as e:
            print(f"  [!] Error saving file {filename}: {e}")
            import traceback
            traceback.print_exc()

    def save_individual(self):
        """（非推奨：逐次保存を使用）各会話を個別ファイルとして保存"""
        print("[*] Re-saving all chats...")
        for chat in self.chats:
            self.save_single_chat(chat)
    
    async def close(self):
        """リソースを解放"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def export_single(self, title: str = "current_chat"):
        """現在表示されている会話のみをエクスポート（手動モード）"""
        if not await self.connect():
            return
        
        try:
            print(f"[*] Exporting current conversation: {title}")
            
            # 現在表示されているメッセージを抽出
            await asyncio.sleep(1.0)  # DOM 安定化待機
            messages = await self.extract_messages()
            
            if not messages:
                print("[!] No messages found in current view")
                return
            
            # 記録を保存
            chat_record = {
                "id": f"manual_{datetime.now().strftime('%H%M%S')}",
                "title": title,
                "exported_at": datetime.now().isoformat(),
                "message_count": len(messages),
                "messages": messages
            }
            self.chats.append(chat_record)
            self.save_single_chat(chat_record)
            
            print(f"    → {len(messages)} messages extracted")
            
        finally:
            await self.close()
    
    async def export_watch(self):
        """待機モード: コンテンツ変化を検出して自動エクスポート"""
        if not await self.connect():
            return
        
        print("[*] 待機モード開始！")
        print("[*] Agent Manager で会話を切り替えると自動でエクスポートします")
        print("[*] 終了するには Ctrl+C を押してください")
        print()
        
        exported_hashes = set()  # エクスポート済みコンテンツのハッシュ
        last_content_hash = None
        export_count = 0
        
        try:
            while True:
                try:
                    # 現在のメッセージを取得
                    messages = await self.extract_messages()
                    
                    if messages:
                        # コンテンツのハッシュを計算
                        content = "".join(m.get('content', '')[:200] for m in messages[:3])
                        content_hash = hash(content)
                        
                        # 新しいコンテンツを検出
                        if content_hash != last_content_hash and content_hash not in exported_hashes:
                            export_count += 1
                            
                            # タイトルを推測（最初のメッセージの先頭20文字）
                            title = messages[0].get('content', 'unknown')[:50].replace('\n', ' ')
                            
                            print(f"[{export_count}] 新しい会話を検出: {title[:30]}...")
                            
                            # 記録を保存
                            chat_record = {
                                "id": f"watch_{datetime.now().strftime('%H%M%S')}",
                                "title": title,
                                "exported_at": datetime.now().isoformat(),
                                "message_count": len(messages),
                                "messages": messages
                            }
                            self.chats.append(chat_record)
                            self.save_single_chat(chat_record)
                            
                            print(f"    → {len(messages)} messages extracted")
                            
                            last_content_hash = content_hash
                            exported_hashes.add(content_hash)
                    
                    # 1秒間隔でチェック
                    await asyncio.sleep(1.0)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"[!] Error: {e}")
                    await asyncio.sleep(2.0)
        
        finally:
            print(f"\n[*] 待機モード終了。{export_count} 件の会話をエクスポートしました")
            await self.close()


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
    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=None,
        help="エクスポートする会話数の上限 (テスト用)"
    )
    
    parser.add_argument(
        '--single', '-s',
        type=str,
        default=None,
        metavar='TITLE',
        help="手動モード: 現在表示されている会話だけをエクスポート"
    )
    
    parser.add_argument(
        '--watch', '-w',
        action='store_true',
        help="待機モード: 会話の切り替えを検出して自動エクスポート（Ctrl+C で終了）"
    )
    
    args = parser.parse_args()
    
    exporter = AntigravityChatExporter(output_dir=args.output, limit=args.limit)
    
    try:
        if args.watch:
            # 待機モード: 会話の切り替えを検出して自動エクスポート
            await exporter.export_watch()
        elif args.single:
            # 手動モード: 現在表示されている会話だけをエクスポート
            await exporter.export_single(title=args.single)
        else:
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
            exporter.save_individual()
        
        print(f"\n[✓] Export complete: {len(exporter.chats)} conversations")
        return 0
        
    except Exception as e:
        print(f"[✗] Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))



