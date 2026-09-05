# Mode: unit

Generate pytest tests for the application source and run them. Report the pass
rate honestly.

## Scope

Source under `app/`. **`app/fares.py` is the priority target** - cover it first
and most thoroughly (every public function, boundary values, error paths,
rounding and currency edges) before spending effort elsewhere. Then cover the
remaining modules under `app/` in rough order of how much logic they hold.

Tests are written into `.clearance/tests/unit/`, one test file per source file,
named `test_<module>.py`. Never write a test into the application repo, never
modify `app/`, and never touch an existing top-level `tests/` directory.

## Procedure

1. `mkdir -p .clearance/tests/unit .clearance/findings`.
2. Read each target source file before writing tests for it. Test the behavior
   that is actually there - do not test an imagined API.
3. Write the tests. Make imports work from `.clearance/tests/unit/` without
   editing the app: put the repo root on `sys.path` from a `conftest.py` inside
   `.clearance/tests/unit/`.
4. Run from that directory, e.g.
   `python -m pytest .clearance/tests/unit -q --tb=short`.
5. **Two retries on import or syntax failure.** If a test file fails to import
   or does not compile, you may fix and rerun it at most twice. After the second
   retry it stays broken - leave it on disk, count it as never compiled, and
   record a finding. Do not delete a broken file to improve the numbers.

## Honest pass rate

A test that never compiled is not a passing test and is not excluded from the
denominator. Report:

- tests collected, passed, failed, errored
- test files that never compiled, by name
- pass rate = passed / (collected + tests lost to files that never compiled,
  estimated as the number of test functions written into those files)

State the estimate as an estimate. Never round a failure away.

## Findings

Write `.clearance/findings/unit.json` - a JSON array of
`{id, severity, title, evidence, owasp}`. Include:

- each failing test as a finding, `evidence` = the assertion and traceback tail
- each file that never compiled, `severity` at least `high`
- a summary finding carrying the pass rate, `severity: "info"`

`owasp` is `null` for ordinary test failures; set it when a failure shows an
actual security defect. Write `[]` if nothing was found. Always write the file.
