# AIDB Article Collection Walkthrough (Batches 2-5)

## Overview
Successfully collected articles from index 151 to 595 using a local Node.js script.

## Results by Batch

| Batch | Range | Articles | Status |
|---|---|---|---|
| Batch 2 | 151-270 | 120 | 114 Success, 6 Failed (HTTP 500) |
| Batch 3 | 271-390 | 120 | 120 Success |
| Batch 4 | 391-510 | 120 | 120 Success |
| Batch 5 | 511-595 | 85 | 83 Success, 1 Failed (HTTP 500), 1 Invalid |
| **Total** | **151-595** | **445** | **437 Success (98.2%)** |

## Failures
The following URLs consistently returned HTTP 500 errors and could not be retrieved:
1. `https://ai-data-base.com/archives/87816`
2. `https://ai-data-base.com/archives/84069`
3. `https://ai-data-base.com/archives/84055`
4. `https://ai-data-base.com/archives/84975`
5. `https://ai-data-base.com/archives/85037`
6. `https://ai-data-base.com/archives/85996`
7. `https://ai-data-base.com/archives/74097` (Invalid URL/HTTP 500)

## Outputs
- **Manifest**: `Raw/aidb/_index/manifest.jsonl` (Merged)
- **Log**: `Raw/aidb/_index/capture_log.csv`
- **Files**: `Raw/aidb/202X/XX/*.md`
