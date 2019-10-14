#!/usr/bin/python
import os
import time

def log(simulation_name, node_name, message):
    file_name = './log/{}/nodes/{}.log'.format(simulation_name, node_name)
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    f = open(file_name, 'a+')
    f.write('{} {}\n'.format(time.time(), message))
    f.close()

def log_time_sent(simulation_name, time_sent, from_addr, ctp_hash):
    file_name = './log/{}/results/time_sent.log'.format(simulation_name)
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    f = open(file_name, 'a+')
    f.write('{} {} {}\n'.format(time_sent, from_addr, ctp_hash))
    f.close()

def log_time_mined(simulation_name, time_mined, from_addr, ctp_hash):
    file_name = './log/{}/results/time_mined.log'.format(simulation_name)
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    f = open(file_name, 'a+')
    f.write('{} {} {}\n'.format(time_mined, from_addr, ctp_hash))
    f.close()

def log_gas_used(simulation_name, gas_used, from_addr, ctp_hash):
    file_name = './log/{}/results/gas_used.log'.format(simulation_name)
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    f = open(file_name, 'a+')
    f.write('{} {} {}\n'.format(gas_used, from_addr, ctp_hash))
    f.close()

def log_baseline_mining_time(simulation_name, mining_time, from_addr, tx_hash):
    file_name = './log/baseline/{}/mining_time.log'.format(simulation_name  )
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    f = open(file_name, 'a+')
    f.write('{} {} {}\n'.format(mining_time, from_addr, tx_hash))
    f.close()