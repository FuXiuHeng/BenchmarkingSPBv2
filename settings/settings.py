from datetime import datetime 

settings = {
    # Simulation settings
    "num_users": 20, # Existing data has up to 85 unique users (use 86 to allow for 1 producer)
    # "simulation_name": datetime.now().strftime('%Y%m%d_%H%M_file1_70000_100000'),
    "simulation_name": datetime.now().strftime('%Y%m%d_%H%M_users_20_data_5000'),
    "energy_price": 0.00001,

    # Data settings
    "data_path": './data/generated/users_85_data_5000.txt', 

    # Partial data settings
    "use_partial_data": False, # If true, only run simulation with a subset of the data
    "partial_data_start": 0, # Start of the range of partial data to use
    "partial_data_end": 10000, # End of the range of partial data to use

    # Path settings
    "pk_dir_path": "private_keys",
    "eth_dir_path": "eth_nodes",
    "genesis_path": "settings/genesis.json",

    # Database settings
    "db_host": "localhost",
    "db_user": "fuxiu",
    "db_password": "",

    # Ethereum nodes settings
    "password": "test",

    # Ethereum network port allocations
    "miner_eth_port": 30301,
    "user_eth_port_start": 30302,

    # Ethereum network RPC port allocations
    "miner_rpc_port": 8001,
    "user_rpc_port_start": 8002,

    # Overlay network port allocations
    "poller_port": 24000,
    "miner_ctp_overlay_port": 24001,
    "miner_erc_overlay_port": 24002,
    "consumer_overlay_port": 24003
}
