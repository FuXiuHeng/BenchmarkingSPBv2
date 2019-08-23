#!/bin/bash
source ./settings/settings.sh

USER_NODES=`seq -f "user%02g" $num_users` 
OTHER_NODES="miner"
ALL_NODES="$OTHER_NODES $USER_NODES"

# Prepare the address:port of each node
localhost=http://127.0.0.1
declare -A eth_port
declare -A rpc_port
declare -A rpc_addr
for node in $OTHER_NODES
do
    eth_port_var="${node}_eth_port"
    rpc_port_var="${node}_rpc_port"
    eth_port[$node]=${!eth_port_var}
    rpc_port[$node]=${!rpc_port_var}
    rpc_addr[$node]=$localhost:${!rpc_port_var}
done

i=0
for node in $USER_NODES
do
    eth_port[$node]=$(( $user_eth_port_start + $i ))
    rpc_port[$node]=$(( $user_rpc_port_start + $i ))
    rpc_addr[$node]=$localhost:${rpc_port[$node]}
    i=$(( $i + 1 ))
done

# Start all nodes in the network
for node in $ALL_NODES
do
    nohup geth --nousb --datadir eth_nodes/$node --port ${eth_port[$node]} --rpc --rpcapi="db,eth,net,web3,personal,admin,miner" --rpcaddr 127.0.0.1 --rpcport ${rpc_port[$node]} --rpccorsdomain "*" --networkid 881188 --nat extip:127.0.0.1 --allow-insecure-unlock --nodiscover 1>/dev/null 2>/dev/null &
done
echo "Started running all nodes in background"

# Sleep until all nodes have completely started
echo "Waiting for all nodes to be ready"
sleep 3

# Get enode information
declare -A enode
for node in $ALL_NODES
do 
    enode[$node]=`geth attach ${rpc_addr[$node]} --exec 'admin.nodeInfo.enode'`
done
echo "Collected enodes of all nodes"


# Connect all the nodes together as peers
for main_node in $ALL_NODES
do
    add_peer_command=""
    for peer_node in $ALL_NODES
    do
        if [ $main_node != $peer_node ] 
        then
            add_peer_command="
                ${add_peer_command}
                admin.addPeer(${enode[$peer_node]})
            "
        fi
    done
    # e.g.
    #   geth attach MAIN_NODE_ADDRESS --exec "
    # 	    admin.addPeer(SIDE_NODE_1_ENODE)
    # 	    admin.addPeer(SIDE_NODE_2_ENODE)
    #       ...
    # 	    admin.addPeer(SIDE_NODE_N_ENODE)
    #   "
    add_successful=`geth attach ${rpc_addr[$main_node]} --exec "$add_peer_command"`
    
    # Check if successfully added peers
    if [ "$add_successful" != "true" ]
    then
        echo -e "\033[0;31m\e[1mError\033[0m: Unable to add peers to node $main_node"
        exit
    fi
done
echo "Connected all nodes to one another as peers"


# Start mining in miner node
geth attach ${rpc_addr[miner]} --exec "
	personal.unlockAccount(web3.eth.coinbase, 'test', 15000)
	miner.start()
" > /dev/null
echo "Started mining in miner node"
