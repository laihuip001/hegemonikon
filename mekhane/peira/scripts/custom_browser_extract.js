/**
 * custom_browser_extract.js
 * Extracts metadata and converts article content to Markdown using Turndown.
 */
(async () => {
    // 1. Load Turndown if not present
    if (typeof TurndownService === 'undefined') {
        await new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://unpkg.com/turndown/dist/turndown.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    // 2. Metadata Extraction (Original Logic)
    const result = {};
    result.url = window.location.href;
    result.title = document.querySelector('h1')?.innerText?.trim() || "";
    
    let dateText = document.querySelector('.p-article__date')?.innerText?.trim() || 
                   document.querySelector('.entry-date')?.innerText?.trim();
    if (!dateText) {
        const match = document.body.innerText.match(/\d{4}\.\d{2}\.\d{2}/);
        dateText = match ? match[0] : "";
    }
    result.date = dateText;

    const tagElements = Array.from(document.querySelectorAll('a[href*="/archives/type-tag/"], a[href*="/archives/tech-tag/"], a[href*="/archives/app-tag/"], .post_tag a'));
    result.metadata = { 
        tags: [...new Set(tagElements.map(el => el.innerText.trim()).filter(t => t.length > 0 && !t.includes('\n')))] 
    };

    // 3. Content Extraction & Conversion
    const turndownService = new TurndownService({ 
        headingStyle: 'atx', 
        codeBlockStyle: 'fenced' 
    });

    // Remove noise before conversion
    turndownService.remove('script');
    turndownService.remove('style');
    turndownService.remove('nav');
    turndownService.remove('footer');
    turndownService.remove('.related-posts');
    turndownService.remove('.ads');
    turndownService.remove('#comments');

    // Target main content area
    const contentElement = document.querySelector('article') || 
                           document.querySelector('.post-content') || 
                           document.querySelector('.entry-content') || 
                           document.querySelector('main') || 
                           document.body;

    // Convert
    result.markdown = turndownService.turndown(contentElement.innerHTML);

    return JSON.stringify(result);
})();
