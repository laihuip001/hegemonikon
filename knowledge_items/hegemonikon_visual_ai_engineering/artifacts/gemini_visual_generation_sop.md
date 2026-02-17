# Gemini Visual Generation (Banana-kun) SOP

> **Source**: Derived from experimental FileMaker mockup generation (2026-02-06)

## 🎯 Best Practices for Imagen/Gemini

| Strategy | Implementation |
| :--- | :--- |
| **Few-Shot Examples** | Provide at least one visual or descriptive example to guide style. |
| **Negative Prompts** | Explicitly list elements to exclude (e.g., "no device frames", "no watermarks"). |
| **Style Blending** | Use percentages (e.g., "60% minimalist, 40% lifestyle") for precise aesthetic control. |
| **Constraint Repetition** | Repeat critical constraints at the beginning and end of long prompts. |
| **Text Limit** | Keep required text rendering under **25 characters** for accuracy. |

## 🖥️ Screenshot Replication Template

Used for generating realistic software interface captures (not mockups).

```text
A realistic screenshot of [Software Name] [Version] on [OS],
showing [Process/State]. Japanese interface.

EXACT WINDOW STRUCTURE (top to bottom):
1. TITLE BAR: "[Title]" with [OS] standard control buttons.
2. MENU BAR: [Item 1] | [Item 2] | [Item 3]
3. TOOLBAR: [Specific buttons or icons]
4. MAIN CONTENT AREA: [Description of sections, split views, etc.]

Style: Photorealistic [OS] application screenshot. NOT a mockup.
Muted colors typical of [OS]. Standard anti-aliased fonts.

⚠️ CRITICAL CONSTRAINTS:
- No device frames (laptops, monitors).
- Empty space surrounding the window is light gray.
- Exact [Software Name] interface elements only.
```

## 📊 Workflow & Infographic Template

```text
A professional Japanese workflow infographic. Clean, corporate design.
TITLE: "[Title in Japanese]"

TIMELINE showing [N] steps:
STEP 1 ([Time]): [Icon] - [Step Name]
- [Detail 1]
- [Detail 2]

... [Repeat for N steps] ...

Style: Minimalist business infographic. [Color] palette. 
Legible typography. Professional iconography.
```

## 🛠️ Troubleshooting & Refinement

| Issue | Resolution |
| :--- | :--- |
| **Garbled Text** | Limit to 25 chars; use English for generation then edit manually for Japanese. |
| **Abstract Layout** | Use a numbered "Exact Window Structure" to force hierarchy. |
| **Mockup Feel** | Add "NOT a mockup", "standard software UI", "photorealistic screenshot". |
| **Unspecified Elements** | Use Negative Prompts section: "DO NOT include [element]". |

---

*Verified 2026-02-06 for Hegemonikón Visual Engineering.*
