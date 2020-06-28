#!/bin/bash
sudo apt update
sudo apt install python3-pip -y
pip3 install flask==1.0.2
pip3 install flask_pymongo==2.3.0
pip3 install flask_cors==3.0.7
sudo apt -y install curl dirmngr apt-transport-https lsb-release ca-certificates && curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
sudo apt -y install nodejs
node --version
npm --version
sudo apt install -y mongodb