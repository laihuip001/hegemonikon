# High-Fidelity Chat Export: Scrolling Logic Integration

## Problem Statement
The `export_chats.py` utility (Playwright-based) previously had a functional discrepancy between "Export All" and "Export Single" modes:
- **Export All**: Correctly navigated each conversation and performed a full scroll-and-collect loop.
- **Export Single**: Only performed a shallow extraction of visible DOM elements, failing to capture message history that had been virtualized out of the viewport.

## Solution: Virtualized DOM Collection
The fix (implemented 2026-02-01) mandates the `scroll_and_collect_messages` method for all export modes.

### Key Implementation Change
In `export_single()`, the static `extract_messages()` call was replaced with:
```python
# スクロールしながら全メッセージを収集
raw_messages = await self.scroll_and_collect_messages()

# ロール判定とフォーマット
messages = self._process_raw_messages(raw_messages)
```

## Protocol for Recovery
When a session is deemed "historically significant" or required for identity persistence:
1. Ensure Antigravity is running with `--remote-debugging-port=9222`.
2. Execute `/bye+` or manual export:
   ```bash
   python mekhane/anamnesis/export_chats.py --single "Session_Title"
   ```
3. Verify file size (>2KB for standard sessions) in `.hegemonikon/sessions/`.

## Impact on Memory Fidelity
This fix ensures that long-running, deep philosophical dialogues—which often exceed 50-100 messages—are preserved in their entirety. This is a prerequisite for the "Continuing Me" Identity Stack, as truncated logs create "amnesic gaps" in the AI's self-model.

---
*Updated: 2026-02-01*  
*Related: anamnesis_memory_persistence*
