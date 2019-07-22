import sys
import os

# Column index constants for log files
TIME_GAS_COL = 0 # Used for both time and gas 
PK_COL = 1
TXN_COL = 2

# Takes in a log file path for either time_
def log_to_dict(log_path):
    # Store info in dictionary with key-value pair format:
    # { txn_hash : time or gas }
    result_dict = {}

    f = open(log_path)
    lines = f.readlines()
    for l in lines:
        data = l.split(' ', 2)
        time_gas = data[TIME_GAS_COL]
        txn_hash = data[TXN_COL]

        result_dict[txn_hash] = time_gas

    f.close()
    return result_dict

def process_mining_time(time_sent_path, time_mined_path):
    time_sent_dict = log_to_dict(time_sent_path)
    time_mined_dict = log_to_dict(time_mined_path)
    
    time_sent_keys = list(time_sent_dict.keys())
    time_mined_keys = list(time_mined_dict.keys())

    if len(time_sent_keys) != len(time_sent_keys):
        print('Error: Inconsistent number of transactions between time_sent and time_mined logs')
        print('time_sent log: {}'.format(time_sent_path))
        print('time_mined log: {}'.format(time_mined_path))
        exit()

    mining_time_dict = {}
    total_mining_time = 0
    for txn_hash in time_sent_keys:
        if txn_hash not in time_mined_dict:
            print('Error: Inconsistency between time_sent and time_mined logs.')
            print('{} exists in time_sent log but not in time_mined log.')
            print('time_sent log: {}'.format(time_sent_path))
            print('time_mined log: {}'.format(time_mined_path))
            exit()
        
        time_sent = time_sent_dict[txn_hash]
        time_mined = time_mined_dict[txn_hash]
        mining_time = float(time_mined) - float(time_sent)
        total_mining_time += mining_time

        mining_time_dict[txn_hash] = mining_time
    
    return total_mining_time, len(time_sent_keys), mining_time_dict

def write_result(result_path, mining_time_path, total_mining_time, total_gas_used, num_data, mining_time_dict):
    if not os.path.exists(result_path):
        f = open(result_path, 'w+')
        f.write('num_data: {}\n'.format(num_data))
        f.write('total_mining_time: {} seconds\n'.format(total_mining_time))
        f.write('total_gas_used: {} gas\n'.format(total_gas_used))
        f.write('average_mining_time: {} seconds\n'.format(total_mining_time / num_data))
        f.write('average_gas_used: {} gas\n'.format(total_gas_used / num_data))
        f.close()
        print('Final results written into {}'.format(result_path))
    else: 
        print('Warning: {} already exists. Generation of this file is skipped'.format(result_path))
    
    if not os.path.exists(mining_time_path):
        f = open(mining_time_path, 'w+')
        for txn in mining_time_dict:
            f.write('{} {}'.format(mining_time_dict[txn], txn))
        f.close()
        print('Mining time results written into {}'.format(mining_time_path))
    else: 
        print('Warning: {} already exists. Generation of this file is skipped'.format(mining_time_path))

def process_gas_used(gas_used_path):
    gas_used_dict = log_to_dict(gas_used_path)

    total_gas_used = 0
    for txn_hash in gas_used_dict:
        total_gas_used += int(gas_used_dict[txn_hash])

    return total_gas_used, len(gas_used_dict.keys()), gas_used_dict


def process_simulation_logs(simulation_name):
    log_dir = './log/{}'.format(simulation_name)

    # Check if specified simulation name exists
    if not os.path.isdir(log_dir):
        print('Error: No directory named {}'.format(log_dir))
        print('Ensure the specified simulation name exists')
        exit()

    time_sent_path = '{}/results/time_sent.log'.format(log_dir)
    time_mined_path = '{}/results/time_mined.log'.format(log_dir)
    gas_used_path = '{}/results/gas_used.log'.format(log_dir)
    mining_time_path = '{}/results/mining_time.log'.format(log_dir)
    final_result_path = '{}/results/final_result.log'.format(log_dir)

    # Processing the logs to compute the total mining time and gas used
    total_mining_time, num_data_1, mining_time_dict = process_mining_time(time_sent_path, time_mined_path)
    total_gas_used, num_data_2, gas_used_dict = process_gas_used(gas_used_path)

    if num_data_1 != num_data_2:
        print('Error: Inconsistency between time logs and gas logs.')
        exit()

    # Writing to result
    write_success = write_result(final_result_path, mining_time_path, total_mining_time, total_gas_used, num_data_1, mining_time_dict)
    print('Completed processing logs for {}'.format(simulation_name))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Error: Invalid number of arguments.')
        print('Usage: python3 process_logs.py (all | ALL | __simulation_name__)')
        exit()

    input_simulation_name = sys.argv[1]

    # Process all unprocessed logs in the logs directory
    if input_simulation_name == 'all' or input_simulation_name == 'ALL':
        for simulation_name in os.listdir('./log'):
            process_simulation_logs(simulation_name)

    # Process only the log of the specified simulation name
    else:
        process_simulation_logs(input_simulation_name)