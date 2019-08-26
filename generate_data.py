import os
import sys
import random

# Run the script to pre-generate data
# Usage: 
#   python3 generate_data.py <dest_name> <num_users> <num_data>
#
# Generate fake energy usage data with up to the given number of users and with the given number of data.

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Error: Invalid number of arguments to the script.')
        print('Usage:')
        print('  python3 generate_data.py <dest_name> <num_users> <num_data>')
        exit()
    
    dest_name = sys.argv[1]
    num_users = int(sys.argv[2])
    num_data = int(sys.argv[3])
    
    dest_dir_path = './data/generated'
    dest_file_path = os.path.join(dest_dir_path, dest_name)
    os.makedirs(dest_dir_path, exist_ok=True)

    f = open(dest_file_path, 'w+')

    for i in range(0, num_data):
        customer_id_base = 10000
        customer_id = random.randint(customer_id_base, customer_id_base + num_users - 1)
        min_total_energy = 500
        max_total_energy = 2000
        total_energy_usage = random.randint(min_total_energy, max_total_energy)
        f.write('{} {}\n'.format(customer_id, total_energy_usage))
    
    f.close()

