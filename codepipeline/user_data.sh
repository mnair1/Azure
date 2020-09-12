#!/bin/bash -x
apt update
apt install python3-pip -y
pip3 install flask==1.0.2
pip3 install flask_pymongo==2.3.0
pip3 install flask_cors==3.0.7
apt -y install curl dirmngr apt-transport-https lsb-release ca-certificates && curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
apt -y install nodejs
apt install -y mongodb