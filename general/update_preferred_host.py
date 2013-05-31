#!/usr/bin/python
#
# This script will update the preferred hosts as specified in listfile
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
import sys
import os
import getopt
from getpass import getpass
from rhevtools import config
from sys import exit, argv

# TODO
# check preferred HV

def usage():
	"""
	Usage
	"""
	print "Tool to manage RHEV virtual machines"
	print "Version",version,lastchange
	print "Latest Version",homepage,"by",author
	print "This is free software, see LICENSE for details"
	print "\nUsage:",sys.argv[0]
	print "This script will update the preferred host for all VMs in the given listfile"
	print "--listfile: is the text file conatining the VMs you want to import"
	print ""
	print "Connection Details:"
	print "--host: URL to RHEV-M (https://<servername>)"
	print "--user: user name"
	print "--pass: password, will be asked interactively, if not given"
	print ""
	exit(0)
	
try:
	opts, args = getopt.getopt(argv[1:], "h", ["listfile=" "host=", "user=", "passwd="])
except getopt.GetoptError as err:
	# print help information and exit:
	print str(err)  # will print something like "option -argument not recognized"
	usage()
	exit(2)

# create a config object to store the RHEV configuration details
config = config()
# check which command will have to be executed
command = ""

# parse command line
for option, argument in opts:
	if option == "-h":
		usage()
		exit(0)
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
	usage()
	exit(1)
elif config.rhevmconfig["user"] == "":
	print "No user name was specified."
	usage()
	exit(1)
elif config.rhevmconfig["passwd"] == "":
	config.rhevmconfig['passwd'] = getpass() 

if not os.access(listfile,os.R_OK):
	print "\nCannot read",listfile,"\n"
	exit(1)

print "\nParsing",listfile,"...\n"
content=open (listfile,'r')
importvms={}
lines=content.readlines()
for line in lines:
	if line != '\n':
		line=line.rstrip('\n')
		[vmname,dststoragedomain,host,status,alloc,total,cluster]=line.split(';')[0:7]
		print "Found VM",vmname,"in file"
		importvms[vmname]={}
		importvms[vmname]['host']=host
		importvms[vmname]['status']=status
		importvms[vmname]['alloc']=alloc
		importvms[vmname]['total']=total
		importvms[vmname]['cluster']=cluster

# Connect to RHEV-M
print "Connecting to RHEV-M..."
api = API (url=config.rhevmconfig["host"], username=config.rhevmconfig["user"], password=config.rhevmconfig["passwd"], insecure=True)
print "Connection established"
print ""

uplist=[]

for vm in importvms.keys():
	uplist.append(vm)

if len(uplist)>0:
	while len(uplist)>0:
		for vm in importvms.keys():
			print "\nSetting preferred Host for",vm,"to",importvms[vm]['host']
			hostid=api.hosts.get(name=importvms[vm]['host'])
			v=api.vms.get(name=vm)
			v.placement_policy.affinity="migratable"
			v.placement_policy.host=hostid
			v.update()
			uplist.remove(vm)
else:
	print "\nNo VMs found in given file",listfile

