sudo yum update -y
sudo yum install docker
sudo service docker start
sudo usermod -a -G docker ec2-user
#curl -L https://github.com/docker/compose/releases/download/1.26.2/docker-compose-Linux-x86_64 -o /usr/local/bin/docker-compose
#chmod +x /usr/local/bin/docker-compose
curl -L https://github.com/docker/compose/releases/download/1.26.2/docker-compose-Linux-x86_64 -o /usr/bin/docker-compose
chmod +x /usr/bin/docker-compose
