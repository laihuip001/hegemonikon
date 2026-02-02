# Intent Recognition RCA: Workflow Execution Heuristics (2026-01-29)

## 1. Incident Overview

**Incident**: During the 2026-01-29 session, a request to use the `/sop` workflow for a specific inquiry was misinterpreted by the assistant as a request to *analyze the optimality* of the `/sop` template, rather than *executing* it.
**Result**: The user received a meta-report on the template instead of the intended research request artifact.

## 2. Five Whys Analysis

- **Why 1**: Why did the assistant not generate the research request?
  - *Answer*: It prioritized the evaluation of the template's "optimality" mention in the user prompt over the execution trigger.
- **Why 2**: Why did it prioritize analysis over execution?
  - *Answer*: The presence of the question "Is it optimal?" triggered a "Meta-Analysis" persona rather than a "Workflow Executor" persona.
- **Why 3**: Why did the presence of `/sop` not override the analysis trigger?
  - *Answer*: The assistant lacked a clear heuristic that `/workflow_name` signifies a mandatory execution intent regardless of accompanying questions.
- **Why 4**: Why was this intent ambiguous?
  - *Answer*: The user included both a question about the template and the workflow name twice. The assistant failed to recognize the "1st: Question, 2nd: Execution" switch.
- **Why 5 (Root Cause)**: The assistant's internal instruction set did not explicitly mandate "Execution-by-Default" for workflow triggers.

To prevent recurrence, the following rule is established and codified as **Rule E6 Workflow Execution Priority** in the Hegemonikón core rules (`.agent/rules/hegemonikon.md`):

> **Rule [EXEC-01 / E6]**: Whenever a workflow name (e.g., `/sop`, `/noe`, `/zet`) is provided in the user request, the **primary intent** is execution of that workflow. If the prompt contains meta-questions about the workflow itself, the assistant should perform the execution *first* or *as part of* the response, never *instead of* the execution. If truly ambiguous, the assistant must confirm intent before defaulting to pure analysis.

## 4. Operational Impact

- **Reliability**: Reduces "Looping" or "Stalling" where the assistant talks about doing work rather than doing it.
- **User Trust**: Ensures that specific workflow commands act as canonical triggers for action.

---
*Created: 2026-01-29*
*Reference: /why RCA session (9cb3717d-7407-4d8e-a8d7-aefc3b31f3e0)*
