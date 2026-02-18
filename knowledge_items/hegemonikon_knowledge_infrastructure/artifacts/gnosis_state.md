# Gnōsis Research Infrastructure

## 1. Role in Hegemonikón

Gnōsis (知識) is the research-focused knowledge layer of the system. It bridges the gap between the agent's pre-trained knowledge and live/curated technical data (papers, articles, docs).

## 2. Technical Stack

- **Database**: **LanceDB** (serverless vector database).
- **Embedding Model**: ONNX-based (e.g., BGE-small) for local, fast inference without external API calls.
- **CLI Management**: `mekhane/anamnesis/cli.py` (Main Gnōsis/Anamnesis CLI).
  - *Note*: Former references to `forge/gnosis/cli.py` or `mekhane/gnosis/cli.py` are deprecated/stale.
- **Enforcement**: Mandatory Vector Search is enforced via `~/.gemini/GEMINI.md` to prevent falling back to inefficient keyword/grep searches.

## 3. Knowledge Streams

- **AIDB**: 795 articles (LanceDB 1,331 chunks).
- **Note.com**: Direct ingestion from technical profiles (e.g., `tasty_dunlin998`) via `note-collector.py`. (✅ Status: 120 articles collected 2026-02-06. Digesting high-priority technical articles).
- **arXiv/Semantic Scholar/OpenAlex**: High-throughput research paper ingestion via Anamnesis (570+ papers).
- **Documentation**: Codebase-level architectural documentation (Hegemonikón KIs).

## 4. Operational Integration

The system triggers Gnōsis automatically under the following conditions:

- **Uncertainty Score (U) > 0.6**.
- **Topic**: Technical consultation, architecture design, or research analysis.
- **Workflow**: Explicitly triggered via `/sop` or `/noe`.

As of 2026-02-06, GNOSIS is managed via the **Anamnesis** module. The index has been massively populated with **570+ papers** across diverse domains:

- **Core AI**: LLM prediction error, transformer architecture, prompt engineering, multi-agent orchestration.
- **Cognitive Science**: Active Inference (FEP), Bayesian brain, cognitive architectures (ACT-R, SOAR), self-modeling.
- **Mathematics**: Category theory, functorial semantics, informational aesthetics.
- **Cognitive Algebra**: CCL implementation, Existential Purpose Tensors, EPT logic.

New papers are tracked in `mekhane/anamnesis/state.json`.

### 5. Mandatory Vector Search Protocol (2026-02-07)

To minimize informational entropy and ensure semantic retrieval, the following protocol is enforced:

1. **Tool Choice**: Always use `python mekhane/anamnesis/cli.py search "query"` for Gnōsis.
2. **Prohibition**: Direct `grep` or keyword-based string matching on `gnosis_data/` is strictly prohibited as a primary discovery method.
3. **Pathing**: The root directory for search execution must be the Hegemonikón project root (`~/oikos/hegemonikon`).

### state.json Schema

```json
{
  "last_collected_at": "ISO-TIMESTAMP",
  "undigested": {
    "papers": [],
    "jules_prs": []
  },
  "digestion_log": []
}
```

These un-digested entries serve as "chemotactic signals" for the Auto-Digest Agent (WBC) during the `/boot` sequence, triggering the **Convergent Digestion Hub**.
