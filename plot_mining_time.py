import matplotlib.pyplot as plt 
import os
import sys

# Plot the mining time in desired log directory name
# Usage:
#   python3 plot_mining_time.py <log_dir_name> [<title> <subtitile>]

if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) >= 5:
        print('Error: Invalid number of arguments to the script.')
        print('Usage:')
        print('  python3 plot_mining_time.py <log_dir_name> [<title> <subtitle>]')
        exit()
    
    log_dir_name = sys.argv[1]
    if len(sys.argv) >= 3:
        title = sys.argv[2]
    else:
        title = "Time Taken to Mine a Transaction"
    if len(sys.argv) >= 4:
        subtitle = sys.argv[3]
    else:
        subtitle = "Plot generated from log: {}".format(log_dir_name)
        
    file_path = './log/{}/results/mining_time.log'.format(log_dir_name)
    if not os.path.isfile(file_path):
        raise Exception('File {} does not exist'.format(file_path))
    
    # Parse the mining_time.log
    all_txn_no = []
    all_mining_time = []
    txn_no = 0
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            mining_time = float(line.split(' ', 1)[0])
            all_txn_no.append(txn_no)
            all_mining_time.append(mining_time)
            txn_no = txn_no + 1
           
    # Plot the graph: mining times against transaction no.
    plt.plot(all_txn_no, all_mining_time)
    plt.xlabel('Transaction No.')
    plt.ylabel('Mining Time (s)')
    plt.suptitle(title, fontsize=16)
    plt.title(subtitle, fontsize=10)
    plt.show()