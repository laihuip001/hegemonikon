// ============================================================
// Antigravity セッションエクスポート（DevTools Console 用）
// ============================================================
// 使い方:
//   1. Antigravity で Ctrl+Shift+P → "Developer: Toggle Developer Tools"
//   2. DevTools の Console タブを開く
//   3. ⚠️ Console 上部のドロップダウンで "top" ではなく
//      "jetski-agent" を含むコンテキストを選択（あれば）
//   4. このスクリプト全体をペースト → Enter
//
// Phase 1: まず discovery() を実行して構造を確認
// Phase 2: exportAll() で全セッションをエクスポート
// ============================================================

// --- Phase 1: Discovery ---
async function discovery() {
    console.log('=== Phase 1: Discovery ===');

    // Check current context
    console.log('Current URL:', location.href);
    console.log('Title:', document.title);

    // Find webviews (Electron)
    const webviews = document.querySelectorAll('webview');
    console.log(`Webviews found: ${webviews.length}`);
    for (const wv of webviews) {
        console.log(`  webview: ${wv.src?.substring(0, 100)}`);
    }

    // Find iframes
    const iframes = document.querySelectorAll('iframe');
    console.log(`Iframes found: ${iframes.length}`);
    for (const iframe of iframes) {
        try {
            console.log(`  iframe: ${iframe.src?.substring(0, 100)}`);
        } catch (e) {
            console.log(`  iframe: (cross-origin)`);
        }
    }

    // Look for chat buttons in current context
    const buttons = document.querySelectorAll('button.select-none');
    console.log(`Chat buttons (button.select-none): ${buttons.length}`);

    // Alternative selectors
    const altButtons = document.querySelectorAll('[role="button"]');
    console.log(`Role=button elements: ${altButtons.length}`);

    // Look for any jetski-related elements
    const allElements = document.querySelectorAll('*');
    let jetskiCount = 0;
    for (const el of allElements) {
        if (el.className?.toString().includes('jetski') ||
            el.id?.includes('jetski')) {
            jetskiCount++;
        }
    }
    console.log(`Jetski-related elements: ${jetskiCount}`);

    // Try to find chat container with various selectors
    const selectors = [
        '.chat-widget',
        '[class*="chat"]',
        '[class*="conversation"]',
        '[class*="message"]',
        '.flex.flex-col.gap-y-3',
        '[data-testid]',
        'span.truncate',
    ];

    for (const sel of selectors) {
        const els = document.querySelectorAll(sel);
        if (els.length > 0) {
            console.log(`  ✓ "${sel}": ${els.length} elements`);
        }
    }

    // Try webview.executeJavaScript if webviews exist
    for (let i = 0; i < webviews.length; i++) {
        try {
            const result = await webviews[i].executeJavaScript(`
        JSON.stringify({
          url: location.href,
          title: document.title,
          buttons: document.querySelectorAll('button.select-none').length,
          truncateSpans: document.querySelectorAll('span.truncate').length,
          bodyLength: document.body?.innerHTML?.length || 0
        })
      `);
            const data = JSON.parse(result);
            console.log(`  webview[${i}]:`, data);
            if (data.buttons > 0 || data.url.includes('jetski')) {
                console.log(`  ★ THIS IS THE CHAT WEBVIEW (index ${i})`);
            }
        } catch (e) {
            console.log(`  webview[${i}]: executeJavaScript failed: ${e.message}`);
        }
    }

    console.log('\n=== Next Steps ===');
    console.log('If you see "★ THIS IS THE CHAT WEBVIEW" above, run exportAll()');
    console.log('If not, check the Console context dropdown (top-left) for jetski-agent');
}

// --- Phase 2: Export All ---
async function exportAll() {
    console.log('=== Phase 2: Export All Sessions ===');

    // Determine context: are we in the webview or do we need to proxy?
    const buttons = document.querySelectorAll('button.select-none');

    if (buttons.length === 0) {
        // Try through webview
        const webviews = document.querySelectorAll('webview');
        for (const wv of webviews) {
            try {
                const count = await wv.executeJavaScript(
                    `document.querySelectorAll('button.select-none').length`
                );
                if (count > 0) {
                    console.log(`Found ${count} conversations in webview, exporting via proxy...`);
                    await exportViaWebview(wv);
                    return;
                }
            } catch (e) { }
        }
        console.error('No chat buttons found. Switch Console context to jetski-agent.');
        return;
    }

    // Direct context - we're inside the chat panel
    await exportDirect();
}

