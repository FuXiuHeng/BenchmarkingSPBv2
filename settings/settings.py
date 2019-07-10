settings = {
    # Simulation settings
    "simulation_id": 1,
    "num_users": 3,

    # Path settings
    "pk_dir_path": "private_keys",
    "eth_dir_path": "eth_nodes",
    "genesis_path": "settings/genesis.json",

    # Ethereum node port allocations
    "miner_eth_port": 30301,
    "user_eth_port_start": 30302,

    # Ethereum node RPC port allocations
    "miner_rpc_port": 8001,
    "user_rpc_port_start": 8002,

    # Overlay network port allocations
    "miner_1_overlay_port": 24000,
    "miner_2_overlay_port": 24001,
    "consumer_overlay_port": 24002
}
