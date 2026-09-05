# Mode: ui

Drive a real browser against the running app. **Clearance does not keep a
Playwright test suite.** There are no test files to maintain, in this repo or
under `.clearance/` - the gate is a declarative spec, and the browser driver is
built fresh each run and thrown away.

Read `.clearance/profile.json` first (build it per `detection.md` if absent) for
`ui.base_url`, `ui.start_command`, and `ui.ready_path`.

## How a run works

1. Bring the app up with `ui.start_command`, wait for `ui.ready_path` to
   answer, and stop it when the mode ends. If it is already up on
   `ui.base_url`, use it and leave it running. **Never report failures when the
   app was never up** - that is an `info` finding about the environment.
2. Write a single-use Playwright driver to your scratchpad directory, never
   into the repo or `.clearance/`. It reads `.clearance/ui-spec.json`, walks
   the steps, and prints one JSON result per check: step id, pass/fail, what
   was expected, what was observed, and for a failure whether the locator
   resolved at all.
3. Execute it, parse the results, delete it. The next run builds a new one.

The driver is a mechanism, not an artifact. Never ask the user to keep it,
never reuse a stale copy, and never let it accumulate state between runs.

## The spec

`.clearance/ui-spec.json` is the gate: pages, flows, and expectations as data.
Roughly - keep the shape stable across runs:

```json
{"flows": [{"id": "search-valid", "page": "/search",
  "steps": [{"action": "fill", "target": {"by": "label", "value": "Origin"}, "with": "CDG"},
            {"action": "click", "target": {"by": "role", "role": "button", "name": "Search"}}],
  "expect": [{"check": "status", "value": 200},
             {"check": "visible", "target": {"by": "role", "role": "row"}}]}]}
```

Targets are addressed by `role`, `label`, or `test_id`. A CSS or XPath target
is a last resort and must carry a `why` field. Every expectation states what a
passing state looks like: an emptiness check alone (`count: 0`, "no error
shown") also passes on a crash or a 404, so pair it with the expected status or
a visible element.

## Branch A - BOOTSTRAP (no `.clearance/ui-spec.json`)

1. Confirm the app answers on `ui.base_url`.
2. Crawl from there with the browser. Record pages reachable by link, forms and
   their fields, links, and API routes the pages call. Stay on the app's origin.
3. Write `.clearance/ui-spec.json` covering that surface - page loads, form
   submits with valid and invalid input, navigation - and `.clearance/baseline.json`
   with the observed structure per URL: roles, accessible names, test ids, form
   fields, and enough surrounding context to re-identify an element later.
4. Run the spec once. Report as **BOOTSTRAP**: first-run results are
   observations, not gate failures. Do not heal.

## Branch B - GATE RUN (the spec exists)

The spec is the gate. **Never regenerate it**, never delete a flow, never
weaken an expectation to make a run pass.

1. Execute every flow.
2. On a **locator failure** (target not found, not visible, or ambiguous - not
   an expectation that failed on behavior):
   a. Capture the live page structure with the driver.
   b. Compare against `.clearance/baseline.json`.
   c. Identify which element the flow intended.
   d. Rewrite **only that target** in the spec, preferring `role`, then
      `test_id`, then `label`.
   e. Rerun that flow once.
3. **If uncertain which element was intended, do not edit.** Flag it for review.
   An ambiguous match, a plausible-but-different element, or a page changed
   beyond recognition are all "uncertain".
4. An expectation that fails on behavior is a real failure. Never heal it.

Healing edits data, never code - which is the point of keeping the gate
declarative. A heal is a one-line change to a target, reviewable in a diff.

## Healing log

Log every heal attempt, healed or not: flow and step id, old target, new
target, the reasoning for believing they are the same element, and the rerun
outcome. Carry it into the findings so `report` can render it.

## Findings

Write `.clearance/findings/ui.json` - a JSON array of
`{id, severity, title, evidence, owasp}`: failed expectations, targets flagged
for review, heals applied, and any flow that passes only by asserting absence
(a gate that cannot see a crash is itself a defect). On a bootstrap run include
one `info` finding saying so, so `report` withholds a verdict. `owasp` is
normally `null`. Write `[]` if nothing was found. Always write the file.
