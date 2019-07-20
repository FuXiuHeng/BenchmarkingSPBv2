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
    simulation_name = settings["simulation_name"]

    # Etherem settings
    miner_rpc_port = settings['miner_rpc_port']
    password = settings['password']

    # Overlay network settings
    miner_erc_overlay_port = settings['miner_erc_overlay_port']
    local_host = socket.gethostname()
    node_name = 'miner_erc'

    # Database settings
    db_host = settings["db_host"]
    db_user = settings["db_user"]
    db_password = settings["db_password"]

    # Welcome message
    # logger.log(simulation_name, node_name, 'Running {} overlay node'.format(node_name))
    # print('Running {} overlay node'.format(node_name))

    # Starting server to listen to ERC
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((local_host, miner_erc_overlay_port))

    # Connecting to miner ethereum node
    w3 = web3.Web3(web3.Web3.HTTPProvider('http://127.0.0.1:{}'.format(miner_rpc_port)))
    # logger.log(simulation_name, node_name, 'Connected to miner ethereum node via RPC')
    # print('Connected to miner ethereum node via RPC')

    while True:
        # Listening for ERC
        # logger.log(simulation_name, node_name, 'Listening for ERC on port {}'.format(miner_erc_overlay_port))
        # print('Listening for ERC on port {}'.format(miner_erc_overlay_port))
        s.listen(5)
        miner_ctp_conn, addr = s.accept()
        # logger.log(simulation_name, node_name, 'Connected by {}'.format(addr))
        # print('Connected by {}'.format(addr))

        while True:
            # Parse packet header
            header_packet = communications.receive_message_header(miner_ctp_conn)

            if header_packet == constants.ERC:
                pass
                # logger.log(simulation_name, node_name, 'Received ERC')
                # print('Received ERC')
            elif header_packet == constants.END:
                miner_ctp_conn.close()
                s.close()
                # logger.log(simulation_name, node_name, 'Closed current connection')
                # logger.log(simulation_name, node_name, 'End of simulation')
                # print('Closed current connection')
                # print('End of simulation')
                exit()
            elif header_packet == b'':
                miner_ctp_conn.close()
                # logger.log(simulation_name, node_name, 'Closed current connection')
                # print('Closed current connection')
                break
            else:
                miner_ctp_conn.close()
                s.close()
                # logger.log(simulation_name, node_name, 'Received this header packet {}'.format(header_packet)) 
                # logger.log(simulation_name, node_name, 'Exception: Should not receive anything other than ERC')
                # print('Received this header packet {}'.format(header_packet))
                raise Exception('Should not receive anything other than ERC')

            # Receive the message body (CTP ID)
            ctp_id = communications.receive_message_body(miner_ctp_conn)

            # Mine CTP for the given CTP ID
            db = ctp_database.connect_database(db_host, db_user, db_password)
            db_entry = ctp_database.get_ctp(db, ctp_id)
            raw_txn_hex_str = db_entry[ctp_database.RAW_TXN_INDEX]
            raw_txn = bytes.fromhex(raw_txn_hex_str[2:])
            w3.eth.sendRawTransaction(raw_txn)
            # logger.log(simulation_name, node_name, 'Sent ethereum transactions for the CTP_ID {}'.format(ctp_id))
            # print('Sent ethereum transactions for the CTP_ID {}'.format(ctp_id))

            # Log CTP sent time
            time_sent = time.time()
            from_addr = db_entry[ctp_database.FROM_ADDR_INDEX]
            txn_hash_hex_str = db_entry[ctp_database.TXN_HASH_INDEX]
            txn_hash = bytes.fromhex(txn_hash_hex_str[2:])

            logger.log_time_sent(simulation_name, time_sent, from_addr, txn_hash)
            # logger.log(simulation_name, node_name, 'Logged time transaction is sent')
            # print('Logged time transaction is sent')

    s.close()
