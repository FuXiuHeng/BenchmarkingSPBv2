import subprocess
import sys

cmd = (
    "geth --datadir eth_nodes/user02 --port 8003 "
    "--rpc --rpcapi=\"eth,net,web3,personal,admin,miner\" "
    "--rpcaddr 127.0.0.1 --rpcport 20003 --rpccorsdomain \"*\" "
    "--networkid 881188 --nat extip:127.0.0.1 --nodiscover &"
)
# ret = subprocess.call(cmd, shell=True)

p = subprocess.Popen(['/bin/sh', '-c', cmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT); 
p.terminate()
print('finished')
