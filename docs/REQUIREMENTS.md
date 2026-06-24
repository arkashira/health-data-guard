# REQUIREMENTS.md  

## 1. Overview  
Health Data Guard (HDG) is a runtime integration layer that enforces data‑handling policies for health‑care workloads running in a Kubernetes cluster. It intercepts pod creation, updates, and network traffic to ensure compliance with regulatory rules (e.g., HIPAA, GDPR) before resources are admitted or traffic is allowed.

The system is delivered as a container image (`health-data-guard:1.0.0`) and installed via a Helm chart. The chart must accept a `policyStoreUrl` value that points to a remote, read‑only JSON/REST policy store.

---

## 2. Functional Requirements  

| ID | Description |
|----|-------------|
| **FR‑1** | **Policy Retrieval** – On startup, HDG must fetch the complete policy set from the URL supplied via `policyStoreUrl`. The policies are JSON documents conforming to the **Health Policy Schema v1.0** (see Appendix A). |
| **FR‑2** | **Policy Caching & Refresh** – Cache policies locally in memory and refresh them every **15 minutes** (configurable via Helm value `policyRefreshInterval`). If the refresh fails, continue using the last‑known good cache and emit a warning event. |
| **FR‑3** | **Admission Control** – Implement a MutatingAdmissionWebhook that validates every pod spec against the loaded policies. If a pod violates a policy, the webhook must reject the creation with a detailed error message. |
| **FR‑4** | **Network Enforcement** – Deploy a sidecar proxy (based on **Envoy**) that inspects inbound/outbound traffic of pods labeled `health-data-guard=enabled`. The proxy must block any request that does not match an allowed data‑transfer rule in the policy set. |
| **FR‑5** | **Audit Logging** – Emit structured audit logs (JSON) for every admission decision and network block event to a configurable sink (`stdout` by default, optional `logstash` endpoint via Helm value `auditLogEndpoint`). Logs must include timestamp, pod UID, policy ID, decision, and request metadata. |
| **FR‑6** | **Policy Exception API** – Expose a REST endpoint (`/exceptions`) that allows an authorized admin to submit temporary exceptions (max 24 h). Exceptions are stored in an in‑memory store and must be persisted to a ConfigMap for crash recovery. |
| **FR‑7** | **RBAC Integration** – Enforce that only ServiceAccounts with the Kubernetes role `health-data-guard-admin` can call the Exception API or trigger a manual policy refresh (`/refresh`). |
| **FR‑8** | **Helm Configurability** – All operational parameters (policy URL, refresh interval, audit sink, exception TTL, log level) must be configurable via Helm values. The chart must generate the necessary `MutatingWebhookConfiguration`, `Deployment`, `Service`, and `ConfigMap`. |
| **FR‑9** | **Graceful Shutdown** – On SIGTERM, HDG must stop accepting new admission requests, finish processing in‑flight requests, flush audit logs, and deregister the webhook within 30 seconds. |
| **FR‑10** | **Metrics Export** – Expose Prometheus metrics on `/metrics` covering: request count, reject count, network block count, cache hit/miss, refresh latency, and exception count. |

---

## 3. Non‑Functional Requirements  

