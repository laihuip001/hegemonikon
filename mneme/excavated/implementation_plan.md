# implementation_plan.md: AIDB Batch 5 Collection

## Goal Description
Collect articles for Batch 5 (Index 511-595) from `url_list.txt`.
Since the original extraction scripts are missing, I will implement a robust **browser-side extraction** using `Turndown` (via CDN) to safeguard the collection quality.

## User Review Required
> [!IMPORTANT]
> **Missing Script Replacement**: The original "Chunk 1/2" scripts were not found. I will use a custom script that injects `TurndownService` to convert HTML to Markdown directly in the browser. This ensures high-quality output compatible with previous batches.

## Proposed Changes

### Scripts
#### [NEW] Custom Browser Extraction Logic
I will use the following logic within the `browser_subagent` to extract content. I will combine Metadata and Content extraction into a cohesive flow to minimize overhead.

**Extraction Strategy:**
1.  **Metadata**: Extract title, date, tags (same as original).
2.  **Content**: 
    - Inject `Turndown` library from CDN.
    - Identify main content container (`article`, `.post-content`, etc.).
    - Clean DOM (remove ads, navs).
    - Convert to Markdown.
3.  **Return**: JSON object containing both metadata and full markdown.

**JavaScript Snippet (Conceptual):**
```javascript
async () => {
    // Load Turndown
    if (!window.TurndownService) {
        await fetch('https://unpkg.com/turndown/dist/turndown.js')
            .then(r => r.text())
            .then(eval);
    }
    
    // Metadata
    const meta = {
        url: window.location.href,
        title: document.querySelector('h1')?.innerText?.trim() || "",
        // ... date and tags extraction ...
    };

    // Content
    const service = new TurndownService({ headingStyle: 'atx', codeBlockStyle: 'fenced' });
    const contentEl = document.querySelector('article, .post-content, .entry-content, main') || document.body;
    const clone = contentEl.cloneNode(true);
    // Remove noise
    clone.querySelectorAll('script, style, nav, footer, .related, .ads').forEach(e => e.remove());
    
    meta.markdown = service.turndown(clone.innerHTML);
    
    return JSON.stringify(meta);
}
```

### Process Flow
1.  **Iterate** through URLs 511-595.
2.  **Browser Action**: Open URL -> Run Extraction JS.
3.  **Save**: Write to `temp_batch_data_5.json`.
4.  **Persist**: Run `python scripts/phase3-save-batch-parallel.py 5` incrementally (every 10 articles or so).

## Verification Plan

### Automated Verification
- **Run on 1st Article**: Test the extraction script on the first URL (Index 511).
- **Check Output**: Verify `temp_batch_data_5.json` contains valid Markdown.
- **Check Manifest**: Verify `manifest_5.jsonl` is updated correctly.

### Manual Verification
- Review the generated Markdown for the first article to ensure formatting is preserved.
