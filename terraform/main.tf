terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

resource "aws_ecr_repository" "anyllm2music_backend" {
  name                 = "anyllm2music-backend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "AnyLLM2Music Backend Repository"
  }
}

resource "aws_ecr_lifecycle_policy" "anyllm2music_backend" {
  repository = aws_ecr_repository.anyllm2music_backend.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 2 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 2
      }
      action = {
        type = "expire"
      }
    }]
  })
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "ap-northeast-3"
}