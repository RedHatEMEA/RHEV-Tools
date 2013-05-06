#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    Script o manage your RHEV virtual machines
#
#    Copyright (C) 2013 Christian Bolz <cbolz at redhat dot com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

version="0.1.0"
lastchange="2013-03-11"
homepage="http://github.com/RedHatEMEA/RHEV-Tools"
author="Christian Bolz <cbolz at redhat dot com>"

from ovirtsdk.api import API
from sys import exit, argv
from rhevtools import config, vm
import getopt
from getpass import getpass

def usage():
    """ 
    Usage of this tool
    """
    print ""
    print "Tool to manage RHEV virtual machines"
    print "Version",version,lastchange
    print "Latest Version",homepage,"by",author
    print "This is free software, see LICENSE for details"
    print ""
    print "Usage:", argv[0], "<command> [option,..]"
    print ""
    print "Commands:"
    print "--start: Start virtual machine"
    print "--stop: Stop virtual machine"
    print "--shutdown: shutdown virtual machine"
    print "--migrate: Live Migration of virtual machine"
    print "--create: create a new virtual machine"
    print "--delete: delete a virtual machine"
    print "--details: query details of virtual machine"
    print "--console: connect to serial console of given virtual machine"
    print "  read SERIAL_CONSOLE for detais on how to use this feature"
    print ""
    print "Connection Details:"
    print "--host: URL to RHEV-M (https://<servername>)"
    print "--user: user name"
    print "--pass: password, will be asked interactively, if not given"
    print ""
    print "Console Mode:"
    print "--console: connect to serial Console of a virtual machine"
    print "--vm: Name of virtual machine to connect to "
    print "  read SERIAL_CONSOLE for detais on how to use this feature"
    print ""
    print "Options for create):"
    print "--vm: Name of virtual machine"
    print "--cluster: RHEV Cluster"
    print "--hv: preferred Hypervisor"
    print "--storagedomain: StorageDomain to store the virtual disks"
    print "--sockets=number of CPU sockets of the virtual machine"
    print "--cores=number of ocres of the virtual machine"
    print "--mem=amount of memory in MB"
    print "--guaranteedmem=amount of guaranteed mamory in MB"
    print "--template=template, Blank is deftault"
    print "--disksize=size of virtual disk"
    print "--vnet=name of virtual (logical) network"
    print "--mac: MAC addresss" 
    print "--osver: Operating System (rhel_6x64, rhel_5x64, windows_2008r2)"
    print "--fqdn: FQDN of virtual machine (for Satellite/Cobbler integration)"
    print "--createscript: call external script after VM was created"
    print "  see README for more details on external scripts"
    print "--display: Disply Type (spice/vnc)"
    print "--hamode: enable high availability (True or False)"
    print "--haprio: Priority for HA Feature (1=low,50=medium,100=high)"
    print "  all values between 1 and 100 are possible, but not reflected by UI"
    print "--serial: set to 1 to enable serial console support (default: disabled)"
    print "  read SEARIAL_CONSOLE for details on how to set this up"
    print ""
    print "Options for live migration"
    print "--vm: name of the virtual machine"
    print "--tohv: Migrato to the specified HV"
    print ""
    print "Optionen für delete:"
    print "--vma: name of virtual machine"
    print "--deletescript: call external script after VM was deleted"
    print "  see README for more details on external scripts"
    print ""
    exit(0)
    
def error():
    """
    usage information
    """
    print ""
    print "Use -h to list all possible options"
    print ""
    exit(1)

try:
    opts, args = getopt.getopt(argv[1:], "h", ["serial=", "template=", "console", "start", "stop", "shutdown", "osver=", "migrate", "vm=", "cluster=", "tohv=", "fqdn=", "hv=", "host=", "user=", "passwd=", "storagedomain=", "create", "delete", "sockets=", "cores=", "guaranteedmem=", "mem=", "disksize=", "vnet=", "createscript=", "deletescript=", "mac=", "details", "display=", "hamode=", "haprio="])
except getopt.GetoptError as err:
    # print help information and exit:
    print str(err)  # will print something like "option -argument not recognized"
    error()
    
# create a config object to store the RHEV configuration details
config = config()
config.parseconfig()
# check which command will have to be executed
command = ""

# parse command line
for option, argument in opts:
    if option == "-h":
        usage()
    elif option == "--user":
        config.rhevmconfig["user"] = argument
    elif option == "--host":
        config.rhevmconfig["host"] = argument
    elif option == "--passwd":
        config.rhevmconfig["passwd"] = argument   
        
if config.rhevmconfig["host"] == "":
    print "No RHEV-M hostname was specified."
    error()
elif config.rhevmconfig["user"] == "":
    print "No user name was specified."
    error()
elif config.rhevmconfig["passwd"] == "":
    print "Enter password for user %s:" % (config.rhevmconfig['user'])
    config.rhevmconfig['passwd'] = getpass() 
    
# Connect to RHEV-M
print "Connecting to RHEV-M %s..." % (config.rhevmconfig['host'])
api = API (url=config.rhevmconfig["host"], username=config.rhevmconfig["user"], password=config.rhevmconfig["passwd"], insecure=True)
print "Connection established"
print ""


vm = vm(config.vmname, config.vmconfig, api)
if command == "start":
    vm.start()
elif command == "stop":
    vm.stop()
elif command == "console":
    vm.console(config.rhevmconfig)
elif command == "migrate":
    vm.migrate()
elif command == "shutdown":
    vm.shutdown()
elif command == "create":
    vm.create()
elif command == "delete":
    vm.delete(config)
elif command == "details":
    vm.details()
else:
    print "No command specified."
    error()
