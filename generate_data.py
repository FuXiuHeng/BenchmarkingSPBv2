import os
import sys
import random

# Run the script to pre-generate data
# Usage: 
#   python3 generate_data.py <dest_name> <num_users> <num_data>
#
# Generate fake energy usage data with up to the given number of uniques users and with the given number of data.
# Each line of energy usage data will be written in the following format:
#       <consumer_id> <energy_usage> <producer_id>

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Error: Invalid number of arguments to the script.')
        print('Usage:')
        print('  python3 generate_data.py <dest_name> <num_users> <num_data>')
        exit()
    
    dest_name = sys.argv[1]
    num_users = int(sys.argv[2])
    num_data = int(sys.argv[3])
    
    if num_users < 2:
        print('Error: Must allow at least 2 distinct users')
        exit()

    dest_dir_path = './data/generated'
    dest_file_path = os.path.join(dest_dir_path, '{}.txt'.format(dest_name))
    os.makedirs(dest_dir_path, exist_ok=True)

    f = open(dest_file_path, 'w+')
    f.write("consumer_id energy producer_id\n")

    user_id_base = 10000
    min_total_energy = 500
    max_total_energy = 2000

    for i in range(0, num_data):
        consumer_offset = random.randint(0, num_users - 1)
        producer_offset = random.randint(0, num_users - 1)
        if producer_offset == consumer_offset:
            producer_offset = (producer_offset + 1) % num_users
        
        consumer_id = user_id_base + consumer_offset
        producer_id = user_id_base + producer_offset
        total_energy_usage = random.randint(min_total_energy, max_total_energy)

        f.write('{} {} {}\n'.format(consumer_id, total_energy_usage, producer_id))
    
    f.close()

