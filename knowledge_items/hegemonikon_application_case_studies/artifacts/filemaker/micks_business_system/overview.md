# MICKS Business System: Project Overview

## 1. Context

The MICKS Business System is a FileMaker-based platform designed to manage system modifications and requests for multiple partner companies. It follows a multi-tenant, hierarchical structure.

## 2. Core Philosophy (Noēsis)

- **Cognitive Separation Principle**: 1 Screen = 1 Table = 1 Responsibility. Splitting layouts reduces cognitive load.
- **Hierarchical Responsibility Chain**: `Company` -> `System` -> `Major Function` -> `Intermediate Function` -> `Minor Function` -> `Modification/Request`. Ensures clear traceability of responsibility.
- **Dual Global Separation**: Strict distinction between UI state management (`G_UI_`) and search criteria (`G_SCH_`).

## 3. Project Status (as of 2026-02-05)

| Status | Feature |
| :---: | :--- |
| ✅ | Integrated UI Prototype (Company -> System sync) |
| ✅ | Verified Navigation Patterns (Popover -> Detail Layout) |
| ✅ | Global Search Infrastructure (`G_SCH_` + Portal Filter) |
| ✅ | **Phase 2: Layout Segmentation** (Ladder Navigation - System List complete) |
| ✅ | System List Layout (`システム一覧`) |
| ✅ | Function Hierarchies (Major -> Middle -> Minor - Expanded Data Verified) |
| ⬜ | CRUD Operations for Systems and Functions |
| ✅ | Test Data Expansion (90 Major / 270 Middle / 540 Minor verified) |
| ⬜ | Audit Logging (Modification/Request context) |

## 4. Architectural Shift: From Monopoly to Segmentation

- **Integrated Prototype (v1)**: A single "Control Center" layout (`System` base) managing multiple portals. Facilitated rapid prototyping and relationship validation.
- **Ladder Navigation (Split Architecture)**:
  - Each logic table (`会社一覧`, `システム一覧`, `大機能一覧`, etc.) receives its own dedicated layout.
  - Users navigate "down the ladder" (Company -> Click -> System -> Click -> Function).
  - Each step anchors the selection context in the `System` controller table.
  - Advantages: Aligns with FileMaker's native "Found Set" handling and fulfills the President's vision for clear, separate screens for each entity.

## 4. Design Patterns

- **System Controller Pattern**: Using a dedicated `System` table with global fields as a state controller to manage navigation and filtered relationships across the entire application.
- **FEP-Aligned Architecture**: Minimizing existence error by ensuring every request is docked to a specific, unique function ID.

## 5. Operational Strategy: The "Tatakidai" (Prototype) Cycle

To maintain momentum and ensure alignment with Senior Developers and the President:

- **The Tatakidai Approach**: Rapidly generate UI "prototypes" (tatakidai) using AI workflows (`/mek`). These serve as a base for discussion before deep logic is committed.
- **The 30-Minute Boundary**: Aim to share the current iteration with the Senior Developer 30 minutes before EOD. This creates a predictable feedback loop and prevents "over-polishing" in isolation.
- **Phase-Ladder Execution**: Execute the transition between levels (Company -> System -> Major Function) one rung at a time. Succeeding at one "rung" (e.g., Company to System navigation) provides the blueprint for the entire hierarchy.
