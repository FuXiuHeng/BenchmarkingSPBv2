import matplotlib.pyplot as plt 
import os

# Settings
base_dir = 'log'
batch_name = 'run2'
data_file_name = 'file1'
data_ranges = [28259, 30000, 45000, 70000]

# Check if all necessary folders and files exists based on settings
log_dirs = []
for i in range(0, len(data_ranges) - 1):
    range_start = data_ranges[i]
    range_end = data_ranges[i + 1]

    dir_name = '{}/{}_{}_{}_{}'.format(base_dir, batch_name, data_file_name, range_start, range_end)
    log_dirs.append(dir_name)

for d in log_dirs:
    if not os.path.isdir(d): 
        raise Exception('Directory {} does not exists'.format(d))
    log_path = '{}/results/mining_time.log'.format(d)
    if not os.path.isfile(log_path):
        raise Exception('File {} does not exists'.format(log_path))

# Parse the mining_time.log
all_txn_no = []
all_mining_time = []
txn_no = data_ranges[0]
for d in log_dirs:
    with open('{}/results/mining_time.log'.format(d), 'r') as f:
        lines = f.readlines()
        for line in lines:
            mining_time = float(line.split(' ', 1)[0])
            all_txn_no.append(txn_no)
            all_mining_time.append(mining_time)
            txn_no = txn_no + 1
           
# Plot the graph: mining times against transaction no.
subtitle = "Batch: '{}', File: '{}', Partial runs: [{}]".format(batch_name, data_file_name, ', '.join(str(r) for r in data_ranges))
plt.plot(all_txn_no, all_mining_time)
plt.xlabel('Transaction No.')
plt.ylabel('Mining Time (s)')
plt.suptitle('Time Taken to Mine a Transaction Incrementally', fontsize=16)
plt.title(subtitle, fontsize=10)
plt.show()