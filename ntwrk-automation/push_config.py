#!/bin/python3.11
# Created by John W Cunningham
#Run syntax: python3 push_config.py <dir>
# - <dir>: a directory containing two files: push_cmds.txt and target.txt
# - where push_cmds.txt is a file containing desired commands for pulling data whether it be state or running-config
# - where target.txt is a file containing the desired inventory

#global libraries
from flytools import securetools
from netmiko import ConnectHandler
from datetime import datetime
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import getpass
import queue
import socket
import sys
import re

#global variables
console_arg = sys.argv[1].strip()
START_TIME = datetime.now()
TIME_STRING = START_TIME.strftime('%H:%M:%S')
MAX_THREADS = 10
HOME_FOLDER = '<my_home_dir>'
PRJ_FOLDER = HOME_FOLDER + 'scripts/' + console_arg + '/'
LOG_FILE = PRJ_FOLDER + 'push_' + console_arg + '_' + TIME_STRING + '.log'
CMD_FILE = PRJ_FOLDER + 'push_cmds.txt'
INV_FILE = PRJ_FOLDER + 'target.txt'
log_list = []

### Functions ###
def push_to_device(q,usr,pwd):
    # router login info
    error_fetching_data = False

    # run through queue
    while not q.empty():
        # get device information
        device_info = q.get(block = False)
        device = device_info[0]
        ip = device_info[1]

        # metadata #
        metadata_output = f'grab_date: {START_TIME}\ndevice_name: {device}\ndevice_ip: {ip}'
        command_results_list = [{"ios_command":"metadata","output":metadata_output,"last_updated":START_TIME}] # start_result_list with metadata

        # netmiko connection
        cisco = {'device_type':'cisco_ios', 'host': ip, 'username': usr, 'password' : pwd,'session_timeout':4*60}
        print(f'Connecting to {device}')

        # test connection
        try:
            connection = ConnectHandler(**cisco)
            connection_successful = True
            print(f'  Connection to {device} was successful.\n')
        except Exception as e:
            connection_successful = False
            log_list.append(f'\n**Error | {device} | Unable to establishing SSH connection')
            print(e)

        # if connection OK, push data.
        if connection_successful:
            command = CMD_LIST

            # pushing set of commands to device
            try:
                print(f'{device} > pushing "{command}"')
                output = connection.send_config_set(command)
                print(f'  {device} < pushing "{command}" was successful.\n')
            except Exception as exc:
                print(f'  ERROR pushing "{command}"\n{exc}\n')
                output = '**Error pushing data'
                error_fetching_data = True

            command_results_list.append({'output':output})
            connection.disconnect()

            #save to log file
            if error_fetching_data:
                log_list.append(f'\nIncomplete | {device} | Not all data was pushed succesfully')

            else:
                log_list.append(f'\nOK | {device} | pushing data was successful')
        q.task_done()

### Main ###
# parses inventory into INV_FILE
with open(INV_FILE, 'r') as f:
    INV_LIST = f.read().splitlines()

# parses command file into CMD_LIST
with open(CMD_FILE,'r') as f:
    CMD_LIST = f.read().splitlines()

# user authentication
usr = getpass.getuser()+'b'
pwd = getpass.getpass('Enter PASSCODE:')
print(f'\nStarting script... time: {START_TIME}\n')

# get IP from hostname in inventory
list_to_query = []
for device in INV_LIST:
    try:
        ip = socket.gethostbyname(device)
        list_to_query.append((device, ip))
    except:
        ip = 'DNS_RESOLUTION_FAILED'
        log_list.append(f'DNS resolution failed for {device}. Check name\n')

# start queue to get command data from devices
q = queue.Queue()
for host in list_to_query:
    q.put(host)

# set queue size
if (q.qsize()) > MAX_THREADS:
        number_of_threads = MAX_THREADS
else:
        number_of_threads = q.qsize()
# print('Getting information from devices...')
for i in range(number_of_threads):
        t = Thread(target = push_to_device, args = (q,usr,pwd))
        t.start()
q.join()

run_time = datetime.now() - START_TIME

## write to log files
print('Writing data to logs...\n')
log_list.append(f'\nRuntime: {run_time}\n') # last line of logs
try:
    with open(LOG_FILE,'w') as log_f:
        log_f.write(f'Last run: {START_TIME} \n')
        log_f.write('\n'.join(log_list))
except Exception as e:
    print(e)

#run time of full script
print('Runtime: ',datetime.now() - START_TIME)
