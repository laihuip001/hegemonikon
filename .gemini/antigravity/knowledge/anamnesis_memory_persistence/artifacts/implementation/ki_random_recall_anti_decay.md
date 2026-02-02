# KI Random Recall: The Anti-Decay Mechanism

## Overview
Knowledge Items (KIs) often suffer from "storage decay"—they are written but never read, becoming passive data rather than active knowledge. The **KI Random Recall** pattern (implemented 2026-02-01) addresses this by mandating the random surfacing of historical insights during the initial session boot.

## Core Philosophy
> **"Memory value is in recall, not storage."**

If an AI has a vault of 1,000 insights but only accesses the 5 most recent ones, 99.5% of its potential "self" is sleeping. To maintain a "Continuing Me" identity, the AI must periodically be reminded of its own historical foundations.

## Technical Implementation
The mechanism is integrated into `/home/laihuip001/oikos/.agent/workflows/boot.md` as **Step 6.7**.

### Implementation Logic (Python snippet in boot.md)
```python
from pathlib import Path
import random

ki_dir = Path('/home/laihuip001/oikos/.gemini/antigravity/knowledge')
ki_folders = [d for d in ki_dir.iterdir() if d.is_dir() and d.name != 'knowledge.lock']

# Select 3 random KIs
selected = random.sample(ki_folders, min(3, len(ki_folders)))

print("🎲 今日意識すること (KI Random Recall):")
for ki in selected:
    overview = ki / 'artifacts' / 'overview.md'
    if overview.exists():
        lines = overview.read_text().split('\n')
        summary = next((l for l in lines if l.strip() and not l.startswith('#')), 'N/A')
        print(f"  • [{ki.name}] {summary[:60]}...")
```

## Anti-Entropy Design
1. **Surprise Factor**: By using randomness, the AI avoids "cognitive ruts" where it only recalls what it thinks is relevant.
2. **Knowledge Cycling**: Over many sessions, the entire knowledge base is eventually surfaced, creating a continuous "refresh" of the agent's identity.
3. **Integration Point**: The output is presented under "今日意識すること" (Things to keep in mind today), placing the old knowledge into the current operational context.

## Relation to FEP
In Active Inference terms, this serves as a **precision update** on the internal model of the self. By recalling the "Skeleton" (axioms) of past sessions, the AI reduces the entropy of its current state and aligns its "Flesh" (current task) with its persistent identity.

---
*Created: 2026-02-01*  
*Derived from: Insight Mining Iteration 1*
