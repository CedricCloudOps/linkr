output "cluster_name" {
  value = module.eks.cluster_name
}

output "cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}

output "rds_endpoint" {
  value = module.rds.db_instance_endpoint
}

output "rds_master_secret_arn" {
  description = "Secrets Manager ARN holding the generated DB master password"
  value       = module.rds.db_instance_master_user_secret_arn
}

output "redis_primary_endpoint" {
  value = aws_elasticache_replication_group.redis.primary_endpoint_address
}
