# TECH_SPEC.md  

**Project:** health-data-guard  
**Version:** 1.0.0  
**Owner:** Axentx OS – Security & Compliance Team  
**Last Updated:** 2026‑06‑24  

---  

## Table of Contents
1. [Overview](#1-overview)  
2. [Architecture Diagram](#2-architecture-diagram)  
3. [Core Components](#3-core-components)  
4. [Data Model](#4-data-model)  
5. [Key APIs & Interfaces](#5-key-apis--interfaces)  
6. [Technology Stack](#6-technology-stack)  
7. [External Dependencies](#7-external-dependencies)  
8. [Deployment & Operations](#8-deployment--operations)  
9. [Security & Compliance](#9-security--compliance)  
10. [Observability](#10-observability)  
11. [Failure & Recovery](#11-failure--recovery)  
12. [Scalability & Performance](#12-scalability--performance)  
13. [Future Enhancements](#13-future-enhancements)  
14. [Appendix](#14-appendix)  

---  

## 1. Overview
Health Data Guard (HDG) is a **runtime integration layer** that enforces data‑handling policies for health‑related workloads running in a Kubernetes cluster. It operates as a **mutating and validating admission webhook** combined with a **side‑car policy‑enforcement proxy**.  

Key goals:  

| Goal | Description |
|------|-------------|
| **Policy Enforcement** | Guarantees that every pod handling PHI (Protected Health Information) complies with organization‑wide policies (encryption‑at‑rest, network segmentation, audit logging, etc.). |
| **Zero‑Touch Integration** | Deployable via a single Helm chart; no code changes required for existing workloads. |
| **Extensible Policy Store** | Policies are fetched from a configurable remote store (REST/GRPC) and cached locally. |
| **Compliance‑Ready Auditing** | Generates immutable audit events stored in a configurable backend (e.g., CloudWatch, Elasticsearch). |
| **K8s‑Native** | Leverages native Kubernetes mechanisms (AdmissionReview, CRDs, RBAC). |

---  

## 2. Architecture Diagram
```
+-------------------+          +-------------------+          +-------------------+
|   Kubernetes API | <------> | Admission Webhook | <------> |  Policy Store API |
|   Server          |          | (mutating/valid) |          | (HTTPS/GRPC)      |
+-------------------+          +-------------------+          +-------------------+
          ^                               ^                               ^
          |                               |                               |
          |                               |                               |
          |   AdmissionReview             |   Policy Pull/Refresh          |
          |   (JSON)                      |   (JSON/Proto)                 |
          |                               |                               |
+-------------------+          +-------------------+          +-------------------+
|   Workload Pods   | <------> | Side‑car Proxy    | <------> |   Audit Backend   |
| (PHI‑handling)    |          | (Envoy/OPA)       |          | (S3/ES/CloudWatch)|
+-------------------+          +-------------------+          +-------------------+
```

* The **Admission Webhook** validates pod specs before they are persisted.  
* The **Side‑car Proxy** intercepts all inbound/outbound traffic of the pod, applying policy decisions in‑flight.  
* **Policy Store** holds declarative JSON/YAML policies; HDG caches them locally with TTL.  
* **Audit Backend** receives immutable audit logs via a push endpoint.

---  

## 3. Core Components
| Component | Language | Runtime | Description |
|-----------|----------|---------|-------------|
| `admission-webhook` | Go (1.22) | Stateless container | Implements MutatingAdmissionWebhook & ValidatingAdmissionWebhook. |
| `policy-agent` | Go + OPA (Rego) | Side‑car container (Envoy + OPA) | Evaluates requests against policies; returns allow/deny + mutation patches. |
| `policy-fetcher` | Go | Init container | Pulls policies from `policyStoreUrl`, validates signatures, writes to shared volume. |
| `audit-exporter` | Go | Side‑car container | Streams audit events to configured backend (configurable via env). |
| `helm chart` | YAML | N/A | Deploys all components, creates required RBAC, CRDs, and Service resources. |
| `CRD: HealthPolicy` | YAML | N/A | Allows cluster admins to define policies as native K8s objects (optional overlay). |

---  

## 4. Data Model
### 4.1 Policy Schema (JSON)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "HealthPolicy",
  "type": "object",
  "required": ["id", "description", "rules"],
  "properties": {
    "id": { "type": "string", "format": "uuid" },
    "description": { "type": "string" },
    "version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
    "rules": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["action", "resource", "conditions"],
        "properties": {
          "action": { "enum": ["allow", "deny"] },
          "resource": { "type": "string" },
          "conditions": {
            "type": "object",
            "additionalProperties": { "type": "string" }
          }
        }
      }
    },
    "signature": { "type": "string" }   // base64‑encoded SHA256 of the policy JSON
  }
}
```

### 4.2 AdmissionReview Patch (K8s)
Standard JSONPatch format as defined by K8s admission API.

### 4.3 Audit Event (JSON)
```json
{
  "timestamp": "2026-06-24T12:34:56Z",
  "requestID": "uuid",
  "pod": "namespace/name",
  "policyID": "uuid",
  "decision": "allow|deny",
  "details": { "matchedRule": "...", "reason": "..." },
  "sourceIP": "10.1.2.3",
  "user": "system:serviceaccount:default:my-sa"
}
```

---  

## 5. Key APIs & Interfaces
### 5.1 Admission Webhook Endpoints
| Path | Method | Payload | Response |
|------|--------|---------|----------|
| `/mutate` | POST | `AdmissionReview` (pod spec) | `AdmissionReview` with JSONPatch |
| `/validate` | POST | `AdmissionReview` (pod spec) | `AdmissionReview` with `allowed:true/false` & message |

### 5.2 Policy Store API (configurable)
* **GET** `/policies` – returns list of policies (JSON).  
* **GET** `/policies/{id}` – returns single policy with `If-None-Match` support.  
* **Optional** **POST** `/policies` – for internal CI/CD pipeline to push new policies (auth via mTLS).

### 5.3 Side‑car OPA API (local)
* **POST** `/v1/data/health/policy/decide` – request: `{ "input": {...} }` → response: `{ "result": { "allow": true, "reason": "..."} }`.

### 5.4 Audit Exporter
* **POST** `/audit` – internal only, receives audit JSON, forwards to backend.  

---  

## 6. Technology Stack
| Layer | Technology | Version | Rationale |
|-------|------------|---------|-----------|
| Container Runtime | Docker / OCI | 24.0+ | Standard for K8s |
| Orchestration | Kubernetes | 1.28+ | Production‑grade |
| Admission Webhook | Go + client-go | 1.22 | Low latency, native K8s SDK |
| Policy Engine | Open Policy Agent (OPA) | 0.61 | Declarative, Rego language, easy to extend |
| Proxy | Envoy | 1.28 | High‑performance L7 proxy, integrates with OPA via external auth |
| Helm | Helm 3.14 | – | Simplified install/upgrade |
| TLS | cert‑manager | 1.13 | Automated cert issuance for webhook |
| Logging | Zap (structured) | 1.26 | Performance & JSON output |
| Metrics | Prometheus client | 1.16 | Export webhook & side‑car metrics |
| Auditing | Fluent Bit → Elasticsearch / CloudWatch | – | Scalable log pipeline |
| CI/CD | GitHub Actions + ArgoCD | – | Automated build & rollout |

---  

## 7. External Dependencies
| Dependency | Purpose | Version/URL |
|------------|---------|-------------|
| `github.com/open-policy-agent/opa` | Policy evaluation engine | v0.61.0 |
| `github.com/envoyproxy/go-control-plane` | Envoy xDS integration | v0.12.0 |
| `k8s.io/api`, `k8s.io/client-go` | Admission webhook handling | v0.28.0 |
| `github.com/cert-manager/cert-manager` | Automated TLS for webhook | v1.13.2 |
| Policy Store (user‑provided) | Remote JSON/YAML policy repository | Configurable URL |
| Audit Backend (user‑provided) | Persistent audit log storage | Configurable endpoint |

---  

## 8. Deployment & Operations
### 8.1 Helm Chart Values (excerpt)
```yaml
replicaCount: 2
image:
  repository: health-data-guard
  tag: "1.0.0"
  pullPolicy: IfNotPresent
policyStoreUrl: https://example.com/policy-store
auditBackend:
  url: https://audit.example.com/ingest
  authToken: "<secret>"
resources:
  limits:
    cpu: "500m"
    memory: "256Mi"
  requests:
    cpu: "250m"
    memory: "128Mi"
tls:
  enabled: true
  certManager:
    enabled: true
    issuerRef:
      name: letsencrypt-prod
      kind: ClusterIssuer
```

### 8.1 Installation Steps
```bash
# 1. Build & push image
docker build -t <registry>/health-data-guard:1.0.0 .
docker push <registry>/health-data-guard:1.0.0

# 2. Install chart
helm repo add axentx https://charts.axentx.io
helm install health-data-guard axentx/health-data-guard \
  --set image.repository=<registry>/health-data-guard \
  --set policyStoreUrl=https://example.com/policy-store \
  --set auditBackend.url=https://audit.example.com/ingest
```

### 8.2 Upgrade / Rollback
* Use Helm `upgrade` with `--atomic` for zero‑downtime.  
* Rollback via `helm rollback health-data-guard <revision>`.

### 8.3 Certificate Management
* If `tls.certManager.enabled=true`, cert‑manager automatically provisions a TLS cert for the webhook service using the supplied `ClusterIssuer`.

---  

## 9. Security & Compliance
| Aspect | Implementation |
|--------|----------------|
| **Mutual TLS** | Webhook server requires client certs signed by the cluster’s CA. |
| **Policy Signature** | Policies must include a SHA‑256 signature; `policy-fetcher` validates against a public key (configurable via env `POLICY_PUBKEY`). |
| **RBAC** | Minimal ServiceAccount with `admissionregistration.k8s.io/webhooks` and `configmaps` read. |
| **Pod Security Standards** | Enforces `restricted` PSP/PodSecurityPolicy via admission validation. |
| **Data Residency** | Audit logs can be routed to region‑specific backends. |
| **Compliance** | Designed to satisfy HIPAA §164.312(b) (access control) and §164.312(e) (audit controls). |

---  

## 10. Observability
* **Metrics (Prometheus)**
  * `hdg_webhook_requests_total{type="mutate|validate",code="200|400|500"}`
  * `hdg_policy_cache_hits_total`
  * `hdg_sidecar_decisions_total{allow="true|false"}`
* **Logs**
  * Structured JSON via Zap; includes requestID, pod, policyID, decision.
* **Dashboards**
  * Provide Grafana dashboard JSON (in `charts/health-data-guard/dashboards/`).

---  

## 11. Failure & Recovery
| Failure Mode | Detection | Mitigation |
|--------------|-----------|------------|
| Policy fetch failure | `policy-fetcher` exit code ≠ 0 | Fallback to last‑known good cache; emit `Ready=False` condition on CRD. |
| Webhook timeout > 5s | Prometheus alert `hdg_webhook_latency_seconds` | Autoscale webhook deployment; increase `timeoutSeconds` in `ValidatingWebhookConfiguration`. |
| Side‑car OPA crash | Pod restart (k8s liveness probe) | Restart side‑car; policy cache persisted on emptyDir. |
| Audit backend unreachable | Exporter error counter > threshold | Buffer events locally (up to 10 k) and retry with exponential back‑off. |

---  

## 12. Scalability & Performance
* **Horizontal Pod Autoscaling** – based on CPU and `hdg_webhook_requests_total`.  
* **Cache Layer** – In‑memory LRU cache (size configurable, default 100 MiB) for policies; TTL 5 min.  
* **Latency Goal** – ≤ 30 ms per admission request, ≤ 5 ms per side‑car decision.  
* **Throughput** – Tested up to 10 k AdmissionReview/sec on a 4‑core node (benchmark scripts in `test/perf/`).  

---  

## 13. Future Enhancements
| # | Feature | Priority | Notes |
|---|---------|----------|-------|
| 1 | Policy versioning & rollback via CRD | High | Enables cluster‑wide “policy freeze”. |
| 2 | Support for OIDC‑based policy store authentication | Medium | Use client‑certificate or JWT. |
| 3 | Integration with Axentx BRAIN for automated policy generation from incident data | Low | Leverage existing vector store. |
| 4 | Multi‑cluster policy propagation (Federation) | Low | Future for multi‑region deployments. |

---  

## 14. Appendix
* **Directory Layout**
```
/charts/health-data-guard/          # Helm chart
/src/
   /cmd/webhook/                    # Admission webhook binary
   /cmd/policy-fetcher/             # Init container binary
   /cmd/audit-exporter/             # Audit exporter binary
   /internal/
       /policy/                     # Policy schema & validation
       /opa/                        # OPA wrapper
       /audit/                      # Audit struct & sink adapters
   /pkg/
       /k8s/                        # K8s client helpers
       /metrics/                    # Prometheus wrappers
Dockerfile
go.mod / go.sum
README.md
```

* **Build Commands**
```bash
make build          # builds all binaries
make docker-build   # builds multi‑arch image
make test           # unit + integration tests
make lint           # golangci-lint
```

* **License** – Apache‑2.0 (compatible with all bundled OSS).  

---  

*End of Technical Specification*
