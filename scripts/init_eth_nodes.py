import os
import shutil
import subprocess

def initialise_eth_node(node_name, eth_dir_path, genesis_path):
    cmd = "geth --nousb --verbosity 2 --datadir {}/{} init {}".format(eth_dir_path, node_name, genesis_path)
    ret = subprocess.call(cmd, shell=True)
    if ret:
        raise Exception('init_eth_nodes.py: Unable to initialise {} node'.format(node_name))

def initialise_eth_pk(node_name, eth_dir_path, pk_dir_path):
    src = "{}/{}".format(pk_dir_path, node_name)
    dst = "{}/{}/keystore/pk".format(eth_dir_path, node_name)
    shutil.copyfile(src, dst)

def run(settings):
    # Settings
    num_users = settings["num_users"]
    genesis_path = settings["genesis_path"]
    eth_dir_path = settings["eth_dir_path"]
    pk_dir_path = settings["pk_dir_path"]

    # Empty the ethereum nodes directory
    if os.path.exists(eth_dir_path) and os.path.isdir(eth_dir_path):
        shutil.rmtree(eth_dir_path)
    os.mkdir(eth_dir_path)
    
    # Reset the ethereum nodes
    initialise_eth_node("miner", eth_dir_path, genesis_path)
    for i in range(1, num_users + 1):
        initialise_eth_node("user{:02d}".format(i), eth_dir_path, genesis_path)
        
    # Copy private keys to nodes
    initialise_eth_pk("miner", eth_dir_path, pk_dir_path)
    for i in range(1, num_users + 1):
        initialise_eth_pk("user{:02d}".format(i), eth_dir_path, pk_dir_path)

    print("Completed init_eth_nodes.py: Initialised all ethereum nodes")
