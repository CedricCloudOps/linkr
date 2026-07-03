# Terraform — AWS infrastructure

Provisions the runtime for `linkr` on AWS:

- **VPC** across 3 availability zones (public, private and database subnets)
- **EKS** managed cluster with a managed node group and IRSA enabled
- **ECR** repository (immutable tags, scan on push)
- **RDS** PostgreSQL 16 (master password stored in Secrets Manager)
- **ElastiCache** Redis (encryption in transit and at rest; multi-AZ in production)

## Prerequisites
- Terraform >= 1.6, AWS CLI configured with credentials.
- An S3 bucket and DynamoDB table for remote state (see `versions.tf`).

## Usage
```bash
cd infra/terraform
terraform init
terraform workspace new staging   # or: terraform workspace select staging
terraform plan  -var environment=staging
terraform apply -var environment=staging
```

Production uses the same code with `-var environment=production`, which enables
Multi-AZ RDS, Redis automatic failover, deletion protection and longer backups.

## Cost note
This stack creates billable resources (EKS control plane, NAT gateways, RDS,
ElastiCache). Run `terraform destroy` when finished. Use `terraform plan` alone
to review the topology at no cost.

## Wiring application secrets
`terraform output rds_master_secret_arn` returns the Secrets Manager ARN of the
generated database password. Map the connection string to `linkr/database-url`
in Secrets Manager; the External Secrets Operator (see
`deploy/kubernetes/base/externalsecret.yaml`) syncs it into the cluster.
