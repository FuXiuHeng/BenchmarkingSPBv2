import sys
import os
import math
    
# Column index constants for log files
TIME_GAS_COL = 0 # Used for both time and gas
PK_COL = 1
TXN_COL = 2

# Takes in a log file path for either time or gas 
# And creates a dictionary with key-value pair format:
# { txn_hash : time or gas }
def log_to_dict(log_path):
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

if __name__ == "__main__":
    # Script usage check
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print('Error: Invalid number of arguments.')
        print('Usage: python3 process_logs.py (spb | baseline) (all | ALL | __simulation_name__) [-f]')
        exit()
    
    input_simulation_type = sys.argv[1]
    input_simulation_name = sys.argv[2]

    if input_simulation_type != "spb" and input_simulation_type != "baseline":
        print("Input simulation type must be either 'spb' or 'baseline")
        exit()

    if len(sys.argv) == 4 and sys.argv[3] == "-f":
        force_flag = True
    else:
        force_flag = False

    simulation_list = []
    # Process all unprocessed logs in the log directory
    if input_simulation_name == 'all' or input_simulation_name == 'ALL':
        for simulation_name in os.listdir('./log/{}'.format(input_simulation_type)):
            simulation_list.append(simulation_name)
 
    # Process only the log of the specified simulation name
    else: 
        simulation_list.append(input_simulation_name)

    for simulation_name in simulation_list:
        log_dir = './log/{}/{}'.format(input_simulation_type, simulation_name)

        # Check if specified simulation name exists
        if not os.path.isdir(log_dir):
            print('Warning: The directory {} does not exist.'.format(log_dir))
            continue
        
        time_sent_path = '{}/time_sent.log'.format(log_dir)
        time_mined_path = '{}/time_mined.log'.format(log_dir)
        gas_used_path = '{}/gas_used.log'.format(log_dir)
        mining_time_path = '{}/mining_time.log'.format(log_dir)
        final_result_path = '{}/final_result.log'.format(log_dir)

        if not force_flag and os.path.exists(final_result_path):
            print('Warning: {} already exists. Skipping the generation of this result file'.format(final_result_path))

        time_sent_dict = log_to_dict(time_sent_path)
        time_mined_dict = log_to_dict(time_mined_path)
        gas_used_dict = log_to_dict(gas_used_path)
        time_sent_keys = list(time_sent_dict.keys())
        time_mined_keys = list(time_mined_dict.keys())
        gas_used_keys = list(gas_used_dict.keys())

        if len(time_sent_keys) != len(time_mined_keys) or len(time_sent_keys) != len(gas_used_keys):
            print('Warning: Inconsistent number of transactions between time_sent and time_mined logs')
            print('time_sent log: {}'.format(time_sent_path))
            print('time_mined log: {}'.format(time_mined_path))
            print('gas_used log: {}'.format(gas_used_path))
            continue

        mining_time_dict = {}
        total_mining_time = 0
        num_txn = len(time_sent_keys)
        
        # Computing total mining time and mean mining time
        with open(mining_time_path, 'w+') as f:
            for txn_hash in time_sent_keys:
                if txn_hash not in time_mined_dict:
                    print('Warning: Inconsistency between time_sent and time_mined logs.')
                    print('{} exists in time_sent log but not in time_mined log.')
                    print('time_sent log: {}'.format(time_sent_path))
                    print('time_mined log: {}'.format(time_mined_path))
                    continue

                time_sent = time_sent_dict[txn_hash]
                time_mined = time_mined_dict[txn_hash]
                mining_time = float(time_mined) - float(time_sent)
                total_mining_time += mining_time
                mining_time_dict[txn_hash] = mining_time

                f.write("{} {}".format(mining_time, txn_hash))

        mean_mining_time = total_mining_time / num_txn

        # Computing standard deviation and variance of mining time
        variance_mining_time = 0
        for txn_hash in time_sent_keys:
            time_sent = time_sent_dict[txn_hash]
            time_mined = time_mined_dict[txn_hash]
            mining_time = float(time_mined) - float(time_sent)
            diff = mining_time - mean_mining_time
            variance_mining_time += diff * diff
        
        variance_mining_time = variance_mining_time / (num_txn - 1)
        sd_mining_time = math.sqrt(variance_mining_time)

        # Computing total gas used and mean gas used
        total_gas_used = 0
        for txn_hash in gas_used_dict:
            total_gas_used += int(gas_used_dict[txn_hash])

        mean_gas_used = total_gas_used / num_txn

        # Computing standard deviation and variance of gas used
        variance_gas_used = 0
        for txn_hash in gas_used_dict:
            diff = int(gas_used_dict[txn_hash]) - mean_gas_used
            variance_gas_used += diff * diff

        variance_gas_used = variance_gas_used / (num_txn - 1)
        sd_gas_used = math.sqrt(variance_gas_used)

        # Writing results to file
        with open(final_result_path, 'w+') as f:
            f.write("Number of transactions: {}\n".format(num_txn))
            f.write("\n")
            f.write("Mining Time in seconds\n")
            f.write("----------------------------------------------\n")
            f.write("Total              : {}\n".format(total_mining_time))
            f.write("Mean               : {}\n".format(mean_mining_time))
            f.write("Variance           : {}\n".format(variance_mining_time))
            f.write("Standard deviation : {}\n".format(sd_mining_time))
            f.write("\n")
            f.write("Gas Used in seconds\n")
            f.write("----------------------------------------------\n")
            f.write("Total              : {}\n".format(total_gas_used))
            f.write("Mean               : {}\n".format(mean_gas_used))
            f.write("Variance           : {}\n".format(variance_gas_used))
            f.write("Standard deviation : {}\n".format(sd_gas_used))
            f.write("\n")

        # Baseline ONLY - split the gas_used metrics into three parts:
        # gas used in contract creation, payment to contract & contract payment to producer
        if input_simulation_type == "baseline":
            total_gas_contract_creation = 0
            total_gas_contract_payment = 0
            total_gas_producer_payment = 0

            num_txn_per_part = num_txn / 3
            txn_counter = 0
            for txn_hash in gas_used_dict:
                if txn_counter < num_txn_per_part:
                    total_gas_contract_creation += int(gas_used_dict[txn_hash])
                elif txn_counter < 2 * num_txn_per_part:
                    total_gas_contract_payment += int(gas_used_dict[txn_hash])
                else:
                    total_gas_producer_payment += int(gas_used_dict[txn_hash])
                
                txn_counter += 1

            mean_gas_contract_creation = total_gas_contract_creation / num_txn_per_part
            mean_gas_contract_payment = total_gas_contract_payment / num_txn_per_part
            mean_gas_producer_payment = total_gas_producer_payment / num_txn_per_part

            # Computing standard deviation and variance of gas used
            variance_gas_contract_creation = 0
            variance_gas_contract_payment = 0
            variance_gas_producer_payment = 0

            txn_counter = 0
            for txn_hash in gas_used_dict:
                if txn_counter < num_txn_per_part:                            
                    diff = int(gas_used_dict[txn_hash]) - mean_gas_contract_creation
                    variance_gas_contract_creation += diff * diff

                elif txn_counter < 2 * num_txn_per_part:             
                    diff = int(gas_used_dict[txn_hash]) - mean_gas_contract_payment
                    variance_gas_contract_payment += diff * diff

                else:             
                    diff = int(gas_used_dict[txn_hash]) - mean_gas_producer_payment
                    variance_gas_producer_payment += diff * diff

                txn_counter += 1

            variance_gas_contract_creation /= (num_txn_per_part - 1)
            variance_gas_contract_payment /= (num_txn_per_part - 1)
            variance_gas_producer_payment /= (num_txn_per_part - 1)

            sd_gas_contract_creation = math.sqrt(variance_gas_contract_creation)
            sd_gas_contract_payment = math.sqrt(variance_gas_contract_payment)
            sd_gas_producer_payment = math.sqrt(variance_gas_producer_payment)

            with open(final_result_path, 'a+') as f:
                f.write("Gas Used split into three parts:\n")
                f.write("----------------------------------------------\n")
                f.write("[Part 1: Contract Creation]\n")
                f.write("----------------------------------------------\n")
                f.write("Total              : {}\n".format(total_gas_contract_creation))
                f.write("Mean               : {}\n".format(mean_gas_contract_creation))
                f.write("Variance           : {}\n".format(variance_gas_contract_creation))
                f.write("Standard deviation : {}\n".format(sd_gas_contract_creation))
                f.write("----------------------------------------------\n")
                f.write("[Part 2: Contract Payment]\n")
                f.write("----------------------------------------------\n")
                f.write("Total              : {}\n".format(total_gas_contract_payment))
                f.write("Mean               : {}\n".format(mean_gas_contract_payment))
                f.write("Variance           : {}\n".format(variance_gas_contract_payment))
                f.write("Standard deviation : {}\n".format(sd_gas_contract_payment))
                f.write("----------------------------------------------\n")
                f.write("[Part 3: Producer Payment]\n")
                f.write("----------------------------------------------\n")
                f.write("Total              : {}\n".format(total_gas_producer_payment))
                f.write("Mean               : {}\n".format(mean_gas_producer_payment))
                f.write("Variance           : {}\n".format(variance_gas_producer_payment))
                f.write("Standard deviation : {}\n".format(sd_gas_producer_payment))
                f.write("\n")
       
