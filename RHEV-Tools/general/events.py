#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    Script to view events
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
lastchange="2013-0418"
homepage="http://github.com/RedHatEMEA/RHEV-Tools"
author="Christian Bolz <cbolz at redhat dot com>"

import getopt
from ovirtsdk.api import API
from getpass import getpass
from sys import exit, argv
from rhevtools import config


def usage():
    """ 
    Usage of this tool
    """
    print ""
    print "Tool to view RHEV events"
    print "Version",version,lastchange
    print "Latest Version",homepage,"by",author
    print "This is free software, see LICENSE for details"
    print ""
    print "Usage:", argv[0], "<command> [option,..]"
    print ""
    print "-h: help"
    print ""
    print "Connection Details:"
    print "--host: URL to RHEV-M (https://<servername>)"
    print "--user: user name"
    print "--pass: password, will be asked interactively, if not given"
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

#for event in api.events.list(max=10000):
for event in api.events.list(from_event_id=2020):
    print "ID:",event.id
    print "Description:",event.description
    print "Code: ", event.code
    print "Time:", event.time
    