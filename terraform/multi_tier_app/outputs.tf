output "app_url" {
    value = join("", ["http://", aws_instance.multi_tier_instance.public_ip, ":3000"])
}
