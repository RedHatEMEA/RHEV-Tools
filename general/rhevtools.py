#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    Library for RHEV-M VM Management
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

from ovirtsdk.xml import params
from ovirtsdk.infrastructure.errors import RequestError
import os
from sys import exit
from re import search, match, split
from string import rstrip
from time import sleep
import string

if __name__ == "main":
    print "rhevtools is a library used by other scripts to manage RHEV virtual machines"
    print "Version",version,lastchange
    print "Latest Version",homepage
    print ""
    print "This is a library used by the RHEV-Tools"
    print ""
    exit(0)
    
class config():
    """
    This object is used to store configuration data
    """
    
    # directory containing the configuration files
    configdir="/etc/rhev-tools/"
    # default configuration
    defaultconfig=configdir+"default.conf"

    # Dictionary of configuration settings
    # socket=number of CPU sockets
    # cores=number of CPU cores
    # disksize=size of virtual disk in GB
    # mem=amount of memory in MB
    # guaranteedmem=amount of guaranteed memory in MB
    # vnet=name of virtual/logical network
    # hv=preferred Hypervisor
    # tohv=migrate to given Hypervisor (eg. life migration)
    # template=template to use, when creating new virtual machines (Default: Blank)
    # storagedomainname of storage domain used for new virtual disks
    # cluster=name of RHEV Cluster used when creating the new virtual machine
    # createscript=execute script after VM was created
    # deletescript=execute script after VM was deleted
    # mac=MAC address for new virtual NIC
    # display=display mode (vnc or spice)
    # osver=Operating System
    # values are: rhel_6x64, rhel_5x64, windows_2008r2
    # fqdn=full qualified domain name, used when communicating with Satellite/Cobbler
    # serial=1 to enable serail console support (default: 0)
    vmconfig={
        "sockets":0,
        "cores":0,
        "disksize":0,
        "mem":0,
        "guaranteedmem":0,
        "vnet":"",
        "hv":"",
        "tohv":"",
        "template":"",
        "storagedomain":"",
        "cluster":"",
        "createscript":"",
        "deletescript":"",
        "osver":"",
        "mac":"",
        "serial":"",
        "display":"",
        "hamode":"",
        "haprio":"",
        "fqdn":""
    }
    # Name of virtual machine
    vmname=""
    # Dictionary with RHEV configuration data
    # host=URL of RHEV-M (https://<hostname>)
    # user=user namee
    # pass=password
    rhevmconfig={"host":"",
                 "user":"",
                 "passwd":""
                 }
    
    def parseconfig(self):
        """
        parse configuration files
        also check if there is a machine-specific configuration file,
        which will override defaults
        """
        print "Loading default configuration file %s..." % (self.defaultconfig)
        self.readconfig(self.defaultconfig)
        
        __configfile=self.configdir+self.vmname+".conf"
        
        if os.access(__configfile, os.R_OK):
            print "Machine specific config found, parsing..."
            self.readconfig(__configfile)
        
    def readconfig(self,config):
        """
        read given configuration file
        """
        
        if not os.access(config, os.R_OK):
            print "Could not read configuration file %s" % (config)
            exit(1)

        sockets=0
        cores=0
        serial=0
        disksize=0
        vnet=""
        mem=0
        guaranteedmem=0
        hv=""
        tohv=""
        template=""
        storagedomain=""
        cluster=""
        createscript=""
        deletescript=""
        osver=""
        mac=""
        hamode=""
        haprio=""
        display=""
        fqdn=""
        host=""
        user=""
        passwd=""
        
        c=open(config, 'r')
        for line in c:
            if match("#",line):
                # skip comments
                continue
            elif match("sockets=",line):
                sockets=split('=',line)[1]
                sockets=rstrip(sockets)
            elif match("cores=",line):
                cores=split('=',line)[1]
                cores=rstrip(cores)
            elif match("disksize=",line):
                disksize=split("=",line)[1]
                disksize=rstrip(disksize)
            elif match("vnet=",line):
                vnet=split("=",line)[1]
                vnet=rstrip(vnet)
            elif match("mem=",line):
                mem=split("=",line)[1]
                mem=rstrip(mem)
            elif match("guaranteedmem=",line):
                guaranteedmem=split("=",line)[1]
                guaranteedmem=rstrip(guaranteedmem)
            elif match("template=",line):
                template=split("=",line)[1]
                template=rstrip(template)
            elif match("hv=",line):
                hv=split("=",line)[1]
                hv=rstrip(hv)
            elif match("tohv=",line):
                tohv=split("=",line)[1]
                tohv=rstrip(tohv)
            elif match("storagedomain=",line):
                storagedomain=split("=",line)[1]
                storagedomain=rstrip(storagedomain)
            elif match("cluster=",line):
                cluster=split("=",line)[1]
                cluster=rstrip(cluster)
            elif match("osver=",line):
                osver=split("=",line)[1]
                osver=rstrip(osver)
            elif match("fqdn=",line):
                fqdn=split("=",line)[1]
                fqdn=rstrip(fqdn)
            elif match("createscript=",line):
                createscript=split("=",line)[1]
                createscript=rstrip(createscript)            
            elif match("deletescript=",line):
                deletescript=split("=",line)[1]
                deletescript=rstrip(deletescript)            
            elif match("display=",line):
                display=split("=",line)[1]
                display=rstrip(display)
            elif match("mac=",line):
                mac=split("=",line)[1]
                mac=rstrip(mac)
            elif match("hamode=",line):
                hamode=split("=",line)[1]
                hamode=rstrip(hamode)
            elif match("haprio",line):
                haprio=split("=",line)[1]
                haprio=rstrip(haprio)
            elif match("serial",line):
                serial=split("=",line)[1]
                serial=rstrip(serial)
            elif match("host",line):
                host=split("=",line)[1]
                host=rstrip(host)
            elif match("user",line):
                user=split("=",line)[1]
                user=rstrip(user)
            elif match("pass",line):
                passwd=split("=",line)[1]
                passwd=rstrip(passwd)      
                  
        if sockets>0:        
            self.vmconfig["sockets"]=sockets
        if cores>0:        
            self.vmconfig["cores"]=cores
        if disksize>0:
            self.vmconfig["disksize"]=disksize
        if vnet!="":
            self.vmconfig["vnet"]=vnet
        if mem>0:
            self.vmconfig["mem"]=mem
        if guaranteedmem>0:
            self.vmconfig["guaranteedmem"]=guaranteedmem
        if hv!="":
            self.vmconfig['hv']=hv
        if tohv!="":
            self.vmconfig['tohv']=tohv
        if fqdn!="":
            self.vmconfig['fqdn']=fqdn
        if template!="":
            self.vmconfig['template']=template
        if storagedomain!="":
            self.vmconfig['storagedomain']=storagedomain
        if cluster!="":
            self.vmconfig['cluster']=cluster
        if createscript!="":
            self.vmconfig['createscript']=createscript
        if deletescript!="":
            self.vmconfig['deletescript']=deletescript
        if display!="":
            self.vmconfig['display']=display
        if osver!="":
            self.vmconfig["osver"]=osver
        if mac!="":
            self.vmconfig['mac']=mac
        if haprio!="":
            self.vmconfig['haprio']=haprio
        if hamode!="":
            self.vmconfig['hamode']=hamode
        if host!="":
            self.rhevmconfig['host']=host
        if user!="":
            self.rhevmconfig['user']=user
        if passwd!="":
            self.rhevmconfig['passwd']=passwd
            
        
