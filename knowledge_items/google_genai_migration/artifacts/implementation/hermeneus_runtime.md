# Implementation: Hermēneus Runtime Migration

The Hermēneus execution engine was updated to use the `google.genai` SDK for its fallback execution path.

## 1. Changes in `_execute_google`

The legacy static configuration pattern was replaced with a `Client` instance.

### Before (Legacy)

```python
import google.generativeai as genai
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-3-pro-preview")
response = await asyncio.wait_for(
    asyncio.to_thread(model.generate_content, prompt),
    timeout=self.config.timeout
)
```

### After (Modern)

```python
from google import genai
client = genai.Client(api_key=api_key)
model_name = "gemini-2.5-pro-preview-05-06" # Updated to latest preview
response = await asyncio.wait_for(
    asyncio.to_thread(
        client.models.generate_content,
        model=model_name,
        contents=prompt
    ),
    timeout=self.config.timeout
)
```

## 2. Key Improvements

- **Instance Isolation**: Using a `Client` object allows for better isolation of API keys and configurations compared to the global `genai.configure`.
- **Async Handling**: Although the `client.models.generate_content` is synchronous in the basic SDK, it is wrapped in `asyncio.to_thread` to maintain runtime non-blocking performance.
- **Model Versioning**: Migrated to `gemini-2.5-pro-preview-05-06` to leverage improved reasoning capabilities.

---

### Source

Transitioned: 2026-02-03 | Ref: `hermeneus/src/runtime.py`
