# Mode: unit

Generate pytest tests for the application source and run them. Report the pass
rate honestly.

## Scope

Source under `app/`. **`app/fares.py` is the priority target** - cover it first
and most thoroughly (every public function, boundary values, error paths,
rounding and currency edges) before spending effort elsewhere. Then cover the
remaining modules under `app/` in rough order of how much logic they hold.

Generated unit tests are a repo deliverable. They live in the application repo
at `tests/unit/`, mirroring the source layout: `app/fares.py` ->
`tests/unit/test_fares.py`, `app/billing/rates.py` ->
`tests/unit/billing/test_rates.py`. Clearance still never edits `app/`.

## Procedure

1. Create `tests/unit/` and `tests/__init__.py` if they are missing (plus
   `__init__.py` in any subpackage you add under `tests/unit/`). Create
   `.clearance/findings/` too.
2. Read each target source file before writing tests for it. Test the behavior
   that is actually there - do not test an imagined API.
3. **Never overwrite an existing test file.** If `tests/unit/test_fares.py`
   already exists, read it, work out which cases it covers, and *add* the
   missing ones to it. Preserve every existing test, its name, and its
   assertions - append, do not rewrite. The same rule holds for any other
   pre-existing file in `tests/unit/`. Match the file's existing style,
   imports, and fixtures.
4. Run pytest from the **repo root**, e.g.
   `python -m pytest tests/unit -q --tb=short`. Imports of `app.*` resolve from
   the repo root; add a `conftest.py` only if they do not.
5. **Two retries on import or syntax failure.** If a test file fails to import
   or does not compile, you may fix and rerun it at most twice. After the second
   retry it stays broken - leave it on disk, count it as never compiled, and
   record a finding. Do not delete a broken file to improve the numbers. If the
   broken file is one you added cases to, revert your additions rather than
   leaving a pre-existing file uncollectable.

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
actual security defect. Findings always go to `.clearance/findings/unit.json` -
never into the repo alongside the tests. Write `[]` if nothing was found.
Always write the file.
