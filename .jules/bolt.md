## 2026-01-28 - Persistent Async HTTP Sessions
**Learning:** `aiohttp.ClientSession` should be reused to leverage connection pooling. Retrofitting this into a client designed for one-off requests can be done backward-compatibly by supporting context manager usage (`__aenter__`/`__aexit__`) while falling back to one-off sessions if not used as a context manager.
**Action:** When auditing async clients, always check for session reuse. Use the optional context manager pattern to introduce persistence safely without breaking existing synchronous-style instantiation code.
