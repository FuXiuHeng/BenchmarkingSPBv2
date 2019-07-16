import time
import web3

import overlay_nodes.helper.logger as logger

def run(settings):
    # Simulation settings
    simulation_date_time = settings["simulation_date_time"]

    # Ethereum settings
    user01_rpc_port = settings['user_rpc_port_start']
    password = settings['password']

    # Node settings
    node_name = 'poller'

    # Connecting to user01 ethereum node
    w3 = web3.Web3(web3.Web3.HTTPProvider('http://127.0.0.1:{}'.format(user01_rpc_port)))
    logger.log(simulation_date_time, node_name, 'Connected to user01 ethereum node via RPC')
    print('Connected to user01 ethereum node via RPC')

    # Create a filter for latest blocks mined for polling use
    latest_block_filter = w3.eth.filter('latest')

    # Polling for mined blocks to detect if any transactions has been mined
    while True:
        logger.log(simulation_date_time, node_name, 'Polling for new mined transactions')
        print('Polling for new mined transactions')    
        while True:
            latest_blocks = latest_block_filter.get_new_entries()
            time_mined = time.time()

            if latest_blocks:
                block = w3.eth.getBlock(latest_blocks[0])

                if block.transactions:
                    for txn in block.transactions:
                        logger.log(simulation_date_time, node_name, 'Found new mined transaction: {}'.format(txn))
                        print('Found new mined transaction: {}'.format(txn))
                        txn_receipt = w3.eth.getTransactionReceipt(txn)
                        from_addr = txn_receipt['from']
                        gas_used = txn_receipt['gasUsed']

                        # Log the time the block is mined
                        logger.log_time_mined(simulation_date_time, time_mined, from_addr, txn)
                        logger.log(simulation_date_time, node_name, 'Logged CTP mined for transaction')
                        print('Logged CTP mined for transaction')

                        # Get the gas used by the transaction 
                        gas_used = w3.eth.getTransactionReceipt(txn)['gasUsed']
                        logger.log_gas_used(simulation_date_time, gas_used, from_addr, txn)
                        logger.log(simulation_date_time, node_name, 'Logged gas used for transaction')
                        print('Logged gas used for transaction')
                        
                    break
