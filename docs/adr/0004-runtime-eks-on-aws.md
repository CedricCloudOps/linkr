# ADR 0004 — Run on EKS (AWS)

- Status: accepted
- Date: 2026-01-05

## Context
The service needs zero-downtime deploys, horizontal autoscaling, and a portable
deployment model across environments. Candidate runtimes: AWS Lambda, ECS
Fargate, and EKS (Kubernetes).

## Decision
Run on **EKS**. Deployment manifests are environment-agnostic Kustomize bases
with per-environment overlays, so the same artifacts run on any conformant
cluster (including local kind clusters).

## Alternatives considered
- **Lambda** — excellent for spiky traffic, but per-request cold starts and the
  30 s/6 MB constraints fit the redirect path poorly, and the programming model
  differs from the container used everywhere else.
- **ECS Fargate** — simpler than EKS, but weaker ecosystem for progressive
  delivery, HPA on custom metrics, and the operator tooling (External Secrets,
  Prometheus Operator) this project relies on.

## Consequences
- More operational surface than Fargate/Lambda (cluster upgrades, node pools).
- Full portability and a rich, standard operations toolchain.
- Terraform provisions VPC, EKS, RDS, ElastiCache and ECR (see `infra/terraform`).
