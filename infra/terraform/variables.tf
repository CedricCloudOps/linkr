variable "project" {
  type    = string
  default = "linkr"
}

variable "environment" {
  type    = string
  default = "staging"
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "environment must be staging or production."
  }
}

variable "region" {
  type    = string
  default = "eu-west-3"
}

variable "vpc_cidr" {
  type    = string
  default = "10.20.0.0/16"
}

variable "kubernetes_version" {
  type    = string
  default = "1.30"
}

variable "node_instance_types" {
  type    = list(string)
  default = ["t3.medium"]
}

variable "node_min" {
  type    = number
  default = 2
}

variable "node_max" {
  type    = number
  default = 5
}

variable "node_desired" {
  type    = number
  default = 2
}

variable "db_instance_class" {
  type    = string
  default = "db.t4g.micro"
}

variable "redis_node_type" {
  type    = string
  default = "cache.t4g.micro"
}
