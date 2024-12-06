variable "region" {
  type = string
}

variable "project_name" {
  type = string
}

variable "instance_type" {
  type = string
}

variable "eks_policy_arn" {
  default = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
}

variable "access_config" {
  default = "API_AND_CONFIG_MAP"
}
