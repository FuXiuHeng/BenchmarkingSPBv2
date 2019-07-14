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
        print('Listening for CTP and ERC on port {}'.format(miner_ctp_overlay_port))
        s.listen(5)
        conn, addr = s.accept()
        print('Connected by {}'.format(addr))

        while True:
            # Parse packet header
            header_packet = conn.recv(constants.HEADER_BYTES)
            if header_packet == constants.CTP:
                print('Received CTP')
            elif header_packet == constants.END:
                print('No more CTP received from the current connection')
                conn.close()
                print('Closed current connection')
                break
            else:
                print('Received this header packet {}'.format(header_packet))
                raise Exception('Should not receive anything other than CTP')

            # Parse size of data
            size_packet = conn.recv(struct.calcsize("i"))
            size = struct.unpack("i", size_packet)[0]

            # Receive data of the specified size
            buff = []
            acc_size = 0
            while acc_size < size:
                msg = conn.recv(size - acc_size)
                acc_size += len(msg)
                if not msg:
                    print("GGGG")
                    break
                buff.append(msg)

            # Unpickle ddata - convert from byte stream to python object
            serialised_ctp = b"".join(buff)
            ctp = pickle.loads(serialised_ctp)

            # Store CTP into database
            raw_txn = ctp.rawTransaction
            txn_hash = ctp.hash
            from_addr = w3.eth.account.recoverTransaction(raw_txn)
            ctp_id = ctp_database.insert_ctp(db, str(from_addr), raw_txn.hex(), txn_hash.hex())

            print(ctp_id)
            # Signals the receipt of CTP, by sending the CTP_ID
            # miner_erc_conn = socket.socket()
            # miner_erc_conn.connect((local_host, miner_erc_overlay_port))
            # print('Connected to miner_erc: {}'.format((local_host, miner_erc_overlay_port)))

            # serialised_ctp_id = pickle.dumps(ctp_id)
            # miner_erc_conn.sendall(
            #     constants.CTP_SIGNAL
            #     + struct.pack("i", len(serialised_ctp_id)
            #     + serialised_ctp_id
            # )
            # print('Signaled CTP receipt to miner_erc')

    print(constants.END)
    s.close()
