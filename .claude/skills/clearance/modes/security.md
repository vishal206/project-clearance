# Mode: security

Run the scanners, then audit the deployment manifests by reading them.

Read `.clearance/profile.json` first (build it per `detection.md` if absent) for
`source_dirs`, `deploy_manifests`, and `ui.base_url`.

## Scans

Run each of the skill's own `scripts/`, passing the profile values they need -
the base URL to probe, the source dirs to scan:

1. `scripts/probe.py` - live probing of the running app at `ui.base_url`.
2. `scripts/scan_secrets.py` - secrets in source and config.
3. `scripts/scan_logs.py` - sensitive data in logs.

If a script is missing or exits non-zero, do not silently skip it: record an
`info` finding naming the script and what happened, so `report` can say the
coverage was partial. The same goes for a probe that had no running app.

## Deployment manifest audit

Read every path in `deploy_manifests` directly - do not shell out to a scanner
for this. An empty list means no deployment config was found: record that as an
`info` finding and skip this section rather than inventing a path.

Pick the checklist that fits what you actually found. For Kubernetes manifests
and Helm charts, evaluate against the **OWASP Kubernetes Top 10** and check at
minimum:

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

For a Dockerfile or Compose file, check the equivalents: running as root, a
`:latest` or unpinned base image, secrets in `ENV` or build args, bind-mounting
the Docker socket, published ports that should be internal, and `privileged`.
For Terraform, check public ingress, unencrypted storage, over-broad IAM, and
hardcoded credentials.

For each violation write **one sentence of risk** - what an attacker gets from
it, in plain language, not a restatement of the setting.

## Findings

Write `.clearance/findings/security.json` - a JSON array of
`{id, severity, title, evidence, owasp}`. `evidence` is the scanner output line
or the manifest field and its value, with a file path and line reference;
`owasp` is the OWASP identifier (`K01`-`K10` for a Kubernetes manifest, the
relevant `A0x` for app findings, `null` where no category fits).
Severity reflects exploitability in this app, not a generic checklist rating.
Write `[]` if nothing was found. Always write the file.
