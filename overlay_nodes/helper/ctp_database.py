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


# Connects to a MySQL database which stores CTP transactions
def connect_database(host, user, password):
    db = mysql.connector.connect(
        host=host,
        user=user,
        passwd=password,
        database=db_name
    )
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
