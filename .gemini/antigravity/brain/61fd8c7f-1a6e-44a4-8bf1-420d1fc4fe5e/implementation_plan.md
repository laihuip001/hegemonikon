# Implementation Plan - Hegemonikón Interactive Guide

> **Based on S-Series Deep Analysis (/s+)**
> **Source Spec**: `gemini_frontend_spec_20260129.md`
> **Update**: X-Series Visualization Added (2026-01-29)

## STAGE 0: Blindspot + Scale Detection [S1 Metron/abst]

### Scale Determination: **Meso** (New Application Module)

- **Scope**: A standalone frontend application (`hegemonikon-guide`) within the `oikos` workspace.
- **Granularity**: New project structure, multiple components, data layer.
- **Abstraction**: Visualization of abstract concepts (CCL, X-series).

### Blindspot Check

- **Dependencies**: Node.js environment (v20.x verified).
- **Assets**: Need to ensure JSON data files are accurately extracted from existing documentation.
- **Responsiveness**: "Desktop First" but needs to function on Mobile.

---

## STAGE 1: Strategy Selection [S2 Mekhanē/comp]

### Strategy: **Exploit (Proven Tech Stack)** (comp: Composition)

- **Framework**: Vite + Vanilla JS.
  - *Reason*: Lightweight, faster iteration for a guide, no complex state management needed.
- **Styling**: Vanilla CSS (CSS Variables).
  - *Constraint*: **No TailwindCSS** (Strict adherence to GEMINI.md).
  - *Aesthetics*: Glassmorphism + Dark Mode (Premium feel).
- **Data**: Static JSON files (`data/*.json`).
  - *Reason*: Decouples content from logic, allows easy updates.

### Y-1 Time Scale Evaluation

- **Fast (<1 week)**: Quick setup with Vite, immediate visual feedback.
- **Slow (1-6 months)**: Maintainable due to standard web technologies. JSON data allows content updates without code changes.
- **Eternal (>1 year)**: Vanilla JS/CSS has the highest longevity and lowest depreciation risk.

---

## STAGE 2: Success Criteria [S3 Stathmos/norm]

### Rubric (Quality Standards)

- **Must**:
  - [x] All 6 Hubs navigable.
  - [x] 8 Operators displayed with tooltips/details.
  - [ ] X-series visualization interactive (hover/click).
  - [x] Command interactive input with partial matching.
  - [x] Dark Mode only (Premium aesthetic).
- **Should**:
  - [x] Smooth CSS transitions (no abrupt jumps).
  - [x] Glassmorphism blur effects working on supported browsers.

### Metrika (Quality Gates)

- **Atomos**: Keep functions under 30 lines, UI components under 120 lines.
- **Syntomia**: Nesting depth <= 3.

---

## STAGE 3: Blueprint [S4 Praxis/prax]

### Directory Structure

```
hegemonikon-guide/
├── index.html
├── src/
│   ├── style/
│   │   ├── main.css      (Reset + Base)
│   │   ├── tokens.css    (Variables)
│   │   └── components.css (Hubs, Cards)
│   ├── data/
│   │   ├── workflows.json
│   │   ├── operators.json
│   │   ├── derivatives.json
│   │   └── x-series.json  <-- NEW
│   └── main.js           (Entry + Router-ish logic)
└── package.json
```

### Execution Steps (/ene)

#### P1: Foundation [COMPLETED]

1. Initialize Vite project (`hegemonikon-guide`).
2. Define CSS Tokens (Colors, Glass effects, Typography) in `src/style/tokens.css`.
3. Create base layout structure in `index.html`.

#### P2: Core Components [COMPLETED]

4. Implement `HubNavigation` (HTML generator + CSS).
2. Implement `CCLCalculator` (Visual layout for operators).

#### P3: Logic & Interaction [COMPLETED]

7. Implement simplistic "Router" (Show/Hide sections).
2. Implement Interactive Input logic (Simple regex matching).
3. Populate JSON data from knowledge base.

#### P5: X-Series Visualization [NEW]

12. Create `src/data/x-series.json` with 36 relations mapped from the guide.
2. Update `index.html` to include `#x-series-view` container.
3. Implement `renderXSeries()` in `main.js` using SVG.
    - Layout: Circular ( trigonometric positioning).
    - Lines: `<line>` elements connecting centers.
    - Interaction: `mouseenter`/`click` on Hub Node -> Set `opacity: 1` on relevant lines.
4. Add Navigation item in Home view.

#### P4: Verification

10. Apply animations/transitions.
2. Record Demo Video.