class vm():
    """
    virtual machine object
    """
     
    def __init__(self,vmname,vmconfig,connect):
        """
        create new VM object
        """
        
        # store connection to RHEV-M
        self.connect=connect
        # store VM details
        self.vmconfig=vmconfig
        # store the name of the VM
        self.vmname=vmname
    
    def start(self):
        """
        start VM and use preferred host from config, if set
        """
        if self.vmname=="":
            print "No VM name specified"
            exit(1)
        
        if self.status()!="down":
            print "VM",self.vmname,"is not in UP state"
            exit(1)

        response=self.connect.vms.get(name=self.vmname).start()
        return(response)
        
    def stop(self):
        """
        stop VM
        """
        if self.vmname=="":
            print "No VM name specified"
            exit(1)

        if self.status()!="up" and self.status()!="powering_up":
            print "VM",self.vmname,"is not in UP or POWERING_UP state"
            exit(1)

        response=self.connect.vms.get(name=self.vmname).stop()
        return(response)
                    
    def migrate (self):
        """
        VM Live Migration, use preferred host from config as destination, if none specified
        """
        if self.vmname=="":
            print "No VM name specified"
            exit(1)
            
        if self.status()!="up":
            print "VM",self.vmname,"is not in UP state"
            exit(1)

        if self.vmconfig['tohv']!="":
            print "Starting Live Migration of %s to Hypervisor %s..." % (self.vmname,"to Hypervisor", self.vmconfig['tohv'])
            hostid=self.connect.hosts.get(name=self.vmconfig["tohv"])
            self.connect.vms.get(name=self.vmname).migrate(params.Action(host=hostid))
        else:
            print "Starting Live Migration of %s..." % (self.vmname)
            self.connect.vms.get(name=self.vmname).migrate()
                
    def shutdown(self):
        """
        Shutdown VM
        """
        if self.vmname=="":
            print "No VM name specified"
            exit(1)

        if self.status()!="up":
            print "VM",self.vmname,"is not in UP state"
            exit(1)

        response=self.connect.vms.get(name=self.vmname).shutdown()
        return(response)

    def status(self):
        """
        VM status (UP, DOWN, etc)
        """

        if self.vmname=="":
            print "No VM name specified"
            exit(1)

        response=self.connect.vms.get(name=self.vmname).get_status().get_state()
        return(response) 

    def console(self,rhevmconfig):
        """
        connect to serial console of given VM
        """

        host=rhevmconfig['host']
        host=string.replace(host,"https://","")
        host=string.replace(host,"http://","")

        cmd="locateVm.py --user "+rhevmconfig['user']+" --pass "+rhevmconfig['passwd']+" --address "+host+" --port 443 --vm "+self.vmname
        rt=os.system(cmd)
        if rt!=0:
            print "Opening Console failed:"
            print cmd
            exit(1)

    def details(self):
        """
        print details about the given VM
        """

        if self.vmname=="":
            print "No VM name specified"
            exit(1)

        try:
            vm=self.connect.vms.get(name=self.vmname)
        except:
            print "VM",self.vmname,"not found"
            exit(1)

        if vm==None:
            print "VM",self.vmname,"not found"
            exit(0)

        print "Name:",vm.name
        print "Type:",vm.get_type()
        print "Status:",vm.get_status().get_state()
        vm_memory=vm.memory/1024/1024
        print "Memory:",vm_memory,"MB"
        guaranteed=vm.get_memory_policy().get_guaranteed()/1024/1024
        print "Memory (guaranteed):",guaranteed,"MB"
        print "CPU Cores:",vm.get_cpu().topology.cores
        print "CPU Sockets:",vm.get_cpu().topology.sockets
        print "Display Type:",vm.get_display().type_
        ha=vm.get_placement_policy()
        print "HA settings:"
        h=vm.get_high_availability()
        print "\tEnabled:",h.enabled
        print "\tPriority:",h.priority
        print "\tAffinity:",ha.affinity
        print "\tHosts:",ha.host
        print "Operating System:",vm.os.type_
        prop=vm.get_custom_properties()
        if prop != None:
            print "Custom Properties:"
            p=prop.get_custom_property()
            for i in p:
                print "\t",i.name,":",i.value
        else:
            print "Custom Properties: None"
        print "Disks:"
        for disk in vm.get_disks().list():
            print "\tName:",disk.name                 
            disk_size=disk.size/1024/1024/1024
            print "\tSize:",disk_size,"GB"
            print "\tBootable:",disk.get_bootable()
        print "NICs:"
        for nic in vm.get_nics().list():
            print "\tName:",nic.name
            print "\tType:",nic.interface
            print "\tMAC:",nic.mac.address
        return

    def delete(self,config):
        """
        Delete VM
        """

        if self.vmname=="":
            print "No VM name specified"
            exit(1)

        vm=self.connect.vms.get(name=self.vmname)
        if vm==None:
            print "VM",self.vmname,"not found"
            exit(1)

        if self.status()!="down":
            print "VM is not in DOWN state"
            exit(1)

        disks=vm.disks.list()
        for disk in disks:
            print "Delete virtual disk %s..." % (disk.name)
            disk.delete(async=False)

        print "Deleting VM %s..." % (self.vmname)
        vm.delete()

        # Verify VM was really deleted
        v=self.connect.vms.get(name=self.vmname)
        while v!=None:
                sleep(1)
                v=self.connect.vms.get(name=self.vmname)

        print "Done."

        # delete VM config /etc/rhevm-scripts/vm.conf
        __configfile=config.configdir+self.vmname+".conf"
        if os.access(__configfile, os.R_OK):
            try:
                os.remove(__configfile)
            except:
                print "Could not remove configuration file",__configfile

        # call external script, after VM was deleted
        deletescript=self.vmconfig['deletescript']
        if deletescript!="":
            print "Executing external script..."
            cmd=deletescript+" "+self.vmconfig['fqdn']+" "+self.vmname
            print cmd
            rt=os.system(cmd)
            if rt!=0:
                print "Return Code was:",rt
                exit(1)

        return

    def _update(self,vm):
        """
        since update() sometimes failes, this wrapper is used for critical calls
        """
        counter=1
        success=0
        while success==0:
            try:
                vm.update()
                success=1
            except:
                counter+=1
                sleep(1)
                pass
        if counter>1:
            print "Number of retries:",counter

    def create(self):
        """
        Create new VM
        """

        if self.vmname=="":
            print "No VM name was specified"
            exit(1)

        # check if a VM with this name already exists
        vm=self.connect.vms.get(name=self.vmname)
        if vm!=None:
            print "VM",self.vmname,"already exists"
            exit(1)

        # verify the RHEV Cluster was specified
        if self.vmconfig['cluster']=="":
            print "No RHEV Cluster was specified"
            exit(1)

        # verify the RHEV Cluster actually exists
        cluster=self.connect.clusters.get(name=self.vmconfig['cluster'])
        if cluster==None:
            print "Cluster",self.vmconfig['cluster'],"not found"
            exit(1)

        # verify virtual disk size
        disksize=int(self.vmconfig['disksize'])
        ## TODO this check will fail if disksize is not specified or not an convertable
        if disksize==0:
            print "Größe für virtuelle Disk nicht korrekt"
            exit(1)


        # check if StorageDomain was specified
        if self.vmconfig['storagedomain']=="":
            print "Storage Domain was not specified"
            exit(1)

        # verify StorageDomain exists
        sd=self.connect.storagedomains.get(name=self.vmconfig['storagedomain'])
        if sd==None:
            print "Storage Domain",self.vmconfig['storagedomain'],"not found"
            exit(1) 

        # check if NIC was specified
        if self.vmconfig['vnet']=="":
            print "No virtual network specified"
            exit(1)

        # check if logical network exists
        nic_network=self.connect.networks.get(name=self.vmconfig['vnet'])
        if nic_network==None:
            print "Logical Netzwerk",self.vmconfig['vnet'],"not found"
            exit(1)
        
        # read MAC - but is optional
        mac=self.vmconfig['mac']

        # check memory size
        t=int(self.vmconfig['mem'])
        if t>20480 and self.vmconfig['osver']=='':
            print "Memory size is more then 20 GB, but OS is not set"
            exit(1)
        
        # check if memory size was specified
        if self.vmconfig['mem']=="":
            print "Memory size was not specified"
            exit(1)

        # create Vm
        print "Creating virtual machine",self.vmname,"..."

        # check if this instance will be based on a template, and if that template exists
        template=self.vmconfig['template']
        if template!="":
            t=self.connect.templates.get(name=template)
            if t==None:
                print "Template",template,"not found"
                exit(1)
            else:
                print "\tUsing Template",template,"..."
        else:
            print "\tUsing Blank Template ..."
            t=self.connect.templates.get(name="Blank")

        vm_params=params.VM(name=self.vmname,
            cluster=cluster,
            template=t,
            os=params.OperatingSystem(boot=[params.Boot(dev="hd"),params.Boot(dev="network")]),
            type_='server'
        )
        self.connect.vms.add(vm=vm_params)

        # VM Object 
        vm=self.connect.vms.get(name=self.vmname)

        # set Display Mode
        display=self.vmconfig['display']
        if display=="vnc" or display=="spice":
            print "Set Display Mode to",display,"..."
            vm.display.type_=display
            self._update(vm)

        # set OS version
        osver=self.vmconfig["osver"]
        if osver!="":
            print "Set OS Version to",osver,"..."
            vm.os.type_=osver
            self._update(vm)

        # set guaranteed memory, if configured
        if self.vmconfig['guaranteedmem']>0:
            print "Set Guaranteed Memory to",self.vmconfig['guaranteedmem'],"MB..."
            guaranteed=int(self.vmconfig['guaranteedmem'])*1024*1024
            vm.memory_policy.set_guaranteed(guaranteed)
            vm.update()

        # set memory size after OS Type
        # this will avoid problems with RAM >20 GB
        vm_memory=int(self.vmconfig['mem'])*1024*1024
        print "Set Memory Size to",self.vmconfig['mem'],"MB..."
        vm.memory=int(vm_memory)

        # enable HA feature
        hamode=self.vmconfig['hamode']
        if self.vmconfig['haprio']!="":
            haprio=int(self.vmconfig['haprio'])
        if hamode!="":
            print "Setting HA Mode..."
            if hamode=="True" or hamode=="False":
                print "\tEnabled:",hamode
                vm.high_availability.enabled=hamode
            else:
                print "HA Mode must be True or False, ignoring",hamode
            if hamode=="True":
                #if haprio==1 or haprio==50 or haprio==100:
                if haprio>0 and haprio<101:
                    print "\tHA Priority:",haprio
                    vm.high_availability.priority=haprio
                else:
                    print "HA Priority must be in the range 1 to 100, ignoring",haprio
        vm.placement_policy.affinity="migratable"
        #ha=vm.get_placement_policy()
        self._update(vm)

        # set CPU topology
        if self.vmconfig['sockets']!="":
            sockets=int(self.vmconfig['sockets'])
        else:
            sockets=1
        if self.vmconfig['cores']!="":
            cores=int(self.vmconfig['cores'])
        else:
            cores=1
        print "Set Number of cores to",cores,"and sockets to",sockets
        vm.cpu.topology.cores=cores
        vm.cpu.topology.sockets=sockets
        vm.update()
       
        # serial console
        if self.vmconfig['serial']==1:
            print "Setting Custom Property SerialConsole to 0..."
            p=params.CustomProperties()
            prop=params.CustomProperty(name="SerialConsole",value="0")
            p.add_custom_property(prop)
            vm.set_custom_properties(p)
            vm.update()

        # add virtual disk
        if template=="":
            print "Createing vritual disk...",disksize,"GB"
            disksize=disksize*1024*1024*1024
            storagedomain = params.StorageDomains(storage_domain=[self.connect.storagedomains.get(name=self.vmconfig['storagedomain'])])
            disk_params = params.Disk(storage_domains=storagedomain,
                size=disksize,
                type_="system",
                interface="virtio",
                format="cow",
                bootable=True
            )
            vm.disks.add(disk_params,expect='201-created')

            # Give RHEV some time to create the disk
            sleep (3)
            # ...and verify no disk is in state locked
            disks=vm.disks.list()
            for disk in disks:
                while disk.get_status().get_state() == "locked":
                    sleep(3)
                    disk=self.connect.disks.get(alias=disk.name)
    
        # add virtual network interface
        if template!="":
            # if this was based on an template, we have to remove old NICs first
            print "Removing existing network interfaces..."
            for nic in vm.nics.list():
                nic.delete()
                self._update(vm)

        print "Vebinde mit Netzwerk Interface..."
        nic_params = params.NIC(name='nic1',interface='virtio',network=nic_network)
        vm.nics.add(nic_params)

        # set MAC address if specified
        if mac !="":
            # TODO there should be only one nic 
            for n in vm.nics.list():
                n.mac.address=mac
                n.update()

        # setting preferred host
        print "Setting preferred hosts to",self.vmconfig['hv']
        vm.placement_policy.affinity="migratable"
        if self.vmconfig['hv']!="":
            hostid=self.connect.hosts.get(name=self.vmconfig['hv'])
            if hostid==None:
                print "Host",self.vmconfig['hv'],"not fuond, ignoring"
            else:
                vm.placement_policy.host=hostid
                vm.update()

        # call external script
        createscript=self.vmconfig['createscript']
        if createscript!="":
            print "Executing script:"
            cmd=createscript+" "+self.vmname
            print cmd
            rt=os.system(cmd)
            if rt!=0:
                print "Return Code was",rt
                exit(1)

        # einschalten
        print "Starting virtual machine ..."
        vm.start()
        
