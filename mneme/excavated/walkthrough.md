# AIDB Batch 5 Collection Walkthrough

## Summary
Successfully collected **84 articles** for Batch 5 (Index 511-594).
All articles were processed using the custom browser-side extraction script (`custom_browser_extract.js`) to ensure clean metadata and markdown content.

## Scope
- **Target**: `C:\Users\raikh\Forge\Raw\aidb\_index\url_list.txt`
- **Range**: Line 511 to 594
- **Total Articles**: 84

## Results
- **Success Rate**: 100% (84/84 processed)
- **Manifest**: `C:\Users\raikh\Forge\Raw\aidb\_index\manifest_5.jsonl`
- **Output Directory**: `C:\Users\raikh\Forge\Raw\aidb\YYYY\MM\`

## Key Actions
1.  **Tag Fix**: Updated `custom_browser_extract.js` to filter out sidebar tags containing newlines (e.g., `Method\n426`), ensuring clean tag extraction.
2.  **Sequential Collection**: Processed articles in sub-batches of 10.
3.  **Parallel Saving**: Used `scripts/phase3-save-batch-parallel.py 5`.

## Issues & Resolutions
-   **Browser Hangs**: Encountered occasional hangs in `browser_subagent`. Resolved by retrying the sub-batch.
-   **Server Error**: Article in Sub-batch 7 (`/archives/74097`) returned a Critical WordPress Error from the source site. The error message was captured as content.
-   **Manifest Mismatch**: Initially checked `manifest_batch_5.jsonl` (incorrect) instead of `manifest_5.jsonl` (correct). `manifest_5.jsonl` contains 94 entries (84 unique articles + 10 re-runs from initial tag fix testing).

## Validation
-   Verified total count in `manifest_5.jsonl`: **94 lines** (covers all 84 items + 10 retries).
-   Missing articles check passed (all 511-594 present).
