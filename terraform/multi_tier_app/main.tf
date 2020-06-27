module "datafence_network" {
 
  source = "terraform-aws-modules/vpc/aws"
  
  name = "${var.environment}-${var.team}-vpc"
  cidr = "10.0.0.0/16"

  azs  = ["us-east-1a"]
  public_subnets = ["10.0.1.0/24"]
  enable_dns_hostnames = true

  tags = {
    Envrionment = var.environment
  }
}

module "datafence_sg_access" {
  source = "terraform-aws-modules/security-group/aws"

  name        = "${var.environment}-${var.team}-sg"
  description = "Security group for frontend and ssh access"
  vpc_id      = module.datafence_network.vpc_id

  ingress_with_cidr_blocks = [
    {
      from_port   = 3000
      to_port     = 3000
      protocol    = "tcp"
      description = "Frontend Access"
      cidr_blocks = "0.0.0.0/0"
    },
    {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      description = "SSH Access"
      cidr_blocks = "0.0.0.0/0"
    },
  ]

  egress_with_cidr_blocks = [
    {
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = "0.0.0.0/0"
    },
  ]

  tags = {
    Envrionment = var.environment
  }

}

data "aws_ami_ids" "ubuntu_18" {
  owners = ["099720109477"]
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-*"]
  }

}

resource "aws_instance" "multi_tier_instance" {
  ami                         = data.aws_ami_ids.ubuntu_18.ids[0]
  instance_type               = "t2.micro"
  key_name                    = var.ssh_key
  vpc_security_group_ids      = [module.datafence_sg_access.this_security_group_id] #[module.datafence_network.default_security_group_id]
  subnet_id                   = module.datafence_network.public_subnets[0]
  associate_public_ip_address = true
  user_data                   = file("bootstrap.sh")
  
  root_block_device {
      volume_type = "standard"
      volume_size = 30
      delete_on_termination = true
  }
  tags = {
    Name = "${var.environment}-${var.team}-multi-tier-app"
    Envrionment = var.environment
  }
  
}