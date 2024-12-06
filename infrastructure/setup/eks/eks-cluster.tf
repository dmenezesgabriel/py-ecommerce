resource "aws_eks_cluster" "eks-cluster" {
  name     = "cluster-${var.project_name}"
  role_arn = data.aws_iam_role.lab_role.arn

  vpc_config {
    subnet_ids = [
      aws_subnet.private-us-east-1a.id,
      aws_subnet.private-us-east-1b.id,
      aws_subnet.public-us-east-1a.id,
      aws_subnet.public-us-east-1b.id
    ]
    security_group_ids = [data.aws_security_group.main.id]
  }

  access_config {
    authentication_mode = var.access_config
  }
}
