output "app_url" {
    value = "http://${aws_instance.multi_tier_instance.public_ip}:3000"
}

output "ssh_instance" {
    value = aws_instance.multi_tier_instance.public_ip
}


output "ssh_key_name" {
   value = var.ssh_key
}

output "ami_ids" {
   value = data.aws_ami_ids.ubuntu_18.ids[0]
}




