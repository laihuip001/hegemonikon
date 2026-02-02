# /zet Workflow Redesign: Logical Derivation

## 1. Problem Identification

The legacy `/zet` template suffered from **"Context Dilution"**. Critical constraints were too deep in the prompt, leading to quality loss in complex investigations.

## 2. The New Standard: Abbreviated Start (冒頭凝縮型)

The redesigned workflow uses a **Hybrid Model**:

- **Head (Condensed)**: Format, Task, Time in the first ~2,000 tokens (Positional Bias optimization).
- **Body (Deep)**: Granular Points of Inquiry, and Execution Rules.

### 2.1 Claude 4.5 Optimization

- **Lost in the Middle**: Accuracy drops from 75% to 55% in the window center.
- **Mitigation**: Place critical info in the first 500 tokens.
- **Format**: XML tags for boundaries + Markdown hierarchy. Prose > Bullets for depth.

---
*Updated: 2026-01-28*
