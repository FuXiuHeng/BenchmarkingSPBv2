from scipy.io import loadmat, whosmat
from . import constants

# Return the field names as written in the meta-info .mat file
def get_field_names(meta_info_file_path):
    raw = loadmat(meta_info_file_path)
    var_name = whosmat(meta_info_file_path)[0][0]
    data = raw[var_name]
    
    row = 0
    num_fields = len(data[row])
    if num_fields != constants.NUM_FIELDS: 
        raise Exception('Mismatch in number of fields of meta-information')
    
    field_names = []
    for col in range(0, num_cols):
        field_name = data[row][col][0]
        field_names.append(field_name)

    return field_names

# Parse the given, original .mat data file, and returns an array of user energy transactions
# with only the customer_id and aggregated energy usage fields.
# The individual transactions are represented as dictionaries.
def parse_energy_usage_file(matlab_data_file_path):
    raw = loadmat(matlab_data_file_path)
    var_name = whosmat(matlab_data_file_path)[0][0]
    data = raw[var_name]

    result = []
    for row in range(0, len(data)):
        row_data = {}
        row_data[constants.CUSTOMER_ID_KEY] = int(data[row][constants.CUSTOMER_ID][0])

        total_energy_usage = 0
        for i in range(constants.ENERGY, constants.NUM_FIELDS):
            total_energy_usage += float(data[row][i][0])
        row_data[constants.ENERGY_KEY] = total_energy_usage

        result.append(row_data)
        
    return result

# Parse a file containing unique customer ids and places these customer ids
# into a dictionary with the customer id as keys. The value, set to 1, has no significance
def parse_unique_customer_id():
    f = open('./data/unique_customer_id.txt', 'r')
    line = f.readline()
    result = {}
    while line:
        customer_id = line.split(' ')[1].strip()
        result[customer_id] = 1
        line = f.readline()

    f.close()
    return result

