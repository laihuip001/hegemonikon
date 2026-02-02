# LOGIC_GATES Reference

**Source:** OMEGA v8.0.1

ハードコードされた意思決定ロジック。曖昧な判断を排除するための決定木集。

---

## 1. Speed vs Quality

```
┌─────────────────────────────────────────┐
│           SPEED vs QUALITY              │
└─────────────────────────────────────────┘
         │
         ▼
    ┌─────────┐
    │deadline │
    │ < 24h?  │
    └────┬────┘
         │
    ┌────┴────┐
    │         │
   YES        NO
    │         │
    ▼         ▼
┌───────┐ ┌───────────┐
│SPEED  │ │ deadline  │
│Mode   │ │ < 1 week? │
│95% OK │ └─────┬─────┘
└───────┘       │
           ┌────┴────┐
           │         │
          YES        NO
           │         │
           ▼         ▼
      ┌───────┐ ┌─────────┐
      │BALANCE│ │QUALITY  │
      │Mode   │ │Mode     │
      │98% OK │ │100% Aim │
      └───────┘ └─────────┘
```

**Implementation:**
```python
def speed_vs_quality(deadline_hours):
    if deadline_hours < 24:
        return "SPEED", 0.95  # 95% correctness acceptable
    elif deadline_hours < 168:  # 1 week
        return "BALANCE", 0.98
    else:
        return "QUALITY", 1.00
```

---

## 2. Security vs Usability

```
┌─────────────────────────────────────────┐
│        SECURITY vs USABILITY            │
└─────────────────────────────────────────┘
         │
         ▼
    ┌──────────┐
    │handles   │
    │PII/Auth? │
    └────┬─────┘
         │
    ┌────┴────┐
    │         │
   YES        NO
    │         │
    ▼         ▼
┌──────────┐  ┌──────────┐
│SECURITY  │  │user      │
│WINS      │  │facing?   │
│Always    │  └────┬─────┘
└──────────┘       │
              ┌────┴────┐
              │         │
             YES        NO
              │         │
              ▼         ▼
         ┌─────────┐ ┌─────────┐
         │USABILITY│ │INTERNAL │
         │Priority │ │Flexible │
         └─────────┘ └─────────┘
```

**Decision Matrix:**
| PII/Auth | User-Facing | Decision |
|:---:|:---:|:---|
| Yes | - | Security > Usability (No compromise) |
| No | Yes | Usability > Security (UX priority) |
| No | No | Balanced (Internal tools) |

---

## 3. Refactor vs Rewrite

```
┌─────────────────────────────────────────┐
│          REFACTOR vs REWRITE            │
└─────────────────────────────────────────┘
         │
         ▼
    ┌───────────┐
    │codebase   │
    │age > 5y?  │
    └─────┬─────┘
          │
    ┌─────┴─────┐
    │           │
   YES          NO
    │           │
    ▼           ▼
┌──────────┐ ┌───────────┐
│test      │ │tech_debt  │
│coverage  │ │ratio > 40%│
│< 30%?    │ └─────┬─────┘
└────┬─────┘       │
     │        ┌────┴────┐
┌────┴────┐   │         │
│         │  YES        NO
YES       NO  │         │
│         │   ▼         ▼
▼         ▼  ┌───────┐ ┌─────┐
┌───────┐ ┌──────────┐ │Incr-│ │KEEP │
│REWRITE│ │REWRITE   │ │ement│ │as-is│
│Advised│ │Consider  │ │Refac│ └─────┘
└───────┘ └──────────┘ └─────┘
```

**Scoring System:**
```python
def refactor_vs_rewrite(age_years, test_coverage, tech_debt_ratio):
    score = 0
    
    if age_years > 5:
        score += 2
    elif age_years > 3:
        score += 1
    
    if test_coverage < 30:
        score += 2
    elif test_coverage < 60:
        score += 1
    
    if tech_debt_ratio > 40:
        score += 1
    
    if score >= 4:
        return "REWRITE"
    elif score >= 2:
        return "INCREMENTAL_REFACTOR"
    else:
        return "MAINTAIN"
```

