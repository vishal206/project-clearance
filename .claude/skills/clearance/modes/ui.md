# Mode: ui

Conditional mode. Check `.clearance/tests/ui/` first and take exactly one of the
two branches below.

## Branch A - BOOTSTRAP (`.clearance/tests/ui/` does not exist)

There is no suite yet, so build one. Do **not** heal anything in this branch.

1. Determine the base URL (ask, or take it from app config / README) and make
   sure the app is running.
2. Crawl from the base URL. Discover and record: pages reachable by link, forms
   and their fields, links, and API routes visible in the source or called by
   the pages. Stay on the app's own origin.
3. Generate a Playwright suite into `.clearance/tests/ui/` covering the
   discovered surface - page loads, form submits with valid and invalid input,
   navigation. Prefer `get_by_role` and `get_by_test_id` locators from the
   start.
4. Write `.clearance/baseline.json`: the page structure observed during the
   crawl - per URL, the elements the tests target with their roles, accessible
   names, test ids, and enough surrounding structure to re-identify them later.
5. Run the suite **once**.
6. Report as **BOOTSTRAP**. The first run establishes the baseline; its failures
   are observations, not gate failures.

## Branch B - GATE RUN (`.clearance/tests/ui/` exists)

The suite is the gate. **Never regenerate it.** Never add or delete tests, never
weaken an assertion.

1. Run the suite.
2. On a **locator failure** (element not found / not visible / strict-mode
   violation - not an assertion failure about behavior):
   a. Run `scripts/snapshot.py` to capture the current page structure.
   b. Compare it against `.clearance/baseline.json`.
   c. Identify which element the test intended to target.
   d. Rewrite only that locator, preferring `get_by_role`, then
      `get_by_test_id`. Avoid brittle CSS/XPath and nth-child chains.
   e. Rerun **once**.
3. **If uncertain which element was intended, do not edit.** Flag it for human
   review as a finding. An ambiguous match, a plausible-but-different element,
   or a page whose structure changed beyond recognition are all "uncertain".
4. An assertion failure about behavior is a real failure. Never heal it.

## Healing log

Log every heal attempt, healed or not, and carry it into the findings file so
`report` can render it. Per entry: test and line, old locator, new locator,
reasoning for believing they are the same element, and the rerun outcome.

## Findings

Write `.clearance/findings/ui.json` - a JSON array of
`{id, severity, title, evidence, owasp}`. Include failing tests, locators
flagged for review (uncertain, unhealed), heals that were applied, and for a
bootstrap run one `info` finding stating that this was a BOOTSTRAP run so
`report` can withhold a verdict. `owasp` is normally `null`. Write `[]` if
nothing was found. Always write the file.
