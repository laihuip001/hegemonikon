# Symplokē Unified Memory API

## 1. API Definition

The **Unified Memory API** provides a standardized interface for retrieving information across the three cognitive layers of the Memory-First Architecture.

### Entry Point: `retrieve(query, layer)`

- **Args**:
  - `query`: The search string or semantic vector.
  - `layer`: One of `{episodic, semantic, working, all}`.
- **Returns**: A ranked list of candidates with relevance scores and source metadata.

## 2. Retrieval Logic by Layer

### Episodic Retrieval

- **Sources**: `handoff_index`, `persona_store`, `values_store`.
- **Purpose**: "What did I do last time?", "What is my stance on X?".

### Semantic Retrieval

- **Sources**: `knowledge_items`, `sophia_external`, `doxa_beliefs`, `patterns_library`.
- **Purpose**: "What is the definition of X?", "What is the standard implementation of Y?".

### Working Retrieval

- **Sources**: `current_context`, `active_task_file`, `plan_status`.
- **Purpose**: "What was I just doing?", "What are the current constraints?".

## 3. Pattern Implementation (@memory)

The API is surfaced in the CCL Standard Library via the following macros:

- `@memory(layer)`: Direct API call.
- `@recall`: Shortcut for Episodic retrieval.
- `@lookup`: Shortcut for Semantic retrieval.

---
*Created: 2026-01-31 (v7.5 Integration)*
