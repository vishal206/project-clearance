# Mode: unit

Generate unit tests for the application source in the project's own test
framework, run them, and report the pass rate honestly.

## Scope

Read `.clearance/profile.json` first (build it per `detection.md` if absent).
It supplies `source_dirs`, `priority_targets`, and the whole `unit` block -
runner, command, test directory, file naming. Take every path from there.

**Cover `priority_targets` first and most thoroughly** - every public function,
boundary values, error paths, and the numeric or state edges the code actually
has. That is where a gate earns its keep. Then work through the remaining
`source_dirs` in rough order of how much logic each module holds.

Generated unit tests are a repo deliverable. They go in the repo at
`unit.test_dir`, mirroring the source layout and the project's own naming
convention (`unit.file_pattern`): a module at `<src>/a/b.py` gets a test at the
matching path under the test dir. Clearance never edits application source.

## Procedure

1. Create `unit.test_dir` if missing, along with whatever the ecosystem needs
   to make it importable - `__init__.py` for a Python package tree, a
   `tsconfig`/`jest` path entry where the project uses one. Follow what the
   project already does; do not invent a layout. Create `.clearance/findings/`.
2. Read each target source file before writing tests for it. Test the behavior
   that is actually there - do not test an imagined API.
3. **Never overwrite an existing test file.** If the target file already
   exists, read it, work out which cases it covers, and *add* the missing ones.
   Preserve every existing test, its name, and its assertions - append, do not
   rewrite. Match the file's existing style, imports, and fixtures.
4. Run `unit.command` against `unit.test_dir` from the **repo root**, with the
   runner's terse and short-traceback flags. Resolve imports the way the
   project already does; add a bootstrap file only if they do not resolve.
5. **Two retries on import, compile, or syntax failure.** If a test file does
   not load, you may fix and rerun it at most twice. After the second
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
  estimated as the number of test cases written into those files)

State the estimate as an estimate. Never round a failure away.

## Findings

Write `.clearance/findings/unit.json` - a JSON array of
`{id, severity, title, evidence, owasp}`. Include:

- each failing test as a finding, `evidence` = the assertion and failure tail
- each file that never compiled, `severity` at least `high`
- a summary finding carrying the pass rate, `severity: "info"`

`owasp` is `null` for ordinary test failures; set it when a failure shows an
actual security defect. Findings always go to `.clearance/findings/unit.json` -
never into the repo alongside the tests. Also record an `info` finding for any
source area you could not cover and why (a runner dependency missing, a module
with no reachable entry point), so `report` can state the coverage gap. Write `[]` if nothing was found.
Always write the file.
