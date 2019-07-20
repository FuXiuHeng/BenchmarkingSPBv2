import socket
import time
import web3

import overlay_nodes.helper.communications as communications
import overlay_nodes.helper.constants as constants
import overlay_nodes.helper.logger as logger

def run(settings):
    # Simulation settings
    simulation_name = settings["simulation_name"]

    # Ethereum settings
    user01_rpc_port = settings['user_rpc_port_start']
    password = settings['password']

    # Poller settings
    poller_port = settings["poller_port"]
    local_host = socket.gethostname()
    node_name = 'poller'

    # Welcome message
    logger.log(simulation_name, node_name, 'Running {} overlay node'.format(node_name))
    print('Running {} overlay node'.format(node_name))

    # Start socket to ilsten to number of transactions
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((local_host, poller_port))

    # Listening for information about how many transactions to look out for
    logger.log(simulation_name, node_name, 'Listening for number of transactions on port {}'.format(poller_port))
    print('Listening for number of transactions on port {}'.format(poller_port))
    s.listen(5)
    simulator_conn, addr = s.accept()
    logger.log(simulation_name, node_name, 'Connected by {}'.format(addr))
    print('Connected by {}'.format(addr))

    # Parsing packet header
    header_packet = communications.receive_message_header(simulator_conn)
    if header_packet == constants.NUM_TXN:
        logger.log(simulation_name, node_name, 'Received number of transactions')
        print('Received NUM_TXN')
    else:
        simulator_conn.close()
        s.close()
        logger.log(simulation_name, node_name, 'Received this header packet {}'.format(header_packet))
        logger.log(simulation_name, node_name, 'Exception: Should not receive anything other than NUM_TXN')
        print('Received this header packet {}'.format(header_packet))
        raise Exception('Should not receive anything other than NUM_TXN')

    # Parsing the number of transactions to look out for    
    total_txn = communications.receive_message_body(simulator_conn)
    logger.log(simulation_name, node_name, 'Received NUM_TXN: {}'.format(total_txn))
    print('Total number of transactions to poll for: {}'.format(total_txn))

    s.close()
    logger.log(simulation_name, node_name, 'Closed current connection')
    print('Closed current connection')

    # Connecting to user01 ethereum node
    w3 = web3.Web3(web3.Web3.HTTPProvider('http://127.0.0.1:{}'.format(user01_rpc_port)))
    logger.log(simulation_name, node_name, 'Connected to user01 ethereum node via RPC')
    print('Connected to user01 ethereum node via RPC')

    # Create a filter for latest blocks mined for polling use
    latest_block_filter = w3.eth.filter('latest')

    # Polling for mined blocks to detect if any transactions has been mined
    txn_count = 0
    while True:
        logger.log(simulation_name, node_name, 'Polling for new mined transactions')
        print('Polling for new mined transactions')    
        while True:
            latest_blocks = latest_block_filter.get_new_entries()
            time_mined = time.time()

            if latest_blocks:
                block = w3.eth.getBlock(latest_blocks[0])
                for block_entry in latest_blocks:
                    block = w3.eth.getBlock(block_entry)
                    if block.transactions:
                        for txn in block.transactions:
                            logger.log(simulation_name, node_name, 'Found new mined transaction: {}'.format(txn))
                            print('Found new mined transaction: {}'.format(txn))
                            txn_receipt = w3.eth.getTransactionReceipt(txn)
                            from_addr = txn_receipt['from']
                            gas_used = txn_receipt['gasUsed']

                            # Log the time the block is mined
                            logger.log_time_mined(simulation_name, time_mined, from_addr, txn)
                            logger.log(simulation_name, node_name, 'Logged CTP mined for transaction')
                            print('Logged CTP mined for transaction')

                            # Get the gas used by the transaction 
                            gas_used = w3.eth.getTransactionReceipt(txn)['gasUsed']
                            logger.log_gas_used(simulation_name, gas_used, from_addr, txn)
                            logger.log(simulation_name, node_name, 'Logged gas used for transaction')
                            print('Logged gas used for transaction')

                            txn_count += 1
                            if txn_count == total_txn:
                                logger.log(simulation_name, node_name, 'Finished polling all {} transactions'.format(total_txn))
                                logger.log(simulation_name, node_name, 'End of simulation')
                                print('Finished polling all {} transactions'.format(total_txn))
                                print('End of simulation')
                                exit()
                            
                        break
