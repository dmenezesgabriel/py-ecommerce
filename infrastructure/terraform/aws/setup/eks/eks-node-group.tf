resource "aws_eks_node_group" "node" {
  cluster_name    = aws_eks_cluster.eks-cluster.name
  node_group_name = "node-group-${var.project_name}"
  node_role_arn   = data.aws_iam_role.lab_role.arn
  subnet_ids = [
    aws_subnet.private-us-east-1a.id,
    aws_subnet.private-us-east-1b.id,
  ]
  capacity_type  = "ON_DEMAND"
  instance_types = [var.instance_type]
  disk_size      = 50

  scaling_config {
    desired_size = 1
    max_size     = 2
    min_size     = 1
  }

  update_config {
    max_unavailable = 1
  }
}