| ID | Requirement |
|----|-------------|
| **NFR‑1** | **Performance** – Admission webhook latency ≤ 50 ms for 95 th percentile of pod creation requests under a load of 200 req/s. |
| **NFR‑2** | **Scalability** – The Deployment must be horizontally scalable (default replica count = 2). The sidecar proxy must support connection pooling to handle ≥ 5 k concurrent TCP streams per pod. |
| **NFR‑3** | **Security** – All external communications (policy store, audit sink, metrics) must use TLS 1.2+ with certificate verification. The container image must be built from a minimal, non‑root base (e.g., `gcr.io/distroless/static`). |
| **NFR‑4** | **Reliability** – Achieve ≥ 99.9 % availability of the admission webhook (max 5 min downtime per month). Implement liveness and readiness probes. |
| **NFR‑5** | **Observability** – Logs must be structured (JSON) and include correlation IDs. Metrics must be compatible with the cluster‑wide Prometheus stack. |
| **NFR‑6** | **Compliance** – The system must be auditable for HIPAA and GDPR: retain audit logs for at least 180 days, support log export, and ensure no PHI is stored in plaintext on disk. |
| **NFR‑7** | **Resource Usage** – Each pod must stay ≤ 150 MiB memory and ≤ 200 mCPU under normal load. |
| **NFR‑8** | **Disaster Recovery** – Policy cache must be re‑hydrated from the remote store on pod restart; exceptions persisted in a ConfigMap must survive node failures. |
| **NFR‑9** | **Compatibility** – Support Kubernetes v1.27‑v1.30 and OpenShift 4.14+. Must work with both `containerd` and `CRI-O`. |
| **NFR‑10** | **Testing** – Provide unit, integration, and e2e test suites with ≥ 90 % code coverage. CI must run on every PR and block merge on failures. |

---

## 4. Constraints  

1. **Language/Framework** – Implementation must be in **Go 1.22** using the `controller-runtime` library for webhook handling.  
2. **Policy Store** – Must be a read‑only HTTP(S) endpoint returning a single JSON array; no authentication mechanisms other than optional bearer token (`policyStoreAuthToken` Helm value).  
3. **Sidecar Proxy** – Must use the open‑source **Envoy** binary compiled for Linux/amd64; no custom network kernel modules.  
4. **Helm Version** – Chart must be compatible with Helm 3.12+.  
5. **License** – All third‑party dependencies must be compatible with **Apache‑2.0**; no GPL components.  
6. **CI/CD** – Build pipeline must run inside the company’s standard Docker‑in‑Docker runner and push images to the internal registry `registry.axentx.io/health-data-guard`.  

---

## 5. Assumptions  

| ID | Assumption |
|----|------------|
| **A‑1** | The policy store URL supplied by the customer returns a well‑formed JSON document adhering to the Health Policy Schema v1.0. |
| **A‑2** | Cluster administrators will grant the `health-data-guard-admin` role to the ServiceAccount used by the HDG deployment. |
| **A‑3** | Network policies in the cluster allow the HDG pods to reach the policy store and optional audit sink. |
| **A‑4** | Customers will enable the sidecar proxy by labeling their pods with `health-data-guard=enabled`. |
| **A‑5** | The underlying Kubernetes distribution provides a functional `MutatingWebhookConfiguration` API (no feature gates disabled). |
| **A‑6** | Sufficient CPU and memory resources are provisioned for the default replica count (2) in the target cluster. |
| **A‑7** | The organization’s Prometheus stack scrapes the `/metrics` endpoint on the `health-data-guard` service. |
| **A‑8** | All TLS certificates for external endpoints are managed outside of HDG (e.g., via cert‑manager). |

---

## 6. Appendices  

### Appendix A – Health Policy Schema v1.0 (excerpt)  
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "HealthPolicy",
  "type": "object",
  "required": ["id", "description", "resourceSelectors", "allowedOperations"],
  "properties": {
    "id": { "type": "string" },
    "description": { "type": "string" },
    "resourceSelectors": {
      "type": "array",
      "items": { "$ref": "#/definitions/ResourceSelector" }
    },
    "allowedOperations": {
      "type": "array",
      "items": { "type": "string", "enum": ["read", "write", "delete"] }
    },
    "dataRetentionDays": { "type": "integer", "minimum": 0 }
  },
  "definitions": {
    "ResourceSelector": {
      "type": "object",
      "required": ["apiGroup", "kind", "namespace", "namePattern"],
      "properties": {
        "apiGroup": { "type": "string" },
        "kind": { "type": "string" },
        "namespace": { "type": "string" },
        "namePattern": { "type": "string" }
      }
    }
  }
}
```

---  

*End of Document*
