# External Source Collection Protocols (v1.0)

## 1. Overview

Collection protocols define the mechanisms by which Hegemonikón acquires "Bone Marrow" (raw technical data) from external sources. These protocols ensure high-fidelity ingestion while managing API constraints and environmental stability.

## 2. Management Scripts

| Script | Source | Location | Role |
| :--- | :--- | :--- | :--- |
| **`aidb-kb.py`** | AIDB | `mekhane/peira/scripts/` | Articles search, metadata management, and indexing (LanceDB). |
| **`note-collector.py`** | note.com | `mekhane/peira/scripts/` | Fetching technical articles from specific creators via note.com API. |
| **`anamnesis/cli.py`** | arXiv/Scholar | `mekhane/anamnesis/` | High-throughput research paper ingestion and metadata extraction. |

## 3. note.com Collection Protocol

Designed to capture deep technical insights from selected experts (e.g., `tasty_dunlin998`).

### 3.1. Implementation

`note-collector.py` uses the `note.com` internal API (`/api/v2/creators/...`) to list and fetch article contents.

### 3.2. Operational Observations (2026-02-06)

- **API Status**: Responds with `200 OK` via standard `curl`.
- **Hanging Issue**: Large sequential requests (>100 articles) can hang the session if processed synchronously without timeouts.
- **Root Cause**: Backend rate limiting (quiet hangs) or socket timeouts in the `requests` layer when dealing with large JSON payloads.

### 3.3. Mitigation & Fallbacks

1. **Timeout Enforcement**: Ensure all collection scripts implement a strict `timeout` (e.g., 30s) on network requests.
2. **Efficient Body Fetching**: Use the `body` field provided in the creator contents API listing. For `TextNote` types, this field contains the full text, eliminating the need for independent page scraping or per-article requests.
3. **Background PID Management**: For batch sizes exceeding 50 articles, use `nohup` and background process redirection (`> /tmp/log 2>&1 &`) to ensure execution persistence across session resets.
4. **Chunked Fetching**: Set `per_page=20` to balance payload size and request frequency.

## 4. AIDB Collection Protocol

Focuses on the "weekly summary" articles and specific high-value substrates.

- **Storage Layer**: Raw markdown in `mekhane/peira/Raw/aidb/`.
- **Constraint**: Handles "Premium Locked" articles by prioritizing free full-text (58% of substrate) and utilizing "Digest" metadata for locked content.
- **Naturalization**: Integrated with `/sop` Phase 0.5.

## 5. Security & Governance

- **Sensitive Data**: Scripts must NEVER hardcode API keys (comply with `CONSTITUTION.md` and `GEMINI.md`).
- **Taint Tracking**: Information from non-verified external sources should be tagged as `[TAINT]` during the initial capture phase of the **Zero Entropy Protocol**.

----
*Updated: 2026-02-06*
*Current Focus: Expanding the 'Chemotactic Signal' list for prioritized digestion of note.com articles (120 articles corpus).*
