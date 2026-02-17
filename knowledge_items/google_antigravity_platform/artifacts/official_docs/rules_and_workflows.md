# Antigravity: Rules and Workflows

Rules and Workflows are the primary mechanisms for customizing agent behavior and standardizing procedural tasks in Google Antigravity.

## 1. Rules

Rules are Markdown-based constraints that guide the agent.

### 1.1. Scopes

- **Global Rules**: Defined in `~/.gemini/GEMINI.md`. These apply across all workspaces.
- **Workspace Rules**: Defined in `.agent/rules/`. These are project-specific.

### 1.2. Activation Modes

| Mode | Description |
| :--- | :--- |
| **Manual** | Activated only when explicitly mentioned (e.g., `@rule-name`). |
| **Always On** | Permanently active for all prompts in the scope. |
| **Model Decision** | The agent decides whether to activate based on the rule's description. |
| **Glob** | Automatically activated when the active file matches a pattern (e.g., `src/**/*.py`). |

### 1.3. Constraints

- **Character Limit**: Each rule file has a maximum limit of **12,000 characters**.
- **Reference**: Rules can reference other files using the `@filename` syntax.

## 2. Workflows

Workflows define a sequence of steps or prompts for repetitive tasks.

### 2.1. Features

- **Invocation**: Triggered via slash commands (e.g., `/deploy`).
- **Nesting**: Workflows can call other workflows as steps.
- **Agent Generation**: The agent can automatically generate a workflow from conversation history.

### 2.2. Format

- Workflows are stored as Markdown files (typically in `.agent/workflows/`).
- They include a title, description, and sequential steps.

## 3. Optimization and Best Practices

To maximize the effectiveness of Rules and Workflows within the 12KB limit, the following practices are established:

### 3.1. Behavioral Optimization (Primacy & Recency)

- **Lost in the Middle**: LLMs process information at the start and end of a file with the highest fidelity. Critical constraints and the primary objective must be placed at the very beginning and summarized again at the very end.
- **Rule Placement**: If a rule file is large, the most important behavioral triggers should be repeated in the first and last 20% of the artifact.

### 3.2. Formatting Performance

- **Structure**: Structural templates (JSON/YAML) can significantly impact performance. Workspace rules should use YAML frontmatter for metadata and standard Markdown for instructions.
- **Indentation**: Keep formatting simple. Excessive nesting (3+ levels) or complex ASCII decorations can act as noise and degrade instruction adherence.
- **Functional Beauty**: Use semantic Markdown tables instead of ASCII art boxes (`┌─┐`) for structure. In large files, this can reduce token usage by **40%** without loss of information, preventing truncation.
- **Affirmative Constraint**: Define the "desired state" (Goal-oriented) first. Use negative constraints ("Do not...") only as secondary clarification.

---
*Captured from official documentation and research investigations (2026-02-07).*
