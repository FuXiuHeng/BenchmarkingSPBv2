#!/usr/bin/python

from attrdict import (
    AttrDict,
)
import pickle
import socket
import struct
import time
import web3

import data.fake
import private_keys.getter
import overlay_nodes.helper.communications as communications
import overlay_nodes.helper.constants
import overlay_nodes.helper.logger as logger
from settings.settings import settings

# Simulation settings
simulation_date_time = settings["simulation_date_time"]
energy_file = './data/energy_usage_data/separated_users/user1/user1.mat'
energy_price = 0.01

# Ethereum settings
user_rpc_port_start = settings["user_rpc_port_start"]
password = settings["password"]

# Overlay network settings
poller_port = settings["poller_port"]
miner_ctp_overlay_port = settings["miner_ctp_overlay_port"]
local_host = socket.gethostname()
node_name = 'simulator'

# Welcome message
logger.log(simulation_date_time, node_name, 'Running SPB Simulation')
print('Running SPB simulation')

# Fake data for testing
num_users = settings["num_users"] - 1 # -1 because 1 user is reserved as producer
num_fake_data = 5
fake_data = data.fake.generate_energy_usage_data(num_users, num_fake_data)

# Inform poller about how many transaction to poll in the simulation
num_data = len(fake_data)
packet_header = overlay_nodes.helper.constants.NUM_TXN
poller_conn = socket.socket()
poller_conn.connect((local_host, poller_port))
logger.log(simulation_date_time, node_name, 'Connected to poller: {}'.format((local_host, poller_port)))
print('Connected to poller: {}'.format((local_host, poller_port)))

communications.send_message(poller_conn ,packet_header, num_data)
logger.log(simulation_date_time, node_name, 'Sent NUM_TXN to poller')
print('Sent NUM_TXN to poller')
poller_conn.close()

customer_to_user_dict = {} # customer_index_dict[customer_id] = user_id
w3_dict = {}               # w3_dict[customer_id] = w3
nonce_base_dict = {}       # nonce_base_dict[customer_id] = nonce_base
nonce_counter_dict = {}    # nonce_counter_dict[customer_id] = nonce_counter
user_rpc_port_dict = {}    # user_port_dict[customer_id] = user_rpc_port
private_key_dict = {}      # private_key_dict[customer_id] = private_key

next_user_id = 2 # user_id 1 reserved as producer

# Connect to the CTP miner socket
miner_conn = socket.socket()
miner_conn.connect((local_host, miner_ctp_overlay_port))
logger.log(simulation_date_time, node_name, 'Connected to miner: {}'.format((local_host, miner_ctp_overlay_port)))
print('Connected to miner: {}'.format((local_host, miner_ctp_overlay_port)))

# For each energy transaction
# Generate CTP transaction as a raw, signed ethereum transaction object
for data_txn in fake_data:
    customer_id = data_txn[data.constants.CUSTOMER_ID_KEY]
    energy_usage = data_txn[data.constants.ENERGY_KEY]

    if customer_id not in customer_to_user_dict:
        # Assign user id to customer id
        customer_to_user_dict[customer_id] = next_user_id

        # Assign ethereum port, create web3 instance and initialise nonce info
        user_rpc_port = user_rpc_port_start + next_user_id - 1
        w3 = web3.Web3(web3.Web3.HTTPProvider('http://127.0.0.1:{}'.format(user_rpc_port)))
        nonce_base = w3.eth.getTransactionCount(w3.eth.coinbase)
        nonce_counter = 0
        with open('./eth_nodes/user{:02d}/keystore/pk'.format(next_user_id)) as f:
            encrypted_key = f.read()
            private_key = w3.eth.account.decrypt(encrypted_key, password)

        w3_dict[customer_id] = w3
        nonce_base_dict[customer_id] = nonce_base
        nonce_counter_dict[customer_id] = nonce_counter
        user_rpc_port_dict[customer_id] = user_rpc_port
        private_key_dict[customer_id] = private_key

        next_user_id += 1

    logger.log(simulation_date_time, node_name, 'Customer {} used energy {}'.format(customer_id, energy_usage))
    print('Customer {} used energy {}'.format(customer_id, energy_usage))

    w3 = w3_dict[customer_id]
    nonce_base = nonce_base_dict[customer_id]
    nonce_counter = nonce_counter_dict[customer_id]
    user_rpc_port = user_rpc_port_dict[customer_id]
    private_key = private_key_dict[customer_id]

    producer_eth_addr = private_keys.getter.get_address('user01')

    txn = {
        'to': w3.toChecksumAddress(producer_eth_addr),
        'value': w3.toWei(energy_usage * energy_price, 'ether'),
        'gas': 900000,
        'gasPrice': 234567897654,
        'nonce': nonce_base + nonce_counter
    }
    nonce_counter_dict[customer_id] += 1

    w3.personal.unlockAccount(w3.eth.coinbase, password)
    signed_txn = w3.eth.account.signTransaction(txn, private_key)
    copied_txn = AttrDict(signed_txn) # This step prevents type error when unpickling on the receiver node
    pickled_txn = pickle.dumps(copied_txn) # Convert python object to byte stream
    txn_hash = signed_txn.hash

    # Send CTP to miner
    miner_conn.sendall(
        overlay_nodes.helper.constants.CTP
        + struct.pack("i", len(pickled_txn))
        + pickled_txn
    )
    logger.log(simulation_date_time, node_name, 'Sent CTP to miner')
    print('Sent CTP to miner')

# Send END to miner to signal that there are no more CTPs
miner_conn.sendall(overlay_nodes.helper.constants.END)

miner_conn.close()