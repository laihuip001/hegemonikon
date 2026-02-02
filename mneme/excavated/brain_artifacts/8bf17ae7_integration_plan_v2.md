# Forge v2.0: "DNA Transplantation" Plan

`dev-rules` を参照するのではなく、Forgeの血肉として統合する計画。

## 1. System Layer Integration (The Brain)

**統合方針:** `dev-rules/GEMINI_FULL.md` (Titanium Strategist) をベースに、Forge COO (Meta-Prompt Architect) の機能をマージする。

- **Base Personality**: Titanium Strategist (F1_RACING_SPEC)
- **Specialized Skill**: Meta-Prompt Architect (Forge COO)
- **Constitution**: `dev-rules/constitution/` を `Forge/constitution/` として正式配置

**New GEMINI.md Structure:**
1. **Identity**: Titanium Strategist + Forge COO
2. **Core Directives**: Guard, Prove, Undo + 垂直統合欲求
3. **Operational Constraints**: Termux, etc.
4. **Skills**:
    - **Meta-Prompting** (from Forge)
    - **Deep Thinking** (from dev-rules)
    - **Architecture Design** (from dev-rules)

## 2. Library Layer Integration (The Muscle)

`dev-rules/prompts/` のモジュール群を、Forge の `library/` (4段階) に再配置・統合する。

| dev-rules Module | Forge Library Destination |
|---|---|
| `A-*` (Analysis) | `library/perceive/` |
| `B-*` (Context) | `library/perceive/` |
| `X-*` (Divergence) | `library/think/` |
| `Q-*` (Quality) | `library/verify/` |
| `C-*` (Audit/Critique)| `library/verify/` |
| `E-*` (Execution) | `library/execute/` |
| `M-*` (Meta) | `library/execute/` |
| `I-*` (Integration) | `library/execute/` |

**Action:**
- `bible/dev-rules/prompts/` の中身を `library/` の適切フォルダに移動・リネーム。
- 既存の16テンプレートと重複する場合は、`dev-rules` 版を優先（より「軍事級」であるため）し、マージする。

## 3. Directory Restructuring (The Body)

```
Forge/
├── .agent/                 ← Antigravity設定
├── GEMINI.md               ← 統合された脳
├── constitution/           ← dev-rules/constitution を移動 (法典)
├── library/                ← 統合された筋肉 (perceive, think...)
│   ├── modules/            ← 旧dev-rulesモジュール (ID管理)
│   └── templates/          ← Forgeテンプレート
├── docs/                   ← マニュアル類
└── design/                 ← 実験場 (prompt-lang)
```

## Execution Steps

1. **Move Constitution**: `bible/dev-rules/constitution` -> `Forge/constitution`
2. **Merge GEMINI.md**: Create new Hybrid GEMINI.md
3. **Migrate Prompts**: `bible/dev-rules/prompts/*` -> `Forge/library/`
4. **Cleanup**: Remove `bible/` folder (完全に消化したため不要)

This transforms Forge into a **Titanium-Class Prompt Engineering Platform**.
