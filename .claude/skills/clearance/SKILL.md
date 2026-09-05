---
name: clearance
description: QA release gate with modes - generates and runs unit tests, drives a live browser against a self-healing UI spec, runs security scans, and merges findings into a release verdict. Use when asked to run clearance, gate a release, or check whether a build is cleared for departure.
---

# Clearance

A release gate. Each mode produces findings; `report` turns them into a verdict.

## The mode argument
Read the argument after `/clearance`. Match one of `unit`, `ui`, `security`,
`report`. If it is empty or unrecognized, run the **full run**: `unit` -> `ui`
-> `security` -> `report`, each to completion before the next. An unrecognized
argument is a full run plus a note saying so.

## Project detection

Clearance assumes nothing about the stack. Before any mode works, read
`.clearance/profile.json`; if absent, follow `detection.md` to build it. Every
path, runner, and command comes from that profile, never from a name hardcoded
here.

## Hard constraint

**Clearance keeps no UI test code anywhere.** The UI gate is a declarative spec
under `.clearance/`; its browser driver is built per run in the scratchpad and
discarded. Findings, baseline, and report stay in `.clearance/` too. Generated
unit tests are the one repo deliverable, written to the project's own test
location (`unit.test_dir`). Source is read-only to all modes.

## State contract

Fixed paths. Do not invent others.
```
.clearance/findings/unit.json       unit mode findings
.clearance/findings/ui.json         ui mode findings
.clearance/findings/security.json   security mode findings
<unit.test_dir>/                    generated unit tests (repo deliverable)
.clearance/profile.json             detected project profile
.clearance/ui-spec.json             the UI gate, as data - never test code
.clearance/baseline.json            page structure from the last ui run
.clearance/report.html              final report
```
Every mode writes its findings file as a JSON array of objects shaped
`{id, severity, title, evidence, owasp}`, where `severity` is one of
`critical|high|medium|low|info` and `owasp` is the relevant OWASP identifier or
`null`. A mode that finds nothing still writes `[]` - an absent file means the
mode has not run, and `report` says so explicitly.

## Modes

| Mode       | File                | What it does                                           |
| ---------- | ------------------- | ------------------------------------------------------ |
| `unit`     | `modes/unit.md`     | Generate and run unit tests for the detected sources   |
| `ui`       | `modes/ui.md`       | Drive a live browser against the UI spec, self-heal    |
| `security` | `modes/security.md` | Run the scans, audit the detected deploy manifests     |
| `report`   | `modes/report.md`   | Merge findings into `.clearance/report.html` + verdict |

Read the mode file and follow it exactly; for a full run, read each in turn.
