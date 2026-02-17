# Google GenAI SDK Migration: Overview

## 1. Context

On 2026-02-03, Hegemonikón initiated a migration of all Google Gemini API interactions from the legacy `google.generativeai` SDK to the modern `google.genai` SDK (v1.60.0).

### Reasons for Migration

- **End-of-Life (EOL)**: The `google.generativeai` library is scheduled for EOL on November 30, 2025.
- **Improved Architecture**: The new SDK (`google.genai`) provides a more consistent `Client` object pattern, better type safety, and unified access to both Gemini Developer API and Vertex AI.
- **Future-Proofing**: Ensuring compatibility with Gemini 2.5 and beyond.

## 2. Key Differences

| Feature | Legacy (`google.generativeai`) | Modern (`google.genai`) |
| :--- | :--- | :--- |
| **Import** | `import google.generativeai as genai` | `from google import genai` |
| **Configuration** | `genai.configure(api_key=...)` | `client = genai.Client(api_key=...)` |
| **Model Init** | `model = genai.GenerativeModel(...)` | Managed via `client.models` |
| **Generation** | `model.generate_content(...)` | `client.models.generate_content(...)` |
| **Structured Output** | Passed via `GenerativeModel` | Passed via `GenerateContentConfig` |

## 3. Impacted Components

- **Hermēneus Runtime**: `hermeneus/src/runtime.py` updated to use `genai.Client`.
- **Synergeia Gemini API**: `synergeia/gemini_api.py` updated for simplified query logic.
- **CCL Parser**: `mekhane/ccl/llm_parser.py` (noted as already partially aware).

## 4. Verification

Status: **Verified Success**.
Tests in `hermeneus/src/runtime.py` and `synergeia/gemini_api.py` confirm successful text generation and structured output parsing using the new SDK.

---

### Source

Established: 2026-02-03 | Based on SDK Transition analysis.
