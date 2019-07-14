import re

# Returns the address (or private key) of the ethereum node
# which are stored in the /private_keys folder
def get_address(filename):
    filepath = './private_keys/{}'.format(filename)
    f = open(filepath)
    for line in f:
        if re.search("address", line):
            addr = re.findall(r'\w+', line)[1]
            hex_addr = '0x{}'.format(addr)
            f.close()
            return hex_addr
    
    f.close()
    return None