---

## 4. Undefined Variable Handler

```
┌─────────────────────────────────────────┐
│       UNDEFINED VARIABLE HANDLER        │
└─────────────────────────────────────────┘
         │
         ▼
    ┌───────────┐
    │variable   │
    │critical?  │
    └─────┬─────┘
          │
    ┌─────┴─────┐
    │           │
   YES          NO
    │           │
    ▼           ▼
┌──────────┐ ┌───────────┐
│HALT      │ │can infer  │
│Ask user  │ │from SOTA? │
│MANDATORY │ └─────┬─────┘
└──────────┘       │
              ┌────┴────┐
              │         │
             YES        NO
              │         │
              ▼         ▼
         ┌─────────┐ ┌─────────────┐
         │ASSUME   │ │ASSUME       │
         │SOTA     │ │WORST_CASE   │
         │Display  │ │Display      │
         └─────────┘ └─────────────┘
```

**Critical Variables (Always Ask):**
- Budget / Cost constraints
- Security requirements
- Compliance requirements
- Target users / audience
- Deadline (if affects architecture)

**Inferable Variables (SOTA Default):**
- Language version → Latest stable
- Framework → Most popular for use case
- Database → PostgreSQL (default)
- Cloud provider → Context-dependent

---

## 5. Testing Mandate

```
┌─────────────────────────────────────────┐
│           TESTING MANDATE               │
└─────────────────────────────────────────┘
         │
         ▼
    ┌───────────┐
    │code type? │
    └─────┬─────┘
          │
    ┌─────┼─────┬─────────┐
    │     │     │         │
  CORE  API  INFRA      UI
    │     │     │         │
    ▼     ▼     ▼         ▼
┌─────┐┌─────┐┌─────┐┌───────┐
│Unit ││Inte-││Infra││E2E    │
│90%+ ││gra- ││Plan ││Happy  │
│     ││tion ││+ Dry││Path   │
│     ││100% ││Run  ││Only   │
└─────┘└─────┘└─────┘└───────┘
```

**Minimum Coverage by Type:**
| Code Type | Test Type | Minimum Coverage |
|:---|:---|:---|
| Core Business Logic | Unit Tests | 90% |
| API Endpoints | Integration Tests | 100% |
| Infrastructure | Plan + Dry-run | Required |
| UI Components | E2E (Happy Path) | Critical flows |
| Data Migrations | Rollback Test | Required |

---

## 6. Dependency Decision

```
┌─────────────────────────────────────────┐
│         DEPENDENCY DECISION             │
└─────────────────────────────────────────┘
         │
         ▼
    ┌────────────┐
    │build or    │
    │buy/import? │
    └─────┬──────┘
          │
    ┌─────┴─────┐
    │           │
  BUILD       IMPORT
    │           │
    ▼           ▼
┌──────────┐ ┌───────────┐
│core      │ │maintained?│
│competency│ │(activity  │
│?         │ │< 6 months)│
└────┬─────┘ └─────┬─────┘
     │             │
┌────┴────┐   ┌────┴────┐
│         │   │         │
YES       NO YES        NO
│         │   │         │
▼         ▼   ▼         ▼
┌─────┐ ┌───┐┌─────┐┌──────┐
│BUILD│ │RE-││USE  ││FORK  │
│Own  │ │USE││with ││or    │
│     │ │   ││lock ││BUILD │
└─────┘ └───┘└─────┘└──────┘
```

**Decision Criteria:**
```python
def dependency_decision(is_core_competency, last_commit_days, stars, issues_open):
    if is_core_competency:
        return "BUILD"
    
    if last_commit_days > 180:  # 6 months
        if stars > 1000 and issues_open < 50:
            return "FORK_AND_MAINTAIN"
        return "BUILD_ALTERNATIVE"
    
    return "USE_WITH_LOCKFILE"
```

---

## 7. Error Handling Strategy