async function exportDirect() {
    const buttons = document.querySelectorAll('button.select-none');
    const conversations = [];

    for (let i = 0; i < buttons.length; i++) {
        const span = buttons[i].querySelector('span[data-testid], span.truncate');
        const title = span?.textContent?.trim();
        if (title && title.length > 2) {
            conversations.push({ id: i, title: title.substring(0, 100) });
        }
    }

    console.log(`Found ${conversations.length} conversations`);

    const allData = {
        exported: new Date().toISOString(),
        count: conversations.length,
        conversations: []
    };

    for (let i = 0; i < conversations.length; i++) {
        const conv = conversations[i];
        console.log(`[${i + 1}/${conversations.length}] ${conv.title}`);

        // Click to open conversation
        const btn = document.querySelectorAll('button.select-none')[conv.id];
        if (btn) {
            btn.click();
            await new Promise(r => setTimeout(r, 2000)); // Wait for load

            // Extract messages
            const messages = extractMessages();
            allData.conversations.push({
                title: conv.title,
                messageCount: messages.length,
                messages: messages
            });
            console.log(`  → ${messages.length} messages`);
        }
    }

    // Download as JSON
    downloadJSON(allData, `antigravity_export_${new Date().toISOString().slice(0, 10)}.json`);

    // Also download as Markdown
    const md = toMarkdown(allData);
    downloadText(md, `antigravity_export_${new Date().toISOString().slice(0, 10)}.md`);

    console.log(`\n✓ Export complete: ${allData.conversations.length} conversations`);
}

async function exportViaWebview(wv) {
    const result = await wv.executeJavaScript(`
    (async function() {
      const buttons = document.querySelectorAll('button.select-none');
      const conversations = [];
      
      for (let i = 0; i < buttons.length; i++) {
        const span = buttons[i].querySelector('span[data-testid], span.truncate');
        const title = span?.textContent?.trim();
        if (title && title.length > 2) {
          conversations.push({ id: i, title: title.substring(0, 100) });
        }
      }
      
      const allData = {
        exported: new Date().toISOString(),
        count: conversations.length,
        conversations: []
      };
      
      for (let i = 0; i < conversations.length; i++) {
        const conv = conversations[i];
        const btn = document.querySelectorAll('button.select-none')[conv.id];
        if (btn) {
          btn.click();
          await new Promise(r => setTimeout(r, 2000));
          
          // Extract visible messages
          const msgs = [];
          const container = document.querySelector('.flex.flex-col.gap-y-3.px-4.relative');
          if (container) {
            const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT);
            let node, currentMsg = '';
            while (node = walker.nextNode()) {
              if (node.parentElement?.tagName !== 'STYLE') {
                currentMsg += node.textContent;
              }
            }
            if (currentMsg.trim()) msgs.push(currentMsg.trim());
          }
          
          allData.conversations.push({
            title: conv.title,
            messageCount: msgs.length,
            messages: msgs
          });
        }
      }
      
      return JSON.stringify(allData);
    })()
  `);

    const data = JSON.parse(result);
    downloadJSON(data, `antigravity_export_${new Date().toISOString().slice(0, 10)}.json`);
    const md = toMarkdown(data);
    downloadText(md, `antigravity_export_${new Date().toISOString().slice(0, 10)}.md`);
    console.log(`✓ Export complete: ${data.conversations.length} conversations`);
}

function extractMessages() {
    const messages = [];
    // Try multiple selectors
    const container = document.querySelector('.flex.flex-col.gap-y-3.px-4.relative')
        || document.querySelector('[class*="chat-messages"]')
        || document.querySelector('[role="log"]');

    if (!container) return messages;

    const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, {
        acceptNode: (node) => {
            if (node.parentElement?.tagName === 'STYLE') return NodeFilter.FILTER_REJECT;
            if (node.textContent.trim().length === 0) return NodeFilter.FILTER_REJECT;
            return NodeFilter.FILTER_ACCEPT;
        }
    });

    let node;
    let currentText = '';
    while (node = walker.nextNode()) {
        currentText += node.textContent + ' ';
    }

    if (currentText.trim()) {
        messages.push(currentText.trim().substring(0, 50000));
    }

    return messages;
}

function toMarkdown(data) {
    let md = `# Antigravity Session Export\n\n`;
    md += `- Exported: ${data.exported}\n`;
    md += `- Total: ${data.count} conversations\n\n---\n\n`;

    for (const conv of data.conversations) {
        md += `## ${conv.title}\n\n`;
        md += `Messages: ${conv.messageCount}\n\n`;
        for (const msg of conv.messages) {
            md += msg + '\n\n';
        }
        md += '---\n\n';
    }
    return md;
}

function downloadJSON(data, filename) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    console.log(`Downloaded: ${filename}`);
}

function downloadText(text, filename) {
    const blob = new Blob([text], { type: 'text/markdown' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    console.log(`Downloaded: ${filename}`);
}

// === START ===
console.log('Script loaded. Running discovery...');
discovery();
