import matplotlib.pyplot as plt 
import os
import re
import sys

# Line indexing constants for final_result.log
MEAN_MINING_TIME_LINE_NO = 5
SD_MINING_TIME_LINE_NO = 7

# Plot the mining time in desired log directory name
# Usage:
#   python3 plot_mining_time.py <simulation_name> [<title> <subtitile>]
if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) >= 6:
        print('Error: Invalid number of arguments to the script.')
        print('Usage:')
        print('  python3 plot_mining_time.py (spb | baseline) <simulation_name> [<title> <subtitle>]')
        exit()
    
    simulation_type = sys.argv[1]
    simulation_name = sys.argv[2]
    if len(sys.argv) >= 4:
        title = sys.argv[3]
    else:
        title = "Time Taken to Mine a Transaction"
    if len(sys.argv) >= 5:
        subtitle = sys.argv[4]
    else:
        subtitle = "Plot generated from log: {}".format(simulation_name)
        
    file_path = './log/{}/{}/mining_time.log'.format(simulation_type, simulation_name)
    result_path = './log/{}/{}/final_result.log'.format(simulation_type, simulation_name)
    if not os.path.isfile(file_path):
        raise Exception('File {} does not exist'.format(file_path))
    if not os.path.isfile(result_path):
        raise Exception('File {} does not exist. Please process the logs first.'.format(result_path))
    
    # Parse the mining_time.log and collect the mining time data for plotting
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

    # Extract the pre-computed mean and standard deviation of the mining time
    with open(result_path, 'r') as f:
        lines = f.readlines()
        mean_line = lines[MEAN_MINING_TIME_LINE_NO]
        sd_line = lines[SD_MINING_TIME_LINE_NO]

        mean = float(re.findall("[0-9]+\.[0-9]+", mean_line)[0])
        sd = float(re.findall("[0-9]+\.[0-9]+", sd_line)[0])

    # Plot the graph: mining times against transaction no.
    plt.plot(all_txn_no, all_mining_time)
    plt.xlabel('Transaction No.')
    plt.ylabel('Mining Time (s)')
    plt.suptitle(title, fontsize=16)
    plt.title(subtitle, fontsize=10)
    plt.subplots_adjust(bottom=0.18)
    text = "Mean = {0:.3f}, Standard Deviation = {1:.3f}".format(mean, sd)
    plt.figtext(0.5,0.05, text, fontsize=9, va="top", ha="center")
    plt.savefig("./plots/{}.png".format(simulation_name))
    plt.show()