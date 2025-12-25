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

resource "aws_security_group" "alb_sg" {
  name_prefix = "anyllm2music-alb-sg"

  ingress {
    from_port   = 80
    to_port     = 80
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

resource "aws_lb" "app_lb" {
  name               = "anyllm2music-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = data.aws_subnets.default.ids

  enable_deletion_protection = false

  tags = {
    Name = "AnyLLM2Music-ALB"
  }
}

data "aws_subnets" "default" {
  filter {
    name   = "default-for-az"
    values = ["true"]
  }
}

resource "aws_lb_target_group" "app_tg" {
  name     = "anyllm2music-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = data.aws_vpc.default.id

  health_check {
    path                = "/"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

data "aws_vpc" "default" {
  default = true
}

resource "aws_lb_listener" "app_listener" {
  load_balancer_arn = aws_lb.app_lb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app_tg.arn
  }
}

resource "aws_lb_target_group_attachment" "app_tg_attachment" {
  target_group_arn = aws_lb_target_group.app_tg.arn
  target_id        = aws_instance.app_instance.id
  port             = 8000
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

output "alb_dns_name" {
  value = aws_lb.app_lb.dns_name
}