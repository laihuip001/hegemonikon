---
id: metacognition
title: Metacognition Checkpoints（自己評価チェックポイント）
applies_to: All LLM Agents
---

# Metacognition Checkpoints

> **効果**: タスク間での飛ばし行動を **62% 削減**
> **根拠**: [Zenn 2025-11-30](https://zenn.dev/shinpr_p/articles/43e55dfb1076ce)

---

## Self-Evaluation Checkpoints

**各フェーズの開始時に、以下を自問すること:**

```markdown
## Metacognition Checkpoint

Before proceeding, STOP and evaluate:

1. **What phase am I currently in?**
   → Phase [N]: [Phase Name]

2. **Have I read all required rule files for this phase?**
   → [x] .agent/rules/tasks/phase_N_*.md
   → [x] blockers satisfied

3. **Is my current action aligned with the phase goal?**
   → Goal: [Phase Goal]
   → Current Action: [What I'm about to do]
   → Aligned: [Yes/No]

4. **Are there any destructive operations?**
   → If yes, STOP and request confirmation
```

---

## Transition Gates

**フェーズ間の遷移時に、以下を確認すること:**

```markdown
## Phase Transition Gate

**From Phase [N] to Phase [N+1]**

### Prerequisites (blockers)
- [ ] Phase [N] outputs exist: [file1.md, file2.json]
- [ ] Phase [N] status: COMPLETED
- [ ] Human approval (if required): [Yes/N/A]

### If any prerequisite fails:
- STOP execution
- Report: "[PHASE N+1 BLOCKED] Reason: ..."
- Await human decision
```

---

## 5-Minute Interval Check

**長時間タスク中は 5 分ごとに:**

```markdown
## 5-Minute Self-Check

1. Am I still on track for Phase [N]?
2. Have I drifted from the original goal?
3. Is there anything I should ask the user about?
4. Have I skipped any middle sections? (Known limitation)
```

---

## Middle-Section Re-Read

> **Known Limitation**: LLM は文脈の中央部を飛ばす傾向がある (Lost-in-the-Middle)

**長文指示を読む際は:**

```markdown
## Middle Re-Read Protocol

1. Read entire document once
2. Identify middle sections (lines 20-80% of document)
3. Re-read middle sections explicitly
4. Log: "Middle re-read completed: [file] lines [start]-[end]"
```

---

## 実装例

```python
# エージェント実装時のチェックポイント呼び出し
def metacognition_checkpoint(phase: int, action: str):
    print(f"[Metacognition] Phase {phase}")
    print(f"[Metacognition] Action: {action}")
    
    # Check blockers
    if not check_blockers(phase):
        raise BlockedPhaseError(f"Phase {phase} blockers not satisfied")
    
    # Check for destructive operations
    if is_destructive(action):
        if not request_confirmation(action):
            raise ConfirmationRequiredError(f"User confirmation needed: {action}")
    
    return True
```

---

*参照: gemini_sop.md, destructive_ops.md*
