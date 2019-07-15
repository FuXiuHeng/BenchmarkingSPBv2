#!/usr/bin/python

from datetime import datetime

def log(node_name, message):
    pass

def log_time_sent(time_sent, from_addr, ctp_hash):
    file_name = datetime.now().strftime('./log/results/%Y%m%d_%H%M_time_sent.log')
    f = open(file_name, 'a')
    f.write('{} {} {}\n'.format(time_sent, from_addr, ctp_hash))
    f.close()

def log_time_mined(time_mined, from_addr, ctp_hash):
    file_name = datetime.now().strftime('./log/results/%Y%m%d_%H%M_time_mined.log')
    f = open(file_name, 'a')
    f.write('{} {} {}\n'.format(time_mined, from_addr, ctp_hash))
    f.close()

def log_gas_used(gas_used, from_addr, ctp_hash):
    file_name = datetime.now().strftime('./log/results/%Y%m%d_%H%M_gas_used.log')
    f = open(file_name, 'a')
    f.write('{} {} {}\n'.format(gas_used, from_addr, ctp_hash))
    f.close()
