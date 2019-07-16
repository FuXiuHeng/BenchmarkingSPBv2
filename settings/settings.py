from datetime import datetime 

settings = {
    # Simulation settings
    "num_users": 3,
    "simulation_date_time": datetime.now(),
    "energy_price": 0.01,

    # Data settings
    "data_path": './data/energy_usage_data/separated_users/user1/user1.mat',
    "fake_data": True, # If true, the above data_path won't be used
    "num_fake_data": 5,

    # Path settings
    "pk_dir_path": "private_keys",
    "eth_dir_path": "eth_nodes",
    "genesis_path": "settings/genesis.json",

    # Database settings
    "db_host": "localhost",
    "db_user": "root",
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
