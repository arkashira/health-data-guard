# STORIES.md – Health Data Guard

## Overview
Health Data Guard (HDG) is a runtime integration layer that enforces data‑handling policies for health‑care workloads running in a Kubernetes cluster. It intercepts pod creation, monitors data‑flow APIs, and validates compliance against a central policy store before allowing traffic. The following backlog is organized into **Epics** that map to the MVP and subsequent releases.

---

## EPIC 1 – Core Policy Enforcement Engine (MVP)

| # | User Story | Acceptance Criteria |
|---|------------|----------------------|
| 1 | **As a Kubernetes cluster admin, I want HDG to automatically load policies from a remote policy store, so that the cluster always enforces the latest compliance rules without manual updates.** | - HDG reads `policyStoreUrl` from Helm values at startup.<br>- Supports HTTP(S) GET with optional Bearer token (configurable via secret).<br>- Policies are cached locally and refreshed every **N** minutes (default 5).<br>- On refresh failure, HDG continues using the last‑known good policy and logs a warning. |
| 2 | **As a DevOps engineer, I want HDG to reject pod creation that violates a policy, so that non‑compliant workloads never run.** | - HDG registers a validating admission webhook.<br>- When a pod creation request is received, HDG evaluates the pod spec against loaded policies.<br>- If any rule fails, the webhook returns `deny` with a clear error message containing the rule ID and description.<br>- Successful pods receive a `allow` response. |
| 3 | **As a security auditor, I need HDG to emit structured audit logs for every policy decision, so that we can trace compliance over time.** | - Logs are emitted in JSON to stdout (captured by Kubernetes logging).<br>- Each log entry includes: timestamp, request UID, pod name/namespace, evaluated policy IDs, decision (`allow`/`deny`), and reason.<br>- Log level is configurable (info/debug). |
| 4 | **As a platform engineer, I want HDG to be deployable via Helm with sensible defaults, so that installation is repeatable and CI‑friendly.** | - Helm chart packages the Docker image, RBAC (ServiceAccount, Role, RoleBinding), and the validating webhook configuration.<br>- `values.yaml` includes defaults for `policyStoreUrl`, `refreshInterval`, `logLevel`, and TLS secret name.<br>- `helm install` succeeds on a fresh cluster (tested on v1.27+). |
| 5 | **As a developer, I want HDG to expose a health‑check endpoint, so that Kubernetes can automatically restart unhealthy pods.** | - HTTP `/healthz` returns 200 when the webhook server is listening and the policy cache is loaded.<br>- Returns 500 if the policy store cannot be reached for more than two consecutive refresh attempts. |
| 6 | **As a compliance officer, I need a way to view the currently active policy set from within the cluster, so that I can verify what rules are enforced.** | - `kubectl exec` into the HDG pod and run `hdgctl policies list` (CLI bundled in the image).<br>- Output is a pretty‑printed JSON array of policy IDs and descriptions. |
| 7 | **As a CI pipeline, I want HDG to run unit tests against a mock policy store, so that we can validate behavior before release.** | - Repository includes a `make test` target that spins up a local HTTP server serving fixture policies.<br>- Tests cover loading, refresh, admission decision, and logging. |
| 8 | **As a Kubernetes operator, I want HDG to support graceful shutdown, so that ongoing admission requests are not dropped during upgrades.** | - On SIGTERM, HDG stops accepting new webhook calls, finishes in‑flight requests, then exits with code 0.<br>- Helm upgrade uses `--wait` and observes the `/healthz` endpoint before completing. |

---

## EPIC 2 – Advanced Policy Features (Post‑MVP)

| # | User Story | Acceptance Criteria |
|---|------------|----------------------|
| 9 | **As a policy author, I want to define conditional rules based on pod labels and annotations, so that policies can be scoped to specific workloads.** | - Policy schema includes optional `matchLabels` and `matchAnnotations` fields.<br>- HDG evaluates these selectors before applying rule logic.<br>- Unit tests verify correct scoping. |
| 10 | **As a data‑privacy officer, I need HDG to block egress traffic from pods that lack proper encryption annotations, so that data is never sent unencrypted.** | - New rule type `requireEncryption` checks pod annotations `healthguard.io/encrypt=true`.<br>- If missing, admission is denied with a message referencing the rule ID. |
| 11 | **As a security team, I want HDG to integrate with OPA for complex policy expressions, so that we can reuse existing Rego policies.** | - HDG can optionally load a Rego bundle from the policy store.<br>- When enabled, HDG forwards the admission request JSON to OPA’s REST API and respects its decision.<br>- Configuration flag `useOPA` toggles this mode. |
| 12 | **As a platform owner, I want HDG to expose Prometheus metrics, so that we can monitor enforcement activity.** | - `/metrics` endpoint provides counters: `hdg_admission_requests_total`, `hdg_admission_denied_total`, `hdg_policy_refresh_success`, `hdg_policy_refresh_failure`.<br>- Metrics are labelled by `policy_id` and `namespace`. |
| 13 | **As a compliance auditor, I need HDG to retain a configurable audit log retention period, so that we meet data‑retention policies.** | - Helm value `auditLogRetentionDays` controls log rotation via a side‑car `logrotate` container.<br>- Logs older than the configured days are automatically deleted. |
| 14 | **As a DevSecOps engineer, I want HDG to support a dry‑run mode, so that we can test new policies without impacting production workloads.** | - Helm flag `dryRun=true` makes the webhook always return `allow` but still logs the decision that *would* have been made.<br>- Dry‑run mode is clearly indicated in the pod’s logs. |
| 15 | **As a Kubernetes operator, I want HDG to automatically reload TLS certificates from a Kubernetes secret, so that certificate rotation does not require pod restarts.** | - HDG watches the secret referenced by `tlsSecretName` and reloads the cert/key on change (using inotify or the Kubernetes watch API).<br>- No downtime observed during rotation. |

---

## Prioritization & Release Plan

| Release | Epics Included | Stories Delivered |
|---------|----------------|-------------------|
| **v1.0 (MVP)** | EPIC 1 | 1‑8 |
| **v1.1** | EPIC 2 (selected) | 9‑12 |
| **v1.2** | EPIC 2 (remaining) | 13‑15 |

Stories are ordered to deliver a shippable, compliant product at each milestone while keeping the codebase testable and observable.
