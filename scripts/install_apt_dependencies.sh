#!/bin/sh

sudo add-apt-repository -y ppa:ethereum/ethereum
sudo add-apt-repository -y ppa:ethereum/ethereum-dev

LIST_OF_APPS="ethereum mysql-server python3-pip solc"

sudo apt-get install -y $LIST_OF_APPS
