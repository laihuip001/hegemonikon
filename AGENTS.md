# Hegemonikon Workspace Rules

## エージェント選択ルール

### プロンプト生成タスク

When the task involves generating prompts (*.prompt files):
- **Prefer Gemini 3 Pro** for generation tasks
- **Use Claude** for design and review tasks
- **Follow** the Prompt-Lang v2 specification at `docs/specs/prompt-lang-v2-spec.md`

### プロンプト生成の具体的な指示

If asked to generate a prompt file:
1. Read the meta-prompt-generator Skill at `.agent/skills/utils/meta-prompt-generator/SKILL.md`
2. Follow the Phase 0-6 workflow
3. Use Prompt-Lang v2 format
4. Validate with the parser before completion

### タスク委譲

If a task is marked with `[DELEGATE:JULES]` or placed in `.ai/JULIUS_TASK.md`:
- Treat this as a background task
- Execute autonomously
- Report results via artifacts

---

## プロジェクト固有のルール

### ファイル配置

- Prompt files: `forge/prompt-lang/prompts/*.prompt`
- Skill files: `.agent/skills/*/SKILL.md`
- Documentation: `docs/`

### 言語

- All responses in **Japanese**
- Code comments in **English**
- Commit messages in **English**

---

## References

- Prompt-Lang v2 Spec: `docs/specs/prompt-lang-v2-spec.md`
- meta-prompt-generator Skill: `.agent/skills/utils/meta-prompt-generator/SKILL.md`
- jules-pe Skill: `.agent/skills/utils/jules-pe/SKILL.md`
