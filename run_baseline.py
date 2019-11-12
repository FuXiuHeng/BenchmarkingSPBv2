import multiprocessing
import json
import socket
import subprocess
import time
import web3
from solc import compile_standard

import data.parser
import private_keys.getter
import overlay_nodes.helper.communications as communications
import overlay_nodes.helper.constants
import overlay_nodes.helper.logger as logger
from overlay_nodes import poller
from settings.settings import settings

# Smart contract settings
contract_path = settings["contract_path"]

# Simulation settings
simulation_name = settings["simulation_name"]
energy_price = settings["energy_price"]

# Ethereum settings
miner_rpc_port = settings["miner_rpc_port"]
user_rpc_port_start = settings["user_rpc_port_start"]
password = settings["password"]

# Welcome message
print("Running Baseline simulation")

# Starting process for poller
print("Starting process for poller")
poller_process = multiprocessing.Process(target=poller.run, args=(settings, "baseline", ))
poller_process.start()
print("Allowing time for the poller to complete initialisation")
time.sleep(5)

# Data parsing
num_users = settings["num_users"]
data_path = settings["data_path"]

print("Parsing data: {}".format(data_path))
all_energy_data = data.parser.parse_energy_usage_file(data_path)

print("Completed parsing of data")

# Partial data
if settings["use_partial_data"]:
    start = settings["partial_data_start"]
    end = settings["partial_data_end"]
    if end > len(all_energy_data):
        end = len(all_energy_data)
    energy_data = all_energy_data[start:end]
else:
    energy_data = all_energy_data

# Compile the contract
with open(contract_path) as f:
    contract_string = f.read()

compiled_sol = compile_standard({
    "language": "Solidity",
    "sources": {
        "Baseline.sol": {
            "content": contract_string
        }
    },
    "settings": {
        "outputSelection": {
            "*": {
                "*": [
                    "metadata", "evm.bytecode"
                    , "evm.bytecode.sourceMap"
                ]
            }
        }
    }
})
bytecode = compiled_sol['contracts']['Baseline.sol']['Baseline']['evm']['bytecode']['object']
abi = json.loads(compiled_sol['contracts']['Baseline.sol']['Baseline']['metadata'])['output']['abi']

# Inform poller about how many transaction to poll in the simulation
poller_port = settings["poller_port"]
local_host = socket.gethostname()
num_data = len(energy_data)
num_txn = num_data * 3
packet_header = overlay_nodes.helper.constants.NUM_TXN
poller_conn = socket.socket()
poller_conn.connect((local_host, poller_port))
print('Connected to poller: {}'.format((local_host, poller_port)))
communications.send_message(poller_conn ,packet_header, num_txn)
print('Sent NUM_TXN to poller: {}'.format(num_txn))
poller_conn.close()

prosumer_to_user_dict = {} # prosumer_to_user_dict[prosumer_id] = user_id
user_id_dict = {}          # user_id_dict[user_id] = True (if at least once customer is assigned this user_id)
w3_dict = {}               # w3_dict[user_id] = w3
user_rpc_port_dict = {}    # user_port_dict[user_id] = user_rpc_port
private_key_dict = {}      # private_key_dict[user_id] = private_key

next_user_id = 1

# For each energy transaction
# Commit amount to smart contract
data_no = 1
pending_txn = []
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
        with open('./eth_nodes/user{:02d}/keystore/pk'.format(consumer_user_id)) as f:
            encrypted_key = f.read()
            private_key = w3.eth.account.decrypt(encrypted_key, password)

        w3_dict[consumer_user_id] = w3
        user_rpc_port_dict[consumer_user_id] = user_rpc_port
        private_key_dict[consumer_user_id] = private_key

        user_id_dict[consumer_user_id] = True

    if producer_user_id not in user_id_dict:
        user_rpc_port = user_rpc_port_start + producer_user_id - 1
        w3 = web3.Web3(web3.Web3.HTTPProvider('http://127.0.0.1:{}'.format(user_rpc_port)))
        with open('./eth_nodes/user{:02d}/keystore/pk'.format(producer_user_id)) as f:
            encrypted_key = f.read()
            private_key = w3.eth.account.decrypt(encrypted_key, password)

        w3_dict[producer_user_id] = w3
        user_rpc_port_dict[producer_user_id] = user_rpc_port
        private_key_dict[producer_user_id] = private_key

        user_id_dict[producer_user_id] = True
    
    consumer_w3 = w3_dict[consumer_user_id]
    consumer_rpc_port = user_rpc_port_dict[consumer_user_id]
    consumer_private_key = private_key_dict[consumer_user_id]
    consumer_eth_addr = private_keys.getter.get_address('user{:02d}'.format(consumer_user_id))

    producer_w3 = w3_dict[producer_user_id]
    producer_rpc_port = user_rpc_port_dict[producer_user_id]
    producer_private_key = private_key_dict[producer_user_id]
    producer_eth_addr = private_keys.getter.get_address('user{:02d}'.format(producer_user_id))
    print('Transaction {}: Prosumer {} bought {} energy from prosumer {}'.format(data_no, consumer_user_id, energy_usage, producer_user_id))

    # Producer generate smart contract
    producer_w3.eth.defaultAccount = producer_w3.eth.coinbase
    producer_w3.geth.personal.unlockAccount(producer_w3.eth.coinbase, password)
    Baseline = producer_w3.eth.contract(abi=abi, bytecode=bytecode)

    # Deploy contract
    print("Producer deploying baseline smart contract")
    tx_hash = Baseline.constructor(
                    producer_w3.toChecksumAddress(consumer_eth_addr),
                    producer_w3.toWei(energy_usage * energy_price, 'ether')
                ).transact({
                    'from': producer_w3.eth.coinbase
                })
    time_sent = time.time()
    logger.log_baseline_time_sent(simulation_name, time_sent, producer_w3.eth.coinbase, tx_hash)

    pending_txn.append(tx_hash)
    data_no += 1

