# Implementation: Synergeia Gemini API Migration

The Synergeia coordinator's Gemini client was updated to support the new SDK while maintaining its structured output capabilities.

## 1. Changes in `query()`

The main logic was streamlined to use the `Client` and explicit `GenerateContentConfig`.

### Before (Legacy)

```python
import google.generativeai as genai
genai.configure(api_key=api_key)
generation_config = {}
if response_schema:
    generation_config["response_mime_type"] = "application/json"
    generation_config["response_schema"] = response_schema
model_instance = genai.GenerativeModel(model, generation_config=generation_config)
response = model_instance.generate_content(prompt, request_options={"timeout": timeout})
```

### After (Modern)

```python
from google import genai
client = genai.Client(api_key=api_key)
generation_config = {}
if response_schema:
    generation_config["response_mime_type"] = "application/json"
    generation_config["response_schema"] = response_schema

config = genai.types.GenerateContentConfig(**generation_config) if generation_config else None
response = client.models.generate_content(
    model=model,
    contents=prompt,
    config=config
)
```

## 2. Key Improvements

- **Unified Config**: The `GenerateContentConfig` object explicitly handles response schemas and MIME types in a more structured way.
- **Schema Validation**: The new SDK provides tighter integration with Pydantic-based schemas (though Hegemonikón currently uses raw dict schemas for flexibility).

---

### Source

Transitioned: 2026-02-03 | Ref: `synergeia/gemini_api.py`
