#!/usr/bin/env python

#This is the backup script being used
#Created by Beattie, Started @ 22:35 on 2019-06-09
import paramiko
import time
import sys
import datetime
import os
import socket
import csv
filename = sys.argv[1]
f = open(filename, 'r')
data = csv.reader(f)

ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print('''
    GHOSTKEEPER 
    Cisco ASA
    Backup Tool
    Created by @beattiebeatdown''')
for item in data:

    try:
        ip_address = str(item[2])
        username = str(item[3])
        password = str(item[4])
        password2 = str(item[5])
        hostname_ss = str(item[1])
        customer = str(item[0])
        savepath = os.environ.get('SAVE_LOC2') #save path set within the is environment variables
        ssh_client.connect(hostname=ip_address, username=username, password=password, timeout=10)
        print('------------------------------------------------------------------')
        print("Successful connection", hostname_ss + ' ' + ip_address)
        remote_conn = ssh_client.invoke_shell()
#Set date to be used when adding to the file
        date = datetime.datetime.now().strftime("%Y-%m-%d--%H%M")
#Jump up to enable mode
        remote_conn.send('en \n')
        time.sleep(1)
        remote_conn.send(password2)
        remote_conn.send('\n')
        time.sleep(1)
#Pulling hostname to be used for filename
        remote_conn.send('show hostname\n')
        time.sleep(1)
        hostname_output = remote_conn.recv(5000)
        hostname_output2 = hostname_output.split()
        host_filename = hostname_output2[-2]
        print('Backing up ' + host_filename + ' please standby...')
#Set terminal to print the whole config, This also get PSKs for VPNS
        remote_conn.send('terminal page 0\n')
        remote_conn.send('more system:running-config\n')
        time.sleep(5)
        read_config = remote_conn.recv(1000000)
#Saves the file in the specified path defined in savepath then saves with the hostname pulled from above and adds the date
        hostdir = savepath + '/' + host_filename
        try:
            os.makedirs(hostdir)
        except OSError:
            print('Directory ' + hostdir + ' already exists')
        CompletePath = os.path.join(hostdir, host_filename + '-' + date)
        save_config = open(CompletePath, "w")
#writes the shell output read_config to the save_config file name&path
        save_config.write(read_config)
        save_config.write('\n')
        save_config.close
        time.sleep(2)
        print('Finishing backing up ' + customer + "'s firewall " + host_filename)
        print('------------------------------------------------------------------')
        ssh_client.close
        if item[1] == "":
         break
    except paramiko.ssh_exception.AuthenticationException:
        print('************' + customer + "'s " + host_filename + " auth failure...************")
        print('------------------------------------------------------------------')
    except socket.timeout:
        print('************' + customer + "'s " + host_filename + " timed out...************")
        print('------------------------------------------------------------------')
    except paramiko.ssh_exception.SSHException:
        print('************' + customer + "'s " + host_filename + " running ssh V1************")
        print('------------------------------------------------------------------')
    except paramiko.ssh_exception.NoValidConnectionsError:
         print('************' + customer + "'s " + host_filename + " connection refused...************")
         print('------------------------------------------------------------------')



