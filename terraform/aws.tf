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

variable "region" {
  description = "AWS region"
  default     = "ap-northeast-3"
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t3.micro"
}

variable "docker_image" {
  description = "Docker image to deploy"
  default     = "anyllm2music-backend:latest"
}

variable "openrouter_url" {
  description = "OpenRouter API URL"
  default     = "https://openrouter.ai/api/v1"
}

variable "openrouter_api_key" {
  description = "OpenRouter API key"
  type        = string
  sensitive   = true
}

variable "openrouter_default_free_model" {
  description = "Default free model for OpenRouter"
  default     = "meta-llama/llama-3.3-70b-instruct:free"
}

variable "openrouter_default_model" {
  description = "Default model for OpenRouter"
  default     = "x-ai/grok-4.1-fast"
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_security_group" "app_sg" {
  name_prefix = "anyllm2music-sg"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}








resource "aws_instance" "app_instance" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type

  security_groups = [aws_security_group.app_sg.name]

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              amazon-linux-extras install docker -y
              service docker start
              usermod -a -G docker ec2-user
              docker pull ${var.docker_image}
              docker run -d -p 8000:8000 \
                -e OPENROUTER_URL=${var.openrouter_url} \
                -e OPENROUTER_API_KEY=${var.openrouter_api_key} \
                -e OPENROUTER_DEFAULT_FREE_MODEL=${var.openrouter_default_free_model} \
                -e OPENROUTER_DEFAULT_MODEL=${var.openrouter_default_model} \
                ${var.docker_image}
              EOF

  tags = {
    Name = "AnyLLM2Music-Backend"
  }
}

output "instance_public_ip" {
  value = aws_instance.app_instance.public_ip
}