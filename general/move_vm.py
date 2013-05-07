#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    skript verschiebt die angegebenen
#    VMs in einen anderen RHEV Cluster
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

from ovirtsdk.api import API
import sys
from sys import exit
from rhevtools import readfile, listvmsbycluster, config, changeclusterforvms
import getopt
from getpass import getpass

def usage():
	""" 
	Usage
	"""
	print ""
	print "Usgae:",sys.argv[0],"<command>"
	print ""
	print "--from-cluster=all VMs from the specified Cluster will be moved"
	print "--to-cluster=destinatation for all VMs"
	print "--from-file=read the list of virtual machines from this file"
	print ""
	print "Connection Parameters:"
	print "--host: https://<servername>"
	print "--user: user name"
	print "--pass: password, will be asked interactively, if not provided"
	print ""
	
try:
	opts, args = getopt.getopt(sys.argv[1:], "h", ["from-cluster=","to-cluster=","from-file=","host=","user=","pass="])
except getopt.GetoptError as err:
	# print help information and exit:
	print str(err) # will print something like "option -argument not recognized"
	usage()
	exit(2)
	
dstcluster=""
srccluster=""
srcfile=""

# parse command line options
for option, argument in opts:
	if option == "-h":
		usage()
	elif option == "--from-cluster":
		srccluster=argument
	elif option == "--from-file":
		srcfile=argument
	elif option =="--to-cluster":
		dstcluster=argument
	elif option== "--user":
		config.rhevmconfig["user"]=argument
	elif option=="--host":
		config.rhevmconfig["host"]=argument
	elif option=="--passwd":
		config.rhevmconfig["passwd"]=argument

# verifiy specified options
if dstcluster=="":
	print "No destination Cluster was specified"
	usage()
	exit(1)
	
if srccluster=="" and srcfile=="":
	print "No source Cluster and no list file were specified"
	print "Provide a source Cluster or a file containint a list of VM names"
	usage()
	exit(1)

config=config()
config.parseconfig()

if config.rhevmconfig["host"]=="":
	print "No Hostname for RHEV-Manager specified"
	usage()
	exit(1)
elif config.rhevmconfig["user"]=="":
	print "No user name specified"
	usage()
	exit(1)
elif config.rhevmconfig["passwd"]=="":
	config.rhevmconfig['passwd']=getpass()

# Connect to RHEV-M
print "Connecting to RHEV-M..."
api = API (url=config.rhevmconfig["host"], username=config.rhevmconfig["user"], password=config.rhevmconfig["passwd"], insecure=True)
print "established"
	
# read text file
if srcfile != "":
	vms=readfile(api,srcfile)
# or fetc list of all VMs from Cluster
else:
	vms=listvmsbycluster(api,srccluster)

# and finally move the VMs around
changeclusterforvms(api,dstcluster,vms)
