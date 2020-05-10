#!/usr/bin/python3
from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.plugins.functions.text import print_result
from nornir.core.inventory import ConnectionOptions
from getpass import getpass
from colorama import Fore, Style
import os

__author__ = "John Grieger (johngriegerjr@gmail.com)"
__version__ = ": 1.0 $"
__date__ = "04/05/2020"
__copyright__ = "Copyright (c) 2020 John Grieger"
__license__ = "Python"

# Initialize list
site_list = []
# Initialize Nornir using config file
nr = InitNornir(config_file="config.yaml", dry_run=True)
# Discover sites
for i in nr.inventory.hosts:
    host = nr.inventory.hosts[i]
    site_list.append(host['site'])
# Create clean string from list of sites
site_list = str(list(dict.fromkeys(site_list)))
site_list = site_list.replace("'", "")
# Prompt user to choose which site they want to query for port utilization
print("\n")
print(Fore.YELLOW + "#" * 76 + Style.RESET_ALL)
print(Fore.CYAN + " " * 15 + "This script will gather switchport utilization" + "\n" + Style.RESET_ALL)
print(" " * 23 + "Select a " + Fore.RED +"site" + Style.RESET_ALL + " from the list below")
print(" " * 23 + "Available Sites: " + Fore.GREEN + site_list)
print(Fore.YELLOW + "#" * 76 + Style.RESET_ALL)
usr_site = input ("\nEnter Site: ")
# Prompt user for credentials to be used to login to devices
user = input ("\nUsername: ")
p = getpass()
# Create variables for commands to be ran
Onboard_Switch_Total = "sh int bri | in ^Eth[0-9]{1,2}/ | count"
Switch_and_Fex_Total = "sh int bri | in ^Eth[0-9]{1,3}/ | count"
Fex_Total = "sh int bri | in ^Eth[0-9]{3}/ | count"
Onboard_Switch_Up = "sh int bri | in ^Eth[0-9]{1,2}/ | in up | count"
Onboard_Switch_Down = "sh int bri | in ^Eth[0-9]{1,2}/ | in down | count"
Fex_Up = "sh int bri | in ^Eth[0-9]{3}/ | in up | count"
Fex_Down = "sh int bri | in ^Eth[0-9]{3}/ | in down | count"
Overall_Switch_Total = "sh int bri | in ^Eth[0-9]{1,3}/ | count"
Overall_Switch_Up = "sh int bri | in ^Eth[0-9]{1,3}/ | in up | count"
usr_cmds = [Onboard_Switch_Total,Switch_and_Fex_Total,Fex_Total,Onboard_Switch_Up,Onboard_Switch_Down,Fex_Up,Fex_Down,Overall_Switch_Total,Overall_Switch_Up]
# String to be written to first line of output file
headers = "Device_Name,IP_Address,Onboard_Switch_Total,Switch_and_Fex_Total,Fex_Total,Onboard_Switch_Up,Onboard_Switch_Down,Fex_Up,Fex_Down,Overall_Switch_Total,Overall_Switch_Up,Total_Switch_Util_%,Onboard_Switch_Util_%,Fex_Util_%"
# Delete the output file if it exists
if os.path.exists("results.csv"):
    os.remove("results.csv")
# Open the file and write the headers
file = open('results.csv', "a+")
file.write(headers + "\n")
# Initialize dictionary to be used for storing port counts
dict1 = {}

def run_commands(cmds, site):
# Filter Nornir to only use site user specified
    nr_filtered = nr.filter(site=site)
# Use credentials user supplied so they do not have to be stored in inventory files
    nr_filtered.inventory.defaults.username = user
    nr_filtered.inventory.defaults.password = p
    nr_filtered.inventory.defaults.connection_options['netmiko'] = ConnectionOptions(extras={"secret":f"{p}"})
# Filter Nornir inventory for list of hosts
    host_list = nr_filtered.inventory.hosts
# Populate dictionary 'dict1' with a key for each hostname
    for i in host_list:
        dict1[i] = []
# Filter Nornir inventory for dictionary of host info
    ip_dict = nr_filtered.inventory.get_hosts_dict()
# Append the host IP address to the dictionary 'dict1'
    for i in host_list:
        ip = ip_dict[i]['hostname']
        dict1[i].append(ip)
# Run each command and append output to 'dict1' in the hosts' list
    for cmd in cmds:
        result = nr_filtered.run(task=netmiko_send_command,command_string=cmd)
        for dv_name in result.keys():
            value = str(result[dv_name][0].result)
            value = value.rstrip()
            dict1[dv_name].append(value)
    return dict1
# Execute 'run_commands' functions and store result in 'result_dict'
result_dict = run_commands(usr_cmds, usr_site)
# Display headers to screen
print(headers)
# Perform math to determine utilization percents
for key in result_dict:
    if int(result_dict[key][8]) == 0:
        result_dict[key].append("No Ports")
    else:
        result_dict[key].append(str(round(int(result_dict[key][9]) / int(result_dict[key][8]), 2) * 100))
    if int(result_dict[key][8]) == 0:
        result_dict[key].append("No Ports")
    else:
        result_dict[key].append(str(round(int(result_dict[key][4]) / int(result_dict[key][1]), 2) * 100))
    if int(result_dict[key][3]) > 0:
        result_dict[key].append(str(round(int(result_dict[key][6]) / int(result_dict[key][3]), 2) * 100))
    else:
        result_dict[key].append("No Fex")
# Iterate through 'result_dict' and print values to file
for key, value in result_dict.items():
    a = key.rstrip() + ","
    b = ','.join(value)
    c = a + b
    file.write(c + "\n")
    print(c)
# Close the file
file.close()
