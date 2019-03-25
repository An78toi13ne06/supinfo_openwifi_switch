import sys, platform

if sys.version_info < (3, 5):
    print("You are running a too old version of python. (" + platform.python_version() + ")\n"
          "Please consider upgrading your Python installation to at least 3.5")
    exit()

import argparse, getpass, paramiko, socket, time, os
from paramiko import *
from subprocess import DEVNULL, STDOUT, check_call


# Parsing Help
parser = argparse.ArgumentParser(prog="Open-Wifi De/Activator", description="de/activation of SUPINFO OpenWiFi Network")
parser.add_argument('-a', '--activate', help="Use this option to activate the Open-WiFi", action='store_true')
parser.add_argument('-d', '--deactivate', help="Use this option to deactivate the Open-WiFi", action='store_true')
args = parser.parse_args()

# Initializing Variables
buff = ''
resp = ''
choice = ''
option = ''
action = ''
host = []
ips = []

# Setting 'choice' variable with correct action
if args.deactivate:
    option = 'no ssid SUPINFO-OpenWiFi'
    action = 'Deactivating'
elif args.activate:
    option = 'ssid SUPINFO-OpenWiFi'
    action = 'Activating'
else:
    print("You must indicate if you want to activate or deactivate Wifi with the correct argument (-a, -d)")
    exit()

from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


# Put here IPs of WiFi controllers
ips = os.getenv('IPS')


print('\n***********************************************\n'
      '*    SIS/SSN - SUPINFO Systems and Network    *\n'
      '***********************************************\n'
      '*                                             *\n'
      '* You are using a SIS\'s tool.                 *\n'
      '*                                             *\n'
      '* Unauthorised use prohibited.                *\n'
      '* All events are logged.                      *\n'
      '*                                             *\n'
      '* Please, disconnect now if you are not from  *\n'
      '* the SIS/SSN team.                           *\n'
      '*                                             *\n'
      '***********************************************\n')

# Check if SUPINFO's servers are accessible
# response1 = check_call(["ping -c 1 #### TO DO ADD IPS #####"], stdout=DEVNULL, stderr=STDOUT)
# response2 = check_call(["ping -c 1 #### TO DO ADD IPS #####"], stdout=DEVNULL, stderr=STDOUT)

#if response1 != 0 and response2 != 0:
#    print('You are not connected to SWN or using the VPN connection to SUPINFO network.\n'
#          'Please restart this script when connected to SUPINFO network\n')
#    exit()

# Credentials prompt
username = input("Login: ")
password = getpass.getpass("Password: ")
print("\n")

# Setting 'ssh' variable with Paramiko parameters
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.load_system_host_keys()

for ip in ips:
    try:
        print("Finding " + ip + "...")

        # Initializing connection to host with Paramiko
        print("Trying to connect to " + ip + "...")
        ssh.connect(ip, username=username, password=password)

        print("Connected to " + ip + " !")

        # Invoke shell in variable 'chan' in order to send commands
        chan = ssh.invoke_shell()

        print(action + ' OpenWiFi on ' + ip + ' ...')

        # Turn off paging
        chan.send('terminal length 0\n')
        time.sleep(1)
        resp = chan.recv(9999)
        output = resp.decode('ascii').split(',')
        print(''.join(output))

        # Enter Configure Terminal
        chan.send('conf t\n')
        time.sleep(2)
        resp = chan.recv(9999)
        output = resp.decode('ascii').split(',')
        print(''.join(output))

        for i in range(2):

            # Enter Interface
            chan.send('interface dot11Radio ' + str(i) + '\n')
            time.sleep(2)
            resp = chan.recv(9999)
            output = resp.decode('ascii').split(',')
            print(''.join(output))

            # (De)Activating Open-WiFi
            chan.send(option + '\n')
            time.sleep(5)
            resp = chan.recv(9999)
            output = resp.decode('ascii').split(',')
            print(''.join(output))

            # Exit from interface configuration
            chan.send('exit\n')
            time.sleep(2)
            resp = chan.recv(9999)
            output = resp.decode('ascii').split(',')
            print(''.join(output))

        # Exit from Terminal Configuration
        chan.send('exit\n')
        time.sleep(2)
        resp = chan.recv(9999)
        output = resp.decode('ascii').split(',')
        print(''.join(output))

        # Write Configuration
        chan.send('write\n')
        time.sleep(10)
        resp = chan.recv(9999)
        output = resp.decode('ascii').split(',')
        print(''.join(output))

        # Closing SSH connection
        ssh.close()

        # Inform user that action is successfully done
        if args.activate:
            print("\n SUPINFO Open-WiFi successfully activated on " + ip)
        elif args.deactivate:
            print("\n SUPINFO Open-WiFi successfully deactivated on " + ip)

    # Setting exceptions
    except BadHostKeyException:
        print("Remote host key couldn't be verified")
        exit()
    except AuthenticationException:
        print("Authentication failed ! Please check your credentials.")
        exit()
    except SSHException:
        print("An SSH error has occur !! Please restart the script.")
        exit()
    except socket.error as e:
        print("Socket error({0}): {1}".format(e.errno, e.strerror))
        exit()

if args.activate:
    print("\n SUPINFO Open-WiFi successfully activated on all access points")
elif args.deactivate:
    print("\n SUPINFO Open-WiFi successfully deactivated on all access points")