```
┌─────────────────────────────────────────┐
│       ERROR HANDLING STRATEGY           │
└─────────────────────────────────────────┘
         │
         ▼
    ┌───────────┐
    │error      │
    │recoverable│
    │?          │
    └─────┬─────┘
          │
    ┌─────┴─────┐
    │           │
   YES          NO
    │           │
    ▼           ▼
┌──────────┐ ┌───────────┐
│retry     │ │user       │
│worthwhile│ │facing?    │
│?         │ └─────┬─────┘
└────┬─────┘       │
     │        ┌────┴────┐
┌────┴────┐   │         │
│         │  YES        NO
YES       NO  │         │
│         │   ▼         ▼
▼         ▼  ┌───────┐ ┌─────────┐
┌───────┐ ┌──────┐  │GRACEFUL│ │LOG      │
│RETRY  │ │CIRCUIT│  │DEGRADE │ │+ ALERT  │
│+Backof│ │BREAKER│  │+ ERROR │ │+ CRASH  │
└───────┘ └──────┘  │MESSAGE │ └─────────┘
                    └───────┘
```

---

## 8. API Versioning Strategy

```
┌─────────────────────────────────────────┐
│       API VERSIONING STRATEGY           │
└─────────────────────────────────────────┘
         │
         ▼
    ┌───────────┐
    │breaking   │
    │change?    │
    └─────┬─────┘
          │
    ┌─────┴─────┐
    │           │
   YES          NO
    │           │
    ▼           ▼
┌──────────┐ ┌───────────┐
│consumers │ │ship       │
│> 10?     │ │directly   │
└────┬─────┘ └───────────┘
     │
┌────┴────┐
│         │
YES       NO
│         │
▼         ▼
┌─────────┐ ┌──────────┐
│NEW      │ │DEPRECATE │
│VERSION  │ │+ SUNSET  │
│/v2/     │ │TIMELINE  │
└─────────┘ └──────────┘
```

---

## 9. Logging Decision

```
┌─────────────────────────────────────────┐
│          LOGGING DECISION               │
└─────────────────────────────────────────┘

Log Level Selection:
┌─────────────────────────────────────────┐
│ DEBUG: Development only, verbose        │
│ INFO:  Normal operations, key events    │
│ WARN:  Recoverable issues               │
│ ERROR: Failures requiring attention     │
│ FATAL: System cannot continue           │
└─────────────────────────────────────────┘

What to Log:
✓ Request ID (correlation)
✓ Timestamp (ISO 8601 UTC)
✓ Duration (for perf tracking)
✓ Outcome (success/failure)
✗ PII (NEVER)
✗ Secrets (NEVER)
✗ Full request body (unless DEBUG)
```

---

## 10. Caching Decision

```
┌─────────────────────────────────────────┐
│          CACHING DECISION               │
└─────────────────────────────────────────┘
         │
         ▼
    ┌───────────┐
    │data       │
    │changes    │
    │frequency? │
    └─────┬─────┘
          │
    ┌─────┼─────┬─────────┐
    │     │     │         │
 REAL  MINUTE  HOUR      DAY+
 TIME    │     │         │
    │     │     │         │
    ▼     ▼     ▼         ▼
┌─────┐┌─────┐┌─────┐┌───────┐
│NO   ││In-  ││Redis││CDN    │
│CACHE││Proc ││/Mem-││Edge   │
│     ││Cache││cache││Cache  │
│     ││TTL: ││TTL: ││TTL:   │
│     ││30s  ││5min ││1hr+   │
└─────┘└─────┘└─────┘└───────┘
```

**Invalidation Strategy:**
| Pattern | Use When |
|:---|:---|
| TTL-based | Data staleness acceptable |
| Event-driven | Consistency critical |
| Write-through | Strong consistency needed |
| Cache-aside | Read-heavy workloads |

---

## Usage

```python
# Import decision gates
from logic_gates import (
    speed_vs_quality,
    security_vs_usability,
    refactor_vs_rewrite,
    undefined_var_handler,
    testing_mandate
)

# Apply in workflow
decision = speed_vs_quality(deadline_hours=48)
# Returns: ("BALANCE", 0.98)

coverage = testing_mandate("API")
# Returns: {"type": "integration", "minimum": 1.0}
```
