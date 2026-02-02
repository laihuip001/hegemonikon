# AIDB Article Collection - Batch 4

## Goal
Collect AIDB articles from URL list (Index 391-510) using HTTP-based fetch.

## Tasks

- [x] Create `scripts/phase3-fetch-simple.py` (requests + BeautifulSoup)
- [x] Run script for Batch 4 (URLs 391-510) → 120 articles collected
- [x] Verify output in `temp_batch_data_4.json`
- [x] Execute `python scripts/phase3-save-batch-parallel.py 4` → 120/120 saved
- [x] Confirm Markdown files created

# AIDB Article Collection - Batch 5 (Final)

## Goal
Collect remaining AIDB articles (Index 511-595).

## Tasks
- [ ] Run script for Batch 5 (URLs 511-595)
- [ ] Verify output in `temp_batch_data_5.json`
- [ ] Execute `python scripts/phase3-save-batch-parallel.py 5`
- [ ] Confirm Markdown files created

## Notes
- Switched from `browser_subagent` to `requests` due to 429 throttling
- This approach is faster and more reliable for static content
