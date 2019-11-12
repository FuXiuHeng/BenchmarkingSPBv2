#!/usr/bin/python

from attrdict import (
    AttrDict,
)
import multiprocessing
import pickle
import socket
import struct
import subprocess
import threading
import time
import web3

import data.constants
import data.parser
import private_keys.getter
import overlay_nodes.helper.communications as communications
import overlay_nodes.helper.constants
import overlay_nodes.helper.logger as logger
from overlay_nodes import miner_ctp, miner_erc, poller
from settings.settings import settings

# Simulation settings
simulation_name = settings["simulation_name"]
energy_price = settings["energy_price"]

# Ethereum settings
user_rpc_port_start = settings["user_rpc_port_start"]
password = settings["password"]

# Overlay network settings
poller_port = settings["poller_port"]
miner_ctp_overlay_port = settings["miner_ctp_overlay_port"]
local_host = socket.gethostname()
node_name = 'simulator'

# Welcome message
# logger.log(simulation_name, node_name, 'Running SPB Simulation')
print('Running SPB simulation')

# Start thread for all overlay nodes
# logger.log(simulation_name, node_name, 'Starting threads for miner_ctp, miner_erc and poller')
print('Starting threads for miner_ctp, miner_erc and poller')
miner_ctp_thread = threading.Thread(target=miner_ctp.run, args=(settings,))
miner_erc_thread = threading.Thread(target=miner_erc.run, args=(settings,))
poller_process = multiprocessing.Process(target=poller.run, args=(settings, "spb", ))

miner_ctp_thread.start()
miner_erc_thread.start()
poller_process.start()

# logger.log(simulation_name, node_name, 'Allowing time for threads to complete initialisation')
print('Allowing time for threads to complete initialisation')
time.sleep(5)

# Data parsing
num_users = settings["num_users"]
data_path = settings["data_path"]

# logger.log(simulation_name, node_name, 'Parsing data: {}'.format(data_path))
print('Parsing data: {}'.format(data_path))
all_energy_data = data.parser.parse_energy_usage_file(data_path)
# logger.log(simulation_name, node_name, 'Completed parsing of real data')
print('Completed parsing of real data')

# Partial data
if settings["use_partial_data"]:
    start = settings["partial_data_start"]
    end = settings["partial_data_end"]
    if end > len(all_energy_data):
        end = len(all_energy_data)
    energy_data = all_energy_data[start:end]
else:
    energy_data = all_energy_data

# Inform poller about how many transaction to poll in the simulation
num_data = len(energy_data)
packet_header = overlay_nodes.helper.constants.NUM_TXN
poller_conn = socket.socket()
poller_conn.connect((local_host, poller_port))
# logger.log(simulation_name, node_name, 'Connected to poller: {}'.format((local_host, poller_port)))
print('Connected to poller: {}'.format((local_host, poller_port)))

communications.send_message(poller_conn ,packet_header, num_data)
# logger.log(simulation_name, node_name, 'Sent NUM_TXN to poller: {}'.format(num_data))
print('Sent NUM_TXN to poller: {}'.format(num_data))
poller_conn.close()

prosumer_to_user_dict = {} # prosumer_to_user_dict[prosumer_id] = user_id
user_id_dict = {}          # user_id_dict[user_id] = True (if at least once customer is assigned this user_id)
w3_dict = {}               # w3_dict[user_id] = w3
nonce_base_dict = {}       # nonce_base_dict[user_id] = nonce_base
nonce_counter_dict = {}    # nonce_counter_dict[user_id] = nonce_counter
user_rpc_port_dict = {}    # user_port_dict[user_id] = user_rpc_port
private_key_dict = {}      # private_key_dict[user_id] = private_key

next_user_id = 1

