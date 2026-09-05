# Mode: report

Merge every findings file that exists into `.clearance/report.html` and state a
verdict.

## Inputs

`.clearance/findings/unit.json`, `ui.json`, `security.json`. Merge whatever is
present. Read `.clearance/profile.json` too, and name the detected stack,
runners, and targets in the report - a reader needs to know what was gated. A missing file means that mode has not been run - **say so explicitly
in the report**, both in the summary and as a row in a mode-status table. Never
treat a missing file as a clean result.

## Verdict

- **GROUNDED** if any `critical` or `high` finding exists in any merged file,
  **or** UI tests fail without a successful heal.
- **CLEARED FOR DEPARTURE** otherwise.
- **NO VERDICT** if the ui findings record a BOOTSTRAP run. A bootstrap run
  establishes the baseline and does not gate anything; say plainly that the UI
  UI spec was created on this run, that its results are a baseline rather than
  a gate, and that a second `/clearance ui` run is needed before a verdict is
  possible. NO VERDICT overrides the other two.

## Report contents

Write a single self-contained `.clearance/report.html` - inline CSS, no external
assets. In order:

1. **Verdict**, large and unmistakable, with a timestamp.
2. **One paragraph of plain language** explaining the verdict to someone who did
   not run the tests: what was checked, what went wrong, what it means for
   shipping. No jargon, no severity codes.
3. **Mode status table** - each mode: run / not run, findings count.
4. **Findings grouped by severity**, critical first. Per finding: id, title,
   evidence, OWASP identifier where present.
5. **Healing log** from the ui findings - old target, new target, reasoning,
   outcome; plus targets flagged for review and left unedited. Say "no heals
   were attempted" rather than omitting the section.
6. **Unit pass rate**, as recorded by unit mode, including tests that never
   compiled. Do not recompute it more favorably.
   Alongside it, the **coverage gaps** the modes recorded - source areas not
   tested, scans that did not run, manifests not found. A gate is only as good
   as what it looked at, and the reader must be able to see the edges.
7. **Ranked fix list** - what to fix first, ordered by severity then blast
   radius, one line of "why this first" each.

Report only what the findings files actually contain. Do not infer a passing
result from an absent file, and do not soften a verdict.
