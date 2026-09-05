---
name: clearance
description: QA release gate with modes - generates and runs unit tests, runs and self-heals a Playwright UI suite, runs security scans, and merges findings into a release verdict. Use when asked to run clearance, gate a release, or check whether a build is cleared for departure.
---

# Clearance

A release gate. Each mode produces findings; `report` turns them into a verdict.

## Parsing the mode argument

Read the argument after `/clearance`. Match one of `unit`, `ui`, `security`,
`report`. If the argument is empty or unrecognized, run the **full run**:
`unit` -> `ui` -> `security` -> `report`, in that order, each to completion
before the next. An unrecognized argument is a full run plus a note saying so.

## Hard constraint

**Clearance NEVER writes test code, fixtures, config, or output into the
application repo.** Everything Clearance creates lives under `.clearance/`.
Application source is read-only to every mode. If a mode seems to need a file
outside `.clearance/`, it does not - record a finding instead.

## State contract

Fixed paths. Do not invent others.

```
.clearance/findings/unit.json       unit mode findings
.clearance/findings/ui.json         ui mode findings
.clearance/findings/security.json   security mode findings
.clearance/tests/unit/              generated unit tests
.clearance/tests/ui/                the Playwright suite clearance owns
.clearance/baseline.json            page structure from the last ui run
.clearance/report.html              final report
```

Every mode writes its own findings file: a JSON array of objects shaped

```json
{"id": "", "severity": "critical|high|medium|low|info",
 "title": "", "evidence": "", "owasp": ""}
```

`owasp` is the relevant OWASP identifier, or `null`. A mode that finds nothing
still writes `[]` - an absent file means the mode has not run. `report` merges whatever exists and states explicitly which
modes have not been run.

## Modes

| Mode       | File                | What it does                                            |
| ---------- | ------------------- | ------------------------------------------------------- |
| `unit`     | `modes/unit.md`     | Generate and run pytest tests for `app/`                |
| `ui`       | `modes/ui.md`       | Bootstrap or gate-run the Playwright suite, self-heal   |
| `security` | `modes/security.md` | Run the probe/secret/log scans, audit `k8s/`            |
| `report`   | `modes/report.md`   | Merge findings into `.clearance/report.html` + verdict  |

Read the mode file and follow it exactly. For a full run, read each in turn.