# Connect to the CTP miner socket
miner_conn = socket.socket()
miner_conn.connect((local_host, miner_ctp_overlay_port))
# logger.log(simulation_name, node_name, 'Connected to miner: {}'.format((local_host, miner_ctp_overlay_port)))
print('Connected to miner: {}'.format((local_host, miner_ctp_overlay_port)))

# For each energy transaction
# Generate CTP transaction as a raw, signed ethereum transaction object
data_no = 1
for data_txn in energy_data:
    consumer_id = data_txn[data.constants.CONSUMER_ID_KEY]
    producer_id = data_txn[data.constants.PRODUCER_ID_KEY]
    energy_usage = data_txn[data.constants.ENERGY_KEY]

    # Assign user id to new prosumers
    if consumer_id not in prosumer_to_user_dict:
        if next_user_id > num_users: # Ensures number of users does not exceed the number specified in the settings
            next_user_id = 1
        prosumer_to_user_dict[consumer_id] = next_user_id
        next_user_id += 1
        
    if producer_id not in prosumer_to_user_dict:
        if next_user_id > num_users: # Ensures number of users does not exceed the number specified in the settings
            next_user_id = 1
        prosumer_to_user_dict[producer_id] = next_user_id
        next_user_id += 1
        
    # Assign ethereum port, create web3 instance and initialise nonce info
    consumer_user_id = prosumer_to_user_dict[consumer_id]
    producer_user_id = prosumer_to_user_dict[producer_id]

    if consumer_user_id not in user_id_dict:
        user_rpc_port = user_rpc_port_start + consumer_user_id - 1
        w3 = web3.Web3(web3.Web3.HTTPProvider('http://127.0.0.1:{}'.format(user_rpc_port)))
        nonce_base = w3.eth.getTransactionCount(w3.eth.coinbase)
        nonce_counter = 0
        with open('./eth_nodes/user{:02d}/keystore/pk'.format(consumer_user_id)) as f:
            encrypted_key = f.read()
            private_key = w3.eth.account.decrypt(encrypted_key, password)

        w3_dict[consumer_user_id] = w3
        nonce_base_dict[consumer_user_id] = nonce_base
        nonce_counter_dict[consumer_user_id] = nonce_counter
        user_rpc_port_dict[consumer_user_id] = user_rpc_port
        private_key_dict[consumer_user_id] = private_key

        user_id_dict[consumer_user_id] = True

    # logger.log(simulation_name, node_name, 'Transaction {}: Prosumer {} bought {} energy from prosumer {}'.format(data_no, consumer_user_id, energy_usage, producer_user_id))
    print('Transaction {}: Prosumer {} bought {} energy from prosumer {}'.format(data_no, consumer_user_id, energy_usage, producer_user_id))

    w3 = w3_dict[consumer_user_id]
    nonce_base = nonce_base_dict[consumer_user_id]
    nonce_counter = nonce_counter_dict[consumer_user_id]
    user_rpc_port = user_rpc_port_dict[consumer_user_id]
    private_key = private_key_dict[consumer_user_id]

    producer_eth_addr = private_keys.getter.get_address('user{:02d}'.format(producer_user_id))

    txn = {
        'to': w3.toChecksumAddress(producer_eth_addr),
        'value': w3.toWei(energy_usage * energy_price, 'ether'),
        'gas': 900000,
        'gasPrice': 234567897654,
        'nonce': nonce_base + nonce_counter
    }
    nonce_counter_dict[consumer_user_id] += 1

    w3.geth.personal.unlockAccount(w3.eth.coinbase, password)
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
    # logger.log(simulation_name, node_name, 'Sent CTP to miner')
    print('Sent CTP to miner')

    data_no += 1

# Send END to miner to signal that there are no more CTPs
miner_conn.sendall(overlay_nodes.helper.constants.END)

miner_conn.close()

# Wait for all other threads to complete running before closing main process
miner_ctp_thread.join()
miner_erc_thread.join()
poller_process.join()

# Kill all ethereum nodes
subprocess.call("./scripts/kill_eth_nodes.sh")