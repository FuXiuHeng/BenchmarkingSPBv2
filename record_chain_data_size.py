#!/usr/bin/python3

import os
import sys

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Error: Invalid number of arguments to the script.')
        print('Usage:')
        print('  python3 record_chain_data_size.py (spb | baseline) <simulation_name>')
        exit()
    
    simulation_type = sys.argv[1]
    simulation_name = sys.argv[2]

    chain_data_path = os.path.join(".", "eth_nodes", "miner", "geth", "chaindata")
    chain_data_size = os.path.getsize(chain_data_path)

    result_path = os.path.join(".", "log", simulation_type, simulation_name, "chain_data_size.log")

    with open(result_path, "w+") as f:
        f.write("Chain data size: {} bytes\n".format(chain_data_size))