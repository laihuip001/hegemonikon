# Skills Deep Dive (from /eat Phase 1)

## 1. Definition and Core Logic

Antigravity Skills are an **open standard** for extending agent capabilities. They follow a **reusable package** model, allowing sets of instructions, best practices, and tools to be modularized.

### 1.1. Locations & Scope

| Location | Scope | Usage |
| :--- | :--- | :--- |
| `<workspace-root>/.agent/skills/<folder>/` | **Workspace** | Project-specific conventions, deployment flows, local tests. |
| `~/.gemini/antigravity/skills/<folder>/` | **Global** | Personal utilities, general-purpose tools, cross-project standards. |

---

## 2. The Progressive Disclosure Pattern

To manage token cost and context density, Antigravity agents do not "read everything" at once. They follow a three-stage activation process:

1. **Discovery**: Upon conversation start, the agent scans the `name` and `description` in the YAML frontmatter of available skills.
2. **Activation**: If the `description` matches the user's task context, the agent "opens" and reads the full `SKILL.md`.
3. **Execution**: The agent applies the specific instructions, patterns, and checklist provided in the skill while working.

**Implication**: The `description` field is a high-priority "filter" that must be keyword-optimized for agent recognition.

---

## 3. Structural Implementation

### 3.1. The SKILL.md File

Mandatory file containing YAML frontmatter.

```yaml
---
name: skill-identifier
description: Helps with X. Use when user needs Y. (Third-person keywords)
---
```

### 3.2. Recommended Directory Structure

```markdown
.agent/skills/
└─── my-skill/
    └─── SKILL.md       # Mandatory instructions
    ├─── scripts/       # Helper scripts (e.g., Python, Shell)
    ├─── examples/      # Reference implementations or "Ground Truth"
    └─── resources/     # Templates, checklists, or static data
```

---

## 4. Best Practices (Hegemonikón Alignment)

- **Skills as Focused Units**: Each skill should do one thing well (MECE).
- **Scripts as "Black Boxes"**: Instead of providing full source code in the instructions, instruct the agent to run scripts with `--help` first. This preserves context window space for the task implementation.
- **Decision Trees**: Complex skills should include explicit logic (If X, do Y) to guide the agent's judgment.

---

## 5. Hegemonikón Mapping

| Antigravity Concept | Hegemonikón Mapping | Potential Opportunity |
| :--- | :--- | :--- |
| **Global Skills** | Currently unused | Move generic Hegemonikón tools (scripts/ etc.) to Global |
| **scripts/ subfolder** | `.agent/scripts/` | Standardize script location within Skill folders for better encapsulation |
| **description filter** | $var and prompt logic | Refine Skill descriptions to be exactly "match-ready" for Antigravity's discovery logic |

---

## 6. Troubleshooting: Discovery & Activation Failure

### 6.1. Symptoms: The "Zero Use" State

Even if `SKILL.md` files exist in the correct directories, the `dispatch_log` may show **0 skill activations**. This indicates that the agent is not transitioning from *Discovery* to *Activation*.

### 6.2. The Discovery Gap

The most common cause for skills failing to trigger is a mismatch in the "Discovery" phase:

- **Language Bias**: Descriptions in non-English languages (e.g., Japanese) may require more specific keywords or may not match the agent's internal task-filtering logic as effectively as English descriptions.
- **Vague Descriptions**: If the `description` field is too generic (e.g., "Auto-reference for protocols"), the agent manager may not perceive it as relevant to the current conversation context.
- **Missing Global Directory**: The global skills directory (`~/.gemini/antigravity/skills/`) is not always pre-created. If placing skills there, the directory structure must be manually verified.

### 6.3. Recovery Protocol

1. **Keyword Optimization**: Rewrite the `description` to be explicitly keyword-rich and in the third person (e.g., "Provides implementation protocols for DMZ and TDD when editing configuration files").
2. **Explicit Invocation**: If a skill is not activating automatically, the user can mention it by its `name` to force the agent into the "Activation" phase.
3. **Path Verification**: Run `find` or `list_dir` to ensure the `SKILL.md` is exactly at `.agent/skills/<skill-folder>/SKILL.md`.

## 7. Forced Reference Rule (Solution Implementation)

### 7.1. Structural Requirement: Environment over Will

To combat the "Discovery Gap" where the agent fails to activate relevant skills, a mandatory **Skill Forced Reference Rule (v1.0)** was added to the `GEMINI.md` (Kernel). This moves the responsibility of skill activation from the agent's "will" (judgment call) to the "environment" (keyword-triggered mandatory reading).

### 7.2. Implementation Mechanism

The rule enforces a **Keyword-to-Path Mapping**. When specific high-intent keywords are detected in the user's input, the agent is instructed to immediately perform a `view_file` on the corresponding `SKILL.md`.

| Intent Keyword(s) | Target Skill | Path |
| :--- | :--- | :--- |
| 「なぜ」「本質」「根本的」 | **O1 Noēsis** | `.agent/skills/ousia/o1-noesis/SKILL.md` |
| 「目的」「意志」「望む」 | **O2 Boulēsis** | `.agent/skills/ousia/o2-boulesis/SKILL.md` |
| 「判断」「評価」「レビュー」 | **A2 Krisis** | `.agent/skills/akribeia/a2-krisis/SKILL.md` |
| 「実装」「作る」「構築」 | **O4 Energeia** | `.agent/skills/ousia/o4-energeia/SKILL.md` |
| 「開発」「コード」「プログラム」 | **Code Protocols** | `.agent/skills/code-protocols/SKILL.md` |

### 7.3. Operation Protocol

1. **Passive Scan**: Analyze user input for mapped keywords.
2. **Explicit Load**: If a match occurs, run `view_file` for the skill.
3. **Traceability**: Output `[Skill Loaded: {name}]` to confirm activation.
4. **Enforcement**: Non-activated skills for relevant tasks are logged as `skill_miss` in the `dispatch_log`.

---
*Generated 2026-02-05 during the initial concrete understanding session. Updated with Forced Reference Rule solution.*
