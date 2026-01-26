## 2024-05-21 - [Playwright N+1 Bottleneck]
**Learning:** Iterating over Playwright ElementHandles in Python to extract data (e.g., text, attributes) causes massive N+1 IPC overhead. For example, extracting 200 messages took 3s individually vs 0.05s batched (~60x faster).
**Action:** Always batch extraction using a single `page.evaluate()` or `element.evaluate()` that returns a JSON-serializable list of data objects.