def readfile(connect,filename):
    """
    read the the file and return a list of virtual machine names
    """
    
    if not os.access(filename, os.R_OK):
        print "Could not open file",filename
        exit(1)
        
    vmlist=[]
    vmfile=open(filename,'r')
    for line in vmfile:
        if match("#",line):
            # ignore comments
            continue
        elif search('^\s*$',line):
            # ignore empty lines
            continue
        else:
            vmname=rstrip(line)
            vm=connect.vms.get(name=vmname)
            vmlist.append(vm)
            
    if vmlist.__len__()==0:
        print "There were no virtual machine names found in",filename
        exit(1)
        
    return(vmlist)

def listvmsbycluster(connect,cluster):
    """
    returns a list of VMs running on the specified cluster
    """

    query="cluster ="+cluster
    vms=connect.vms.list(query=query)
    return(vms)

def changeclusterforvms(connect,dstcluster,vms):
    """
    will move all VMs to the destination cluater
    """

    if connect.clusters.get(name=dstcluster)==None:
        print "Destination Cluster",dstcluster,"not found"
        exit(1)

    for vm in vms:
        #v=connect.vms.get(name=vm)
        print "Changinig Cluster for VM",vm.name,"to",dstcluster,"..."
        print vm.name
        vm.cluster.id=connect.clusters.get(name=dstcluster).id
        vm.update()

def importvm(connect,vm,nfsexport,storagedomain,cluster):
    """
    import the specified VM from NFS export into storagedomain in the RHEV Cluster
    connect is the RHEV connection object
    """
    success=0
    counter=0
    
    # TODO: check if the given VM is available in the export domain
    
    while success==0:
        counter+=1
        try: 
            connect.storagedomains.get(nfsexport).vms.get(vm).import_vm(params.Action(storage_domain=connect.storagedomains.get(storagedomain), cluster=connect.clusters.get(name=cluster)))
        except RequestError, err:
            print "Error while importing VM "+vm+":",err
            os.system("logger Error while importing VM "+vm+":"+err)
            if counter > 10:
                os.system("logger Error while importing VM "+vm+" more than 10 times, skipping")
                print "Giving up with this VM."
                break
        # import was successful
        success=1
        
    if success==1:
        return(0)
    else:
        return(1)
