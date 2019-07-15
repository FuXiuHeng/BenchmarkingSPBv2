#!/usr/bin/python

from attrdict import (
    AttrDict, # This import is necessary for the pickle.loads() step
)
import pickle
import socket
import struct
import time
import web3

import overlay_nodes.helper.constants as constants
import overlay_nodes.helper.ctp_database as ctp_database
import overlay_nodes.helper.logger as logger

def run(settings):
    # Simulation settings
    simulation_id = settings['simulation_id']

    # Etherem settings
    miner_rpc_port = settings['miner_rpc_port']
    password = settings['password']

    # Overlay network settings
    miner_erc_overlay_port = settings['miner_erc_overlay_port']
    local_host = socket.gethostname()

    # Database settings
    db_host = settings["db_host"]
    db_user = settings["db_user"]
    db_password = settings["db_password"]

    # Welcome message
    print('Running miner_erc overlay node')

    # Starting server to listen to ERC
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((local_host, miner_erc_overlay_port))

    # Connecting to miner ethereum node
    w3 = web3.Web3(web3.Web3.HTTPProvider('http://127.0.0.1:{}'.format(miner_rpc_port)))
    print('Connected to miner ethereum node via RPC')

    while True:
        # Listening for ERC
        print('Listening for ERC on port {}'.format(miner_erc_overlay_port))
        s.listen(5)
        miner_ctp_conn, addr = s.accept()
        print('Connected by {}'.format(addr))

        while True:
            # Parse packet header
            header_packet = miner_ctp_conn.recv(constants.HEADER_BYTES)
            if header_packet == constants.ERC:
                print('Received ERC')
            elif header_packet == constants.END or header_packet == b'':
                miner_ctp_conn.close()
                print('Closed current connection')
                break
            else:
                miner_ctp_conn.close()
                s.close()
                print('Received this header packet {}'.format(header_packet))
                raise Exception('Should not receive anything other than ERC')

            # Parse size of data
            size_packet = miner_ctp_conn.recv(struct.calcsize("i"))
            size = struct.unpack("i", size_packet)[0]

            # Receive data of the specified size
            buff = []
            acc_size = 0
            while acc_size < size:
                msg = miner_ctp_conn.recv(size - acc_size)
                acc_size += len(msg)
                if not msg:
                    break
                buff.append(msg)
            
            # Unpickle data - convert from byte stream to python object
            serialised_ctp_id = b"".join(buff)
            ctp_id = pickle.loads(serialised_ctp_id)

            # Mine CTP for the given CTP ID
            db = ctp_database.connect_database(db_host, db_user, db_password)
            db_entry = ctp_database.get_ctp(db, ctp_id)
            raw_txn_hex_str = db_entry[ctp_database.RAW_TXN_INDEX]
            raw_txn = bytes.fromhex(raw_txn_hex_str[2:])
            w3.eth.sendRawTransaction(raw_txn)
            print('Sent ethereum transactions for the CTP_ID {}'.format(ctp_id))

            # Log CTP sent time
            time_sent = time.time()
            from_addr = db_entry[ctp_database.FROM_ADDR_INDEX]
            txn_hash_hex_str = db_entry[ctp_database.TXN_HASH_INDEX]
            txn_hash = bytes.fromhex(txn_hash_hex_str[2:])
            logger.log_time_sent(simulation_id, time_sent, from_addr, txn_hash)

    s.close()
