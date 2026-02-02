# Active Projects System: Monitoring & Alerts

> **Implementation Date**: 2026-02-01
> **Integration**: `/boot` Step 17.5

## 1. Data Schema (`projects.yaml`)

The central registry uses a dictionary of projects keyed by a unique identifier.

```yaml
projects:
  dendron:
    name: "Dendron"
    description: "存在証明 (Existence Proof) システム"
    path: "mekhane/dendron/"
    status: "mvp_complete"
    phase: "運用準備完了"
    priority: "high"
    updated: "2026-02-01"
    next_action: "git push で GitHub Actions 動作確認"
```

## 2. Project Metadata (`PROJECT.md`)

Every registered project must maintain a `PROJECT.md` in its `path`. The system verifies the existence of this file as a baseline for visibility.

### Required Frontmatter
```yaml
---
name: Dendron
status: mvp_complete
phase: 運用準備完了
updated: 2026-02-01
next_action: git push で GitHub Actions 動作確認
---
```

## 3. Freshness Alert Thresholds

The `/boot` sequence calculates the "staleness" of each project based on the `updated` field.

| Staleness | Icon | Level | Meaning |
|:----------|:-----|:------|:--------|
| < 7 Days  | -    | Normal | Active development. |
| 7-20 Days | ⚠️   | Warning | Project velocity is dropping. |
| 21+ Days  | 🔴   | Critical | Project is potentially stalled or abandoned. |

## 4. Priority Ordering

Projects are displayed in `/boot` ordered by priority (High > Medium > Low) to ensure the most critical work is seen first, even if it is stable.

## 5. Automation Strategy

- **Detection**: The `/boot` script (Phase 6, Step 17.5) performs the check.
- **Remediation**: If a project becomes 🔴 Critical, the AI should prompt the Creator to either update the status to `stable`, archive the code, or set a new `next_action`.
