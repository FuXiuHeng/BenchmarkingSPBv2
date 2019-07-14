#!/usr/bin/python

from attrdict import (
    AttrDict,
)
import pickle
import socket
import time
import web3

from settings.settings import settings
from overlay_nodes import miner_ctp
from scripts import init_eth_nodes

# init_eth_nodes.run(settings)
miner_ctp.run(settings)