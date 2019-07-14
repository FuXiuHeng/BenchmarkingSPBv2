import mysql.connector

db_name = "spb_thesis"
table_name = "CTP"

CTP_ID_INDEX = 0
FROM_ADDR_INDEX = 1
RAW_TXN_INDEX = 2
TXN_HASH_INDEX = 3

# Creates a MySQL database for storing CTP transactions
# Returns the connected db object
def initialise_database(host, user, password):
    db = mysql.connector.connect(
        host=host,
        user=user,
        passwd=password
    )
    cursor = db.cursor()

    cursor.execute("DROP DATABASE IF EXISTS {}".format(db_name))
    cursor.execute("CREATE DATABASE {}".format(db_name))
    
    db = mysql.connector.connect(
        host=host,
        user=user,
        passwd=password,
        database=db_name
    )
    cursor = db.cursor()
    cursor.execute("CREATE TABLE {} ("
        "id INT PRIMARY KEY AUTO_INCREMENT,"
        "from_addr VARCHAR(255) NOT NULL," 
        "raw_txn VARCHAR(255) NOT NULL,"
        "txn_hash VARCHAR(255) NOT NULL"
    ")".format(table_name))

    return db

# Inserts a new CTP transaction into the database
# Retursn the CTP id
def insert_ctp(db, from_addr, raw_txn_hex, txn_hash_hex):
    sql = " \
        INSERT INTO {} (from_addr, raw_txn, txn_hash) \
        VALUES ('{}', '{}', '{}')".format(table_name, from_addr, raw_txn_hex, txn_hash_hex)
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    return cursor.lastrowid

# Delete a CTP transaction from the database given its ID
def delete_ctp(db, ctp_id):
    sql = "\
        DELETE FROM {} \
        WHERE id = {}".format(table_name, ctp_id)
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()

# Returns the database entry corresponding to the given CTP ID
# Returns None if no such ID exists
def get_ctp(db, ctp_id):
    sql = "\
        SELECT * FROM {} \
        WHERE id = {}".format(table_name, ctp_id)
    cursor = db.cursor()
    cursor.execute(sql)
    return cursor.fetchone()

# Prints all data in the database for debugging purposes
def print_all(db):
    sql = "SELECT * FROM {}".format(table_name)
    cursor = db.cursor()
    cursor.execute(sql)
    for line in cursor.fetchall():
        print(line)

# from_addr = '0x1147494773a0769c652Ec0404A654F46022a5AD4'
# # raw_txn = "123"
# raw_txn = b"\xf8n\x80\x856\x9dV\x126\x83\r\xbb\xa0\x94\xa8|\x00u\x0b\xab\xf6\x01\xc2\xb8\xd2\x1f\xf3\xed\x85TMu\xed2\x89\x1b\x1a\xe4\xd6\xe2\xefP\x00\x00\x80\x1b\xa0\xdf?\x08\x8bP\xab\x19\xbf\xee\x9d\xf2M\xa1q\x14e\xf1\x11h\xd6\xf0D'm\x94\x97\x13\xfd\x90\x83\xd9\x06\xa0\x1dIC\xff\xb7\xec\x93]yX\xd8\xb6!\xd2Kp\xbaN\xd9\xed\xd8\xa2Ts\xb5\x85\x08f.\x93\xc4\xbf"

# db_host = "localhost"
# db_user = "root"
# db_password = ""
# db = initialise_database(db_host, db_user, db_password)

# insert_ctp(db, from_addr, raw_txn)
# print(raw_txn)
# result = get_ctp(db, 1)
# hexstr = result[2]
# b = bytes(hexstr)
# print(b)