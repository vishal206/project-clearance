# Project detection

Clearance is project-agnostic. Nothing about a stack, a directory layout, or a
file name is assumed - it is detected once and recorded, then every mode reads
the record instead of re-guessing.

## The profile

`.clearance/profile.json` is the single source of truth for "what is this
project". Every mode's first step: if it exists, read it and use it. If it does
not, run the detection below and write it. Re-detect only when the user asks or
when a recorded path has disappeared.

Example profile for a Python web service - the keys are fixed, every value is
detected:

```json
{
  "language": "python",
  "source_dirs": ["app"],
  "priority_targets": ["app/fares.py"],
  "unit": {
    "runner": "pytest",
    "command": "python -m pytest",
    "test_dir": "tests/unit",
    "file_pattern": "test_<module>.py"
  },
  "ui": {
    "runner": "playwright-python",
    "base_url": "http://127.0.0.1:8000",
    "start_command": "python -m uvicorn app.main:app --port 8000",
    "ready_path": "/"
  },
  "deploy_manifests": ["k8s/deployment.yaml"],
  "notes": "how each value was determined"
}
```

Record how you determined each value in `notes`. A guess recorded as a guess is
usable; a guess recorded as a fact is not.

## How to detect

**Language and package manager** - from the manifest present at the repo root:
`pyproject.toml` / `setup.cfg` / `requirements.txt` (Python), `package.json`
(Node - read it for the real script names), `go.mod`, `Cargo.toml`, `pom.xml` /
`build.gradle`, `Gemfile`, `composer.json`, `*.csproj`. More than one means a
polyglot repo: record each with its subdirectory.

**Source dirs** - the package/module roots the manifest declares. Failing that,
the top-level directories holding source files, excluding tests, vendor,
`node_modules`, build output, and the virtualenv.

**Unit runner and test dir** - prefer what the project already uses, in this
order: an explicit config (`[tool.pytest.ini_options]`, `jest`/`vitest` config,
`go test` layout, `package.json` scripts); then the existing test directory's
convention; then the ecosystem default. Match the project's existing naming and
placement - `test/`, `tests/`, `spec/`, `__tests__/`, or Go's sibling
`_test.go`. **Never impose `tests/unit/` on a project that does not use it.**

**Priority targets** - the highest-risk business logic, since that is where a
gate earns its keep: money and pricing, auth and sessions, permissions, crypto,
and anything parsing untrusted input. Find it by name and by content, not by a
fixed filename. Record why each was chosen. If the user names a target, theirs
wins.

**UI runner, base URL, start command** - `ui.runner` is only the language the
per-run browser driver is written in: `playwright-python` where Playwright's
Python package is available, `playwright-node` otherwise. Clearance drives the
browser itself and does not adopt or run an existing e2e suite.

Take the base URL and start command from the project's README, Procfile,
Makefile, `docker-compose.yml`, or dev script. **Ask the user if the
base URL cannot be determined** - do not guess a port and report a dead app as a
failing suite.

**Deploy manifests** - anything deployment-shaped, wherever it lives: `k8s/`,
`deploy/`, `manifests/`, `charts/` (Helm), `kustomization.yaml`,
`docker-compose.yml`, `Dockerfile`, `*.tf`. Record the list; an empty list is a
valid finding, not an error.

## When detection fails

Record the gap as an `info` finding naming what could not be determined and
what was assumed, and carry on with the modes that do not depend on it. Never
fabricate a path, and never fall back to a value from another project.
