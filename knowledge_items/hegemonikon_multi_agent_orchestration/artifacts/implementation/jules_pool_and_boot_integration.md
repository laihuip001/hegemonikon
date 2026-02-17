# Jules Pool and Boot Integration

## 1. Pool Architecture

The **Jules Pool** system enables high-parallelism specialist reviews by managing multiple Google account configurations.

### 1.1. Capacity and Mapping

- **Scale**: 6 Ultra Tier accounts provided a total of 15 API keys.
- **Capacity**: ~1,800 tasks/day (300 tasks/day/account).
- **Accounts**: `jules_01` (makaron8426) to `jules_06` (rairaixoxoxo).

### 1.2. Dual-Access Modes

| Mode | Technology | Primary Benefit | Capacity |
| :--- | :--- | :--- | :--- |
| **CLI Pool** | Browser OAuth (`jules` CLI) | Cost-Optimal (Manual/FREE) | Max 3 Concurrent Sessions |
| **API Pool** | REST/gRPC (API Keys) | High-Parallelism & Speed | 300 Req/Day/Account |

## 2. Jitter-Based Resilience (AI-022 Diorthōsis)

To prevent "Thundering Herd" spikes when 60+ threads retry simultaneously, Joule employs **Exponential Backoff with Jitter**.

- **Jitter Strategy**: Randomly adds 0-25% of the `wait_time` to each retry attempt.
- **Traceability**: Separated session creation from polling to ensure Jules IDs are persisted even if completion fails.

## 3. Boot-Time Result Ingestion

The results of background specialist runs are automatically surfaced during the system initialization.

### 3.1. Flow Overview

1. **Detection**: `jules_results_loader.py` scans `docs/specialist_run_*.json`.
2. **Step 16 Integration**: The `/boot` sequence triggers the loader to print a summary table of findings.
3. **Actionability**: Critical/High findings are flagged immediately for the Creator, ensuring correction (Diorthōsis) is prioritized.

## 4. Selection and Load Balancing

The `coordinator.py` implements a Round-Robin strategy over the 15 verified API keys (`JULIUS_API_KEY_1` to `15`), distributing load across the 6-account pool.

---
*Updated: 2026-02-06. Consolidated: jules_pool_and_access.md, boot_integration.md, case_study_ai_022.md.*
