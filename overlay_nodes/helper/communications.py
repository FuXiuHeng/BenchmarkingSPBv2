import pickle
import struct

import overlay_nodes.helper.constants as constants

def receive_message_header(conn):
    # Parse packet header
    return conn.recv(constants.HEADER_BYTES)

def receive_message_body(conn):
    # Parse size of data
    size_packet = conn.recv(struct.calcsize("i"))
    size = struct.unpack("i", size_packet)[0]

    # Receive data of the specified size
    buff = []
    acc_size = 0
    while acc_size < size:
        packet = conn.recv(size - acc_size)
        acc_size += len(packet)
        if not packet:
            break
        buff.append(packet)

    # Unpickle data - convert from byte stream to python object
    serialised_msg = b"".join(buff)
    unserialised_msg = pickle.loads(serialised_msg)

    return unserialised_msg

def send_message(conn, serialised_header, unserialised_msg):
    serialised_msg = pickle.dumps(unserialised_msg)
    conn.sendall(
        serialised_header
        + struct.pack("i", len(serialised_msg))
        + serialised_msg
    )