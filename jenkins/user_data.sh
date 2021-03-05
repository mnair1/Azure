#!/bin/bash -x
yum update -y
yum install docker -y
service docker start
usermod -a -G docker ec2-user