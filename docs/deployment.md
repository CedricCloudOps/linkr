# Deployment

## Pipeline overview
- **CI** (`.github/workflows/ci.yml`) runs on every pull request and push:
  lint, SAST, dependency audit, unit tests (Python 3.11/3.12), a migration
  apply/revert against PostgreSQL, and an image build with a Trivy scan.
- **Release and Deploy** (`.github/workflows/release.yml`) runs on `main` and on
  `v*` tags: build and push the image to GHCR, scan it, generate an SBOM, then
  deploy.

## Promotion flow
```
push to main ──▶ build+scan+SBOM ──▶ deploy to staging (auto)
tag vX.Y.Z   ──▶ build+scan+SBOM ──▶ deploy to production (manual approval)
                                  └─▶ GitHub Release (notes + SBOM)
```
Production uses a protected GitHub Environment; the deploy waits for a manual
approval before it runs.

## Images
Immutable, tagged by semantic version and commit SHA
(`ghcr.io/cedriccloudops/linkr:1.0.0`, `:sha-<commit>`). `latest` is never
deployed.

## Kubernetes (Kustomize)
```bash
# Render locally
kubectl kustomize deploy/kubernetes/overlays/staging

# Apply
kubectl apply -k deploy/kubernetes/overlays/staging
kubectl apply -k deploy/kubernetes/overlays/production
```
Overlays differ by namespace, hostname, replica count, resources and config.

## Secrets
`DATABASE_URL` and `REDIS_URL` are delivered by the External Secrets Operator
from AWS Secrets Manager into a `linkr-secrets` Secret
(`deploy/kubernetes/base/externalsecret.yaml`). No secret is stored in git.
The CI/CD deploy jobs need a `KUBECONFIG` secret (base64) per environment.

## Infrastructure
The cluster and managed data stores are provisioned with Terraform; see
`infra/terraform/README.md`.

## Rollback
`kubectl -n <ns> rollout undo deployment/linkr`. See `docs/runbook.md`.
