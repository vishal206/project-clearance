# Mode: security

Run the scanners, then audit the Kubernetes manifest by reading it.

## Scans

Run each and capture its output:

1. `scripts/probe.py` - live probing of the running app.
2. `scripts/scan_secrets.py` - secrets in source and config.
3. `scripts/scan_logs.py` - sensitive data in logs.

If a script is missing or exits non-zero, do not silently skip it: record an
`info` finding naming the script and what happened, so `report` can say the
coverage was partial.

## Kubernetes audit

Read `k8s/deployment.yaml` directly - do not shell out to a scanner for this.
Evaluate it against the **OWASP Kubernetes Top 10** and check at minimum:

- K01 Insecure workload configurations - `privileged`, `runAsRoot`,
  `allowPrivilegeEscalation`, missing `readOnlyRootFilesystem`, dropped caps
- K02 Supply chain vulnerabilities - unpinned or `:latest` images, no digest
- K03 Overly permissive RBAC - service account binding, `automountServiceAccountToken`
- K04 Lack of centralized policy enforcement
- K05 Inadequate logging and monitoring
- K06 Broken authentication
- K07 Missing network segmentation controls - `hostNetwork`, no NetworkPolicy
- K08 Secrets management failures - secrets as plain env vars or literals
- K09 Misconfigured cluster components - `hostPID`, `hostIPC`, host path mounts
- K10 Outdated and vulnerable components

For each violation write **one sentence of risk** - what an attacker gets from
it, in plain language, not a restatement of the setting.

## Findings

Write `.clearance/findings/security.json` - a JSON array of
`{id, severity, title, evidence, owasp}`. `evidence` is the scanner output line
or the manifest field and its value with a line reference; `owasp` is the OWASP
identifier (`K01`-`K10` for the manifest, the relevant `A0x` for app findings).
Severity reflects exploitability in this app, not a generic checklist rating.
Write `[]` if nothing was found. Always write the file.
