#!/usr/bin/python
import os
import time

def log(simulation_date_time, node_name, message):
    file_name = simulation_date_time.strftime('./log/%Y%m%d_%H%M/nodes/{}.log'.format(node_name))
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    f = open(file_name, 'a+')
    f.write('{} {}\n'.format(time.time(), message))
    f.close()

def log_time_sent(simulation_date_time, time_sent, from_addr, ctp_hash):
    file_name = simulation_date_time.strftime('./log/%Y%m%d_%H%M/results/time_sent.log')
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    f = open(file_name, 'a+')
    f.write('{} {} {}\n'.format(time_sent, from_addr, ctp_hash))
    f.close()

def log_time_mined(simulation_date_time, time_mined, from_addr, ctp_hash):
    file_name = simulation_date_time.strftime('./log/%Y%m%d_%H%M/results/time_mined.log')
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    f = open(file_name, 'a+')
    f.write('{} {} {}\n'.format(time_mined, from_addr, ctp_hash))
    f.close()

def log_gas_used(simulation_date_time, gas_used, from_addr, ctp_hash):
    file_name = simulation_date_time.strftime('./log/%Y%m%d_%H%M/results/gas_used.log')
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    f = open(file_name, 'a+')
    f.write('{} {} {}\n'.format(gas_used, from_addr, ctp_hash))
    f.close()
