resource "aws_eks_access_policy_association" "policy" {
  cluster_name  = aws_eks_cluster.eks-cluster.name
  policy_arn    = var.eks_policy_arn
  principal_arn = local.principal_arn

  access_scope {
    type = "cluster"
  }
}
