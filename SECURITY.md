# Security

## Reporting a vulnerability
Report suspected vulnerabilities privately via GitHub Security Advisories
("Report a vulnerability" on the repository Security tab). Please do not open a
public issue for security reports.

## Controls in this project
- **Supply chain**: dependency audit (`pip-audit`) and container image scan
  (Trivy) in CI; SBOM (SPDX) generated on release.
- **Static analysis**: `bandit` on application code.
- **Runtime hardening**: non-root container, read-only root filesystem, all
  Linux capabilities dropped, `seccomp: RuntimeDefault`, NetworkPolicy.
- **Secrets**: never committed; delivered at runtime via External Secrets from
  AWS Secrets Manager. Database master password is generated and stored in
  Secrets Manager by Terraform.
- **Transport**: TLS terminated at the ingress; Redis in transit/at-rest
  encryption enabled in AWS.
