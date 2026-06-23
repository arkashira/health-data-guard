# Health Data Guard

Health Data Guard is a runtime integration layer for enforcing policies in a Kubernetes cluster.

## Usage

1. Build the Docker image: `docker build -t health-data-guard:1.0.0 .`
2. Deploy to Kubernetes: `helm install health-data-guard --set policyStoreUrl=https://example.com/policy-store`
