resource "aws_instance" "multi_tier_instance" {
  ami           = "ami-0ac80df6eff0e70b5"
  instance_type = "t2.micro"
  key_name  = "devops-ssh"
  vpc_security_group_ids = ["sg-06fbdcffcabedd6ba"]
  subnet_id = "subnet-31acdb0f"
  associate_public_ip_address = true
  user_data = file("bootstrap.sh")
  root_block_device {
      volume_type = "standard"
      volume_size = 30
      delete_on_termination = true
  }
  tags = {
    Name = "tf-bootstrapped-multi-tier-app"
  }

   provisioner "file" {
    content     = "app/"
    destination = "/home/ubuntu/app"

    connection {
    type     = "winrm"
    user     = "ubuntu"
    host     = aws_instance.multi_tier_instance.public_ip
    private_key = file("devops-ssh.pem")
  }

  }
}