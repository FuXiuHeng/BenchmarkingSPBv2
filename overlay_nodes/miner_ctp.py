#!/usr/bin/python

from attrdict import (
    AttrDict, # This import is necessary for the pickle.loads() step
)
import pickle
import socket
import struct
import time
import web3

import overlay_nodes.helper.communications as communications
import overlay_nodes.helper.constants as constants
import overlay_nodes.helper.ctp_database as ctp_database
import overlay_nodes.helper.logger as logger

def run(settings):
    # Simulation settings
    simulation_id = settings['simulation_id']

    # Ethereum settings
    miner_rpc_port = settings["miner_rpc_port"]
    password = settings["password"]

    # Overlay network settings
    miner_ctp_overlay_port = settings["miner_ctp_overlay_port"]
    miner_erc_overlay_port = settings["miner_erc_overlay_port"]
    local_host = socket.gethostname()

    # Welcome message
    print("Running miner_ctp overlay node")

    # Initialising CTP database
    db_host = settings["db_host"]
    db_user = settings["db_user"]
    db_password = settings["db_password"]
    db = ctp_database.initialise_database(db_host, db_user, db_password)

    # Starting server to listen for CTP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((local_host, miner_ctp_overlay_port))

    # Connecting to miner ethereum node
    w3 = web3.Web3(web3.Web3.HTTPProvider('http://127.0.0.1:{}'.format(miner_rpc_port)))
    print('Connected to miner ethereum node via RPC')

    while True:
        # Listening for CTP
        print('Listening for CTP on port {}'.format(miner_ctp_overlay_port))
        s.listen(5)
        consumer_conn, addr = s.accept()
        print('Connected by {}'.format(addr))

        # Connect to miner_erc for sending ERC 
        miner_erc_conn = socket.socket()
        miner_erc_conn.connect((local_host, miner_erc_overlay_port))
        print('Connected to miner_erc: {}'.format((local_host, miner_erc_overlay_port)))

        while True:
            # Parse packet header
            header_packet = communications.receive_message_header(consumer_conn)
            if header_packet == constants.CTP:
                print('Received CTP')
            elif header_packet == constants.END or header_packet == b'':
                miner_erc_conn.sendall(constants.END)
                miner_erc_conn.close()
                consumer_conn.close()
                print('Closed current connection')
                break
            else:
                miner_erc_conn.close()
                consumer_conn.close()
                s.close()
                print('Received this header packet {}'.format(header_packet))
                raise Exception('Should not receive anything other than CTP')

            # Receive the message body (CTP transaction) 
            ctp = communications.receive_message_body(consumer_conn)

            # Store CTP into database
            raw_txn = ctp.rawTransaction
            txn_hash = ctp.hash
            from_addr = w3.eth.account.recoverTransaction(raw_txn)
            ctp_id = ctp_database.insert_ctp(db, str(from_addr), raw_txn.hex(), txn_hash.hex())
            print('Inserted CTP into the database: CTP_ID {}'.format(ctp_id))

            # Miner signals receipt of CTP to producer, which then sends energy to smart meter
            # Smart meter then sends ERC to miner upon complete energy receipt
            # This step ignores the transmission to the producer and the smart meter
            # Instead, we send an ERC straight back to the miner

            # Sends ERC to miner_erc, along with the relevant CTP ID
            communications.send_message(miner_erc_conn, constants.ERC, ctp_id)
            print('Sends ERC to miner_erc')

        miner_erc_conn.close()

    print(constants.END)
    s.close()
