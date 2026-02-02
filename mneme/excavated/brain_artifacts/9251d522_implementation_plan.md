# Implementation Plan - AIDB Batch 2 Collection

## Goal Description
Collect articles 151-270 from AIDB. The initial attempt using `browser_subagent` failed due to rate limiting (HTTP 429). The plan is to switch to a local Node.js script which implements robust retries and exponential backoff.

## User Review Required
> [!IMPORTANT]
> **Dependency Installation**: Requires `npm install puppeteer turndown @mozilla/readability jsdom` in the project root.

## Proposed Changes

### Configuration
#### [NEW] [url_list_batch_2.txt](file:///C:/Users/raikh/Forge/Raw/aidb/_index/url_list_batch_2.txt)
- Subset of the main URL list for this batch.

### Execution Strategy
1. **Install Dependencies**: Ensure `puppeteer` and other libs are available.
2. **Run Script**: Execute `node scripts/phase3-collect-markdown.js` targeted at the generated URL list.
   - *Note*: The script needs to be pointed to `url_list_batch_2.txt` or modified to accept it. Currently it defaults to `url_list.txt`. I may need to temporarily swap files or modify the script config.
3. **Save Data**: Use existing python scripts to process the output.

## Verification Plan
### Automated Tests
- Check exit code of the node script.
- Verify `manifest.jsonl` contains success entries for the target URLs.
- Check `capture_log.csv` for error rates.
