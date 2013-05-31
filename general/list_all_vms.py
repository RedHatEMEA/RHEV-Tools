#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    Script to print basic information about all RHEV DC, Clusters and VMs
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

version="0.1.2"
lastchange="2013-05-31"
homepage="http://github.com/RedHatEMEA/RHEV-Tools"
author="Christian Bolz <cbolz at redhat dot com>"

from ovirtsdk.api import API
from rhevtools import config, vm, importvm
import getopt
from sys import argv, exit
import time
from getpass import getpass

def usage():
    """
    Usage
    """
    print ""
    print "Tool to print basic information about RHEV DCx, CLusters and VMs"
    print "Version",version,lastchange
    print "Latest Version",homepage,"by",author
    print "This is free software, see LICENSE for details"
    print ""
    print "Connection Details:"
    print "--host: URL to RHEV-M (https://<servername>)"
    print "--user: user name"
    print "--pass: password, will be asked interactively, if not given"
    print ""
    exit(0)
    
def error():
    """
    Usage information
    """
    print ""
    print "Use -h to list all possible options"
    print ""
    exit(1)

try:
    opts, args = getopt.getopt(argv[1:], "h", ["host=", "user=", "passwd="])
except getopt.GetoptError as err:
    # print help information and exit:
    print str(err)  # will print something like "option -argument not recognized"
    error()
    
# create a config object to store the RHEV configuration details
config = config()
config.parseconfig()

# parse command line
for option, argument in opts:
    if option == "-h":
        usage()
    elif option == "--exportdomain":
        exportstoragedomain=argument
    elif option =="--storagedomain":
        importstoragedomain=argument
    elif option =="--listfile":
        listfile=argument
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

dc=api.datacenters.list()
cluster=api.clusters.list()
vms=api.vms.list()
print "DataCenter"
print "=========="
for d in dc:
    print d
    print "ID: ",d.get_id()
    print "Name: ",d.get_name()
    print "----------"

print "Clusters:"
print "========="
for c in cluster: 
    print "  ID: ",c.get_id()
    print "  Name: ",c.get_name()    
    datacenter=c.get_data_center()
    ##print datacenter
    ##print dir(datacenter)
    print "  DC: ",datacenter.get_id()
    datacenter=api.datacenters.get(id=datacenter.get_id())
    print "  DC Name: ",datacenter.get_name()
    print "  DC Description: ",datacenter.get_description()
    print "----------"

print "VMs:"
print "===="
for v in vms:
    print "  ID: ",v.get_id()
    print "  Name: ",v.get_name()
    print "  Cluster: ",v.get_cluster().get_id()
    cluster=api.clusters.get(id=v.get_cluster().get_id())
    d=api.datacenters.get(id=cluster.get_data_center().get_id())
    print "  DataCenter: ",d.get_id()
    print "  DC Name: ",d.get_name()
    print "  DC Desc: ",d.get_description()
    print "  Status:",v.get_status().get_state()
    host=v.get_placement_policy().get_host()
    print "  Preferred Host:",host
    if host != None:
        print "Affinity:",v.get_placement_policy().get_affinity()    
        print "Name:",host.get_name()
        print "ID:",host.get_id()
    
    print "----------"

api.disconnect()
