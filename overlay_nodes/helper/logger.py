#!/usr/bin/python

def log_time_sent(simulation_id, time_sent, from_addr, ctp_hash):
    file_name = './log/{:02d}_time_sent.log'.format(simulation_id)
    f = open(file_name, 'a')
    f.write('{} {} {}\n'.format(time_sent, from_addr, ctp_hash))
    f.close()

def log_time_mined(simulation_id, time_mined, from_addr, ctp_hash):
    file_name = './log/{:02d}_time_mined.log'.format(simulation_id)
    f = open(file_name, 'a')
    f.write('{} {} {}\n'.format(time_mined, from_addr, ctp_hash))
    f.close()

def log_gas_used(simulation_id, gas_used, from_addr, ctp_hash):
    file_name = './log/{:02d}_gas_used.log'.format(simulation_id)
    f = open(file_name, 'a')
    f.write('{} {} {}\n'.format(gas_used, from_addr, ctp_hash))
    f.close()