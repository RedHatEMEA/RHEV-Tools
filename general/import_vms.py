#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    Script to import the VMs in a given listfile
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
#    Modifications:
#       2013-05-31 - Miguel Pérez Colino <mperez at redhat dot com>
#


version="0.1.2"
lastchange="2013-03-31"
homepage="http://github.com/RedHatEMEA/RHEV-Tools"
author="Christian Bolz <cbolz at redhat dot com>"

from ovirtsdk.api import API
from rhevtools import config, vm, importvm
from sys import argv, exit
from re import match
import os
import getopt
import time
from getpass import getpass

def usage():
    """
    Usage
    """
    print ""
    print "Tool to import virtual machines from a specified list"
    print "Version",version,lastchange
    print "Latest Version",homepage,"by",author
    print "This is free software, see LICENSE for details"
    print ""
    print "\nUsage:",argv[0],"<listfile> <storagedomain> <exportdomain>"
    print "--listfile is the text file containing the VMs you want to import"
    print "--storagedoman is the name of the StorageDomain you want the VM to be imported to"
    print "--exportdomain is the NFS Export you import the VMs from\n"
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
    opts, args = getopt.getopt(argv[1:], "h", ["host=", "user=", "passwd=", "storagedomain=", "exportdomain=","listfile="])
except getopt.GetoptError as err:
    # print help information and exit:
    print str(err)  # will print something like "option -argument not recognized"
    error()
    
# create a config object to store the RHEV configuration details
config = config()
config.parseconfig()

# setup some variables
exportstoragedomain=""
importstoragedomain=""
listfile=""

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
elif listfile=="":
    print "No listfile was specified."
    error()
elif exportstoragedomain=="":
    print "No export storage domain was specified."
    error()
elif importstoragedomain=="":
    print "No import storage domain was specified."
    error()  

# Connect to RHEV-M
print "Connecting to RHEV-M %s..." % (config.rhevmconfig['host'])
api = API (url=config.rhevmconfig["host"], username=config.rhevmconfig["user"], password=config.rhevmconfig["passwd"], insecure=True)
print "Connection established"
print ""

if not os.access(listfile,os.R_OK):
    print "\nCannot read",listfile,"\n"
    exit(1)

print "\nParsing",listfile,"...\n"
content=open (listfile,'r')
importvms={}
lines=content.readlines()
for line in lines:
    if match("#",line):
        continue
    if line != '\n':
        line=line.rstrip('\n')
        [vmname,storagedomain,host,status,alloc,total,cluster]=line.split(';')[0:7]
        print "Found VM",vmname,"in file"
        importvms[vmname]={}
        importvms[vmname]['host']=host
        importvms[vmname]['status']=status
        importvms[vmname]['alloc']=alloc
        importvms[vmname]['total']=total
        importvms[vmname]['cluster']=cluster

print "\nVerifying Export Domain..."
exportdomain=api.storagedomains.get(name=exportstoragedomain)
if exportdomain == None:
    print "ExportDomain",exportstoragedomain,"not found"
    exit(1)
else:
    print "Ok"

print "\nVerifying Target StoragDomain..."
storagedomain=api.storagedomains.get(name=importstoragedomain)
if storagedomain == None:
    print "StorageDomain",importstoragedomain,"not found"
    exit(1)
else:
    print "Ok\n"

# array of VMs which will be started after import
uplist=[]

i=raw_input("Press RETURN to continue")

for currentvm in importvms.keys():
    cluster=importvms[currentvm]['cluster']
    print "\nImporting",currentvm,"..."
    print "\tChecking if VM already exists..."
    rc=api.vms.get(name=currentvm)
    if rc != None:
        print "\tVM already exists, skipping."
        continue
    else:
        print "\tImporting into Cluster:",cluster
        print "\tUsing Storage Domain:",importstoragedomain
        print "\tVM does not exist, starting import... (this will take a few seconds)"

    rc=importvm(api,currentvm,exportstoragedomain,importstoragedomain,cluster)
    if rc==0:
        if importvms[currentvm]['status']=="Up":
            print "\tWill mark this VM for Power Up after import is complete."
            uplist.append(currentvm)
        else:
            print "\tImport failed, will not try to start this VM"

# make VMs with more than one virtual disk startable
# Case #00753220
print ""
rc=os.system("psql engine postgres -c \"update base_disks set disk_alias = \'disk\' where disk_alias is null;\"")
if rc != 0 : 
    print "Updating database failed."
else:
    print "Update of database was successful."

if len(uplist)>0:
    while len(uplist)>0:
        print "\nVerifying VMs are in the correct Power State..."
        for currentvm in uplist:
            vmobject=vm(currentvm, config.vmconfig, api)
            state=vmobject.status()
        
            if state!="down":
                print "\tVM",currentvm,"not in status down, waiting..."
            else:
                print "\tSetting preferred Host for",currentvm,"to",importvms[currentvm]['host']
                hostid=api.hosts.get(name=importvms[currentvm]['host'])
                v=api.vms.get(name=currentvm)
                v.usb.enabled='false'
                v.placement_policy.affinity="migratable"
                v.placement_policy.host=hostid
                v.update()
                print "\tVM",currentvm,"is down, starting it now."
                api.vms.get(name=currentvm).start()
                uplist.remove(currentvm)
        print "\tSleeping for 20 seconds...\n"
        time.sleep(20)    
else:
    print "\nNo VMs marked for startup after import.\n"

