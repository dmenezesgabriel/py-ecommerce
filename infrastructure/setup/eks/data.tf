data "aws_iam_role" "lab_role" {
  name = "LabRole"
}

data "aws_caller_identity" "current" {}

data "aws_vpc" "default_vpc" {
  default = true
}

data "aws_subnet" "default_subnet_a" {
  vpc_id            = data.aws_vpc.default_vpc.id
  availability_zone = "us-east-1a"
}

data "aws_subnet" "default_subnet_b" {
  vpc_id            = data.aws_vpc.default_vpc.id
  availability_zone = "us-east-1b"
}

data "aws_subnet" "default_subnet_c" {
  vpc_id            = data.aws_vpc.default_vpc.id
  availability_zone = "us-east-1c"
}

data "aws_security_group" "default" {
  vpc_id = data.aws_vpc.default_vpc.id
  name   = "default"
}

data "aws_security_group" "main" {
  vpc_id = aws_vpc.main_vpc.id
  name   = "default"
}
