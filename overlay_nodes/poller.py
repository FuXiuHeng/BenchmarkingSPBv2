import time
import web3

import overlay_nodes.helper.logger as logger

def run(settings):
    # Simulation settings
    simulation_id = settings['simulation_id']

    # Ethereum settings
    user01_rpc_port = settings['user_rpc_port_start']
    password = settings['password']

    # Connecting to user01 ethereum node
    w3 = web3.Web3(web3.Web3.HTTPProvider('http://127.0.0.1:{}'.format(user01_rpc_port)))
    print('Connected to user01 ethereum node via RPC')

    # Create a filter for latest blocks mined for polling use
    latest_block_filter = w3.eth.filter('latest')

    # Polling for mined blocks to detect if any transactions has been mined
    while True:
        print('Polling for new mined transactions')    
        while True:
            latest_blocks = latest_block_filter.get_new_entries()
            time_mined = time.time()

            if latest_blocks:
                block = w3.eth.getBlock(latest_blocks[0])

                for txn in block.transactions:
                    print('Found new mined transaction: {}'.format(txn))
                    txn_receipt = w3.eth.getTransactionReceipt(txn)
                    from_addr = txn_receipt['from']
                    gas_used = txn_receipt['gasUsed']

                    # Log the time the block is mined
                    logger.log_time_mined(simulation_id, time_mined, from_addr, txn)
                    print('Logged CTP mined for transaction')

                    # Get the gas used by the transaction 
                    gas_used = w3.eth.getTransactionReceipt(txn)['gasUsed']
                    logger.log_gas_used(simulation_id, gas_used, from_addr, txn)
                    print('Logged gas used for transaction')
                    
                break
