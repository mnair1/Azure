variable "environment" {
    type = string
    description = "environment type (i.e dev, qa, uat, prod)"
}

variable "team" {
    type = string
    description = "name of the team (i.e datafence)"
}

variable "ssh_key" {
    type = string
    description = "ssh key name for ec2"
    default = "devops-ssh"
}