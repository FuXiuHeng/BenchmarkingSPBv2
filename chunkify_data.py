import os
import sys
from scipy.io import loadmat, whosmat

import data.constants as constants

# Run the script to chunkify the specified .mat energy usage file
# Usage: 
#   python3 chunkify_data.py <matlab_data_file_path> <dest_name> <max_data_per_chunk>
#
# Parse the given, original .mat data file, and divides up all the data into chunks of the given size.
# Each chunk of data will be written to a separate .txt file in a specified folder.
# Each line of data will contain only customer_id and the aggregated energy usage amount.
# If a chunks_limit is specified, the script terminates after creating that many chunks.

if __name__ == '__main__':
    if len(sys.argv) != 4 and len(sys.argv) != 5:
        print('Error: Invalid number of arguments to the script.')
        print('Usage:')
        print('  python3 chunkify_data.py <matlab_data_file_path> <dest_name> <max_data_per_chunk> [<chunks_limit>]')
        exit()
    
    matlab_data_file_path = sys.argv[1]
    dest_name = sys.argv[2]
    max_data_per_chunk = int(sys.argv[3])

    if len(sys.argv) == 5:
        has_chunks_limit = True
        chunks_limit = int(sys.argv[4])
    else: 
        has_chunks_limit = False

    print(matlab_data_file_path)
    print(dest_name)
    print(max_data_per_chunk)

    raw = loadmat(matlab_data_file_path)
    var_name = whosmat(matlab_data_file_path)[0][0]
    data = raw[var_name]

    dest_dir_path = os.path.join('./data/chunks', dest_name)
    os.makedirs(dest_dir_path, exist_ok=True)

    chunk_index = 1
    dest_file_path = os.path.join(dest_dir_path, 'chunk{:02d}.txt'.format(chunk_index))
    f = open(dest_file_path, 'w+')

    data_counter = 0
    for data_row in data:
        if data_counter >= max_data_per_chunk:
            data_counter = 0
            f.close()
            chunk_index += 1

            if has_chunks_limit and chunk_index > chunks_limit:
                exit()

            dest_file_path = os.path.join(dest_dir_path, 'chunk{:02d}.txt'.format(chunk_index))
            f = open(dest_file_path, 'w+')

        customer_id = int(data_row[constants.CUSTOMER_ID][0])
        total_energy_usage = 0
        for i in range(constants.ENERGY, constants.NUM_FIELDS):
            total_energy_usage += float(data_row[i][0])

        f.write('{} {}\n'.format(customer_id, total_energy_usage))
        data_counter += 1

    f.close()

