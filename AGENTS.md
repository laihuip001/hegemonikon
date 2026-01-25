# Hegemonikon Workspace Rules — 実験 B: Jules 最小化

## エージェント選択ルール（Claude 優先）

### グローバルポリシー

**IMPORTANT**: For ALL tasks including file operations:
- **ALWAYS prefer Claude** as the primary agent
- **NEVER delegate to Jules (Gemini)**
- Claude should handle ALL write_to_file operations directly
- Do NOT invoke any sub-agents or background agents

### プロンプト生成タスク

When the task involves generating prompts (*.prompt files):
- **REQUIRED**: Claude must generate directly, no delegation
- Do NOT use Gemini 3 Pro (Jules)
- Claude handles everything: design, generation, and review
- Follow the Prompt-Lang v2 specification at `docs/specs/prompt-lang-v2-spec.md`

### 実行の分離（なし）

```
ALL Tasks → Claude ONLY
NO delegation to Jules
NO background agents
```

---

## 実験フラグ

**EXPERIMENT_MODE**: jules_minimize
**EXPERIMENT_ID**: B

---

## プロジェクト固有のルール（維持）

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
