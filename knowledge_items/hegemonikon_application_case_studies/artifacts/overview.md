# Hegemonikón Application Case Studies

This Knowledge Item documents the application of Hegemonikón's philosophical and operational framework to external platforms and real-world projects, specifically focusing on FileMaker development.

Key discoveries include the **Isolation Axiom** (safety protocol) and the **Complexity Floor** requirement for automated add-on generation.

## 1. FileMaker Mapping Strategy

The mapping of Hegemonikón to FileMaker focuses on the "Soul" (Process) rather than the "Body" (Syntax).

### 1.1. Workflow Integration

| Hegemonikón | FileMaker Phase | Note |
| :--- | :--- | :--- |
| `/zet` (Zētēsis) | Requirement Discovery | Exploring user needs and existing system frictions. |
| `/noe` (Noēsis) | System Architecture | Deep design of table relations, ERDs, and script architecture. |
| `/dia` (Dialectics) | Logic Review | Adversarial review of script logic and security. |
| `/ene` (Energeia) | Implementation | Actual script writing and layout design. |

### 1.2. Quality Assurance Patterns

- **`/dia` (Adversarial Review)**: Creating a checklist to probe for failure modes in complex scripts.
- **`/syn` (Council of Specialists)**: Reviewing the UI/UX from a user perspective vs. the DB performance from a developer perspective.
- **`/pan` (Blind Spot Search)**: Identifying missing error handling or edge cases in transaction logic.

---

## 2. Active Projects

### 2.1. Contractor Management (Legacy Context)

- **Description**: Initial case study for modification/request management systems.
- **Status**: Research phase conclude; archived as a precursor to the MICKS system.

### 2.2. MICKS Business System (Production)

- **Description**: A comprehensive business management system utilizing a 6-layer "Ladder Navigation" architecture.
- **Applied Patterns**:
  - **Anchor-Buoy Central Hub**: A star schema topology where a `System` controller table acts as the unified state hypervisor.
  - **Ladder Navigation Reset Rules**: Mandatory state clearing protocols to ensure context integrity during hierarchical transition.
  - **Prefix-Coded UUIDs**: Tier-specific prefixes (e.g., `d001-`, `m001-`) for high-speed logical verification of the relationship graph.
- **Core Artifacts**:
  - [Implementation Patterns](./filemaker/micks_business_system/implementation_details.md)
  - [TO Design Document](./filemaker/micks_business_system/to_design_document.md)
  - [Troubleshooting & Lessons Learned](./filemaker/micks_business_system/troubleshooting.md)

---

## 4. Technical Integration Bridge (The Production Core)

To bridge the gap between AI-driven design and low-code implementation, Hegemonikón leverages the **FileMaker Add-on (.fmaddon)** system.

### 4.1. Key Artifacts

- **[Add-on Research & History Archive](./filemaker/research_history_archive.md)**: Consolidation of early integration research, the Hybrid Workflow strategy, and the Isolation Axiom.
- **[Technical Teardown: Schema & Analysis](./filemaker/technical_teardown_archive.md)**: Detailed teardown of `.fmaddon` internals, XAR structure, and `template.xml` complexity.
- **[O1 Noēsis: Capability Boundary Analysis](./filemaker/noesis_capability_boundary_20260205.md)**: Deep analysis of what can be automated in FileMaker vs. what requires GUI intervention.
- **[Hegemonikón Mapping Methodology](./filemaker/hegemonikon_mapping.md)**: How to map philosophical workflows (Zētēsis, Noēsis) to low-code development phases.
- **[Case Study: Contractor Management](./filemaker/case_study_contractor_system.md)**: Initial prototype analysis that led to the MICKS system.

### 4.2. Strategy: Hybrid Workflow (Template Swapping)

Hegemonikón leverages a **Hybrid Workflow** to maintain aesthetic programmatic control:

1. **Skeleton Generation**: A one-time manual (GUI) use of FileMaker Pro's "Save a Copy as Add-on Package" to obtain a valid `template.xml` and manifest.
2. **SaXML Injection**: Hegemonikón generates architectural designs in SaXML format.
3. **Programmatic Modification**: Python/XSLT scripts inject the designed logic into the skeleton `template.xml`, replacing UUIDs and names.
4. **Repackaging**: Modified files are archived via `xar` for direct import into FileMaker Pro.
