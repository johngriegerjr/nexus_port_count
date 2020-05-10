#!/usr/bin/python3
from __future__ import print_function
from __future__ import unicode_literals
import csv
import os
from getpass import getpass
from netmiko import ConnectHandler
from netmiko import NetMikoAuthenticationException
from paramiko.ssh_exception import SSHException

__author__ = "John Grieger (johngriegerjr@gmail.com)"
__version__ = ": 1.0 $"
__date__ = "03/05/2020"
__copyright__ = "Copyright (c) 2020 John Grieger"
__license__ = "Python"

show_command1 = "sh int bri | in ^Eth[0-9] | count"
show_command2 = "sh int bri | in ^Eth[0-9]+/[0-9] | in up | count"
show_command3 = "sh int bri | in ^Eth[0-9]+/[0-9] | in down | count"
show_command4 = "sh int bri | in ^Eth[0-9]+/[0-9] | count"
show_command5 = "sh int bri | in ^Eth[0-9][0-9][0-9] | count"
show_command6 = "sh int bri | in ^Eth[0-9][0-9][0-9] | in up | count"
show_command7 = "sh int bri | in ^Eth[0-9][0-9][0-9] | in down | count"

def establish_netmiko_conn(device_name, netmiko_dict):
    file = open('results.csv', "a+")
    try:
#Initialize variable
        output = ""
#Open Connection
        net_conn = ConnectHandler(**netmiko_dict)
        port_total = net_conn.send_command(show_command1)
        port_total = port_total.strip()
        switch_total = net_conn.send_command(show_command4)
        switch_total = switch_total.strip()
        fex_total = net_conn.send_command(show_command5)
        fex_total = fex_total.strip()
        switch_port_up = net_conn.send_command(show_command2)
        switch_port_up = switch_port_up.strip()
        switch_port_down = net_conn.send_command(show_command3)
        switch_port_down = switch_port_down.strip()
        fex_port_up = net_conn.send_command(show_command6)
        fex_port_up = fex_port_up.strip()
        fex_port_down = net_conn.send_command(show_command7)
        fex_port_down = fex_port_down.strip()
        switch_port_up_int = int(switch_port_up)
        switch_total_int = int(switch_total)
        switch_percent = str(round(switch_port_up_int / switch_total_int, 2) * 100)
        fex_port_up_int = int(fex_port_up)
        fex_total_int = int(fex_total)
        if fex_total_int > 0:
            fex_percent = str(round(fex_port_up_int / fex_total_int, 2) * 100)
        else:
            fex_percent = "No Fex"
        output += (device_name + "," + "{}".format(netmiko_dict["host"]) + "," + port_total + ","  + switch_total + "," + fex_total + "," + switch_port_up + "," + switch_port_down + "," + fex_port_up + "," + fex_port_down + "," + switch_percent  + "," + fex_percent)
        file.write(output + "\n")
        net_conn.disconnect()
#Check if Credentials failed
    except NetMikoAuthenticationException:
        output += (device_name + "," + "{}".format(netmiko_dict["host"]) + "," + "Creds failed")
        file.write(output + "\n")
#Check if SSH is not allowed/enabled
    except(SSHException):
        output += (device_name + "," + "{}".format(netmiko_dict["host"]) + "," + "SSH Not Enabled")
        file.write(output + "\n")
    file.close()

def main():
    file_name = "device_list.csv"
    un = input("Username: ")
    pw = getpass(prompt='Enter Password: ')
    ssh_config = '/home/john/.ssh/config'
    headers = "Device Name,IP Address,Port Total,Switch Total,Fex Total,Switch Up,Switch Down,Fex Up,Fex Down,Switch Util %,Fex Util %"
    if os.path.exists("results.csv"):
        os.remove("results.csv")
    file = open('results.csv', "a+")
    file.write(headers + "\n")
    file.close()
    with open(file_name) as f:
        read_csv = csv.DictReader(f)
        for entry in read_csv:
            device_name = entry.pop('device_name')
            entry['username'] = un
            entry['password'] = pw
            entry['secret'] = pw
            entry['ssh_config_file'] = ssh_config
            establish_netmiko_conn(device_name, entry)

if __name__ == "__main__":
    main()
