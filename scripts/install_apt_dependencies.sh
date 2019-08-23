#!/bin/sh

sudo add-apt-repository -y ppa:ethereum/ethereum

LIST_OF_APPS="ethereum mysql-server python3-pip"

sudo apt-get install -y $LIST_OF_APPS