# Check to ensure all the contract creation transactions has been mined
# Before proceeding to interacting with the contract
miner_w3 = web3.Web3(web3.Web3.HTTPProvider('http://127.0.0.1:{}'.format(miner_rpc_port)))
contract_add = []
print("Checking to ensure all contract has been deployed")
for tx_hash in pending_txn:
    tx_receipt = miner_w3.eth.waitForTransactionReceipt(tx_hash)
    contract_add.append(tx_receipt.contractAddress)
print("All contract has been deployed")

# Consumer pays the smart contract
pending_txn = []
i = 0
data_no = 1
for data_txn in energy_data:
    consumer_id = data_txn[data.constants.CONSUMER_ID_KEY]
    energy_usage = data_txn[data.constants.ENERGY_KEY]
    consumer_user_id = prosumer_to_user_dict[consumer_id]
    consumer_w3 = w3_dict[consumer_user_id]

    # Consumer pays the smart contract
    consumer_w3.geth.personal.unlockAccount(consumer_w3.eth.coinbase, password)
    baseline = consumer_w3.eth.contract(
        address=contract_add[i],
        abi=abi
    )
    print("Consumer making payment to contract for Transaction {}".format(data_no))
    tx_hash = baseline.functions.makePayment().transact({
        'from': consumer_w3.eth.coinbase,
        'value': consumer_w3.toWei(energy_usage * energy_price, 'ether')
    })
    time_sent = time.time()
    logger.log_baseline_time_sent(simulation_name, time_sent, consumer_w3.eth.coinbase, tx_hash)

    pending_txn.append(tx_hash)
    i += 1
    data_no += 1

# Check to ensure all the contract payment transactions has been mined
# Before proceeding to confirming receipt with the contract
print("Checking to ensure all payment transactions have been mined")
for tx_hash in pending_txn:
    miner_w3.eth.waitForTransactionReceipt(tx_hash)
print("All payment transaction has been mined")

# Consumer pays the smart contract
pending_txn = []
i = 0
data_no = 1
for data_txn in energy_data:
    consumer_id = data_txn[data.constants.CONSUMER_ID_KEY]
    energy_usage = data_txn[data.constants.ENERGY_KEY]
    consumer_user_id = prosumer_to_user_dict[consumer_id]
    consumer_w3 = w3_dict[consumer_user_id]

    consumer_w3.geth.personal.unlockAccount(consumer_w3.eth.coinbase, password)
    baseline = consumer_w3.eth.contract(
        address=contract_add[i],
        abi=abi
    )

    # Consumer confirms receipt
    if not baseline.functions.isPaid().call():
        print("The contract should have already been paid fully")
        exit()

    print("Consumer confirming receipt for Transaction {}".format(data_no))
    tx_hash = baseline.functions.confirmReceipt().transact({
        'from': consumer_w3.eth.coinbase
    })
    time_sent = time.time()
    logger.log_baseline_time_sent(simulation_name, time_sent, consumer_w3.eth.coinbase, tx_hash)

    pending_txn.append(tx_hash)
    i += 1
    data_no += 1

# Check to ensure all the receipt confirmation transactions has been mined
# Before proceeding to completing the simulation
contract_add = []
print("Checking to ensure all payment transactions have been mined")
for tx_hash in pending_txn:
    miner_w3.eth.waitForTransactionReceipt(tx_hash)
print("All payment transaction has been mined")

# Wait for all poller process to complete running before closing main process
poller_process.join()

print("Baseline simulation completed")

# Kill all ethereum nodes
subprocess.call("./scripts/kill_eth_nodes.sh")