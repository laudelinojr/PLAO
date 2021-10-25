import socket
import time
import sys
import datetime
import platform
import subprocess
import psutil

# imports to  GetHypervisorStats
import os
import datetime
import uuid
import sys
import time
import urllib3

from keystoneauth1.identity import v3
from keystoneauth1 import session
from novaclient import client as nova_client


def GetHypervisorStats(OPENSTACK_FROM, PARAMETER):
    # Disable SSL Warnings when using self-signed certificates
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    #if ( OPENSTACK_FROM == "10.159.205.7" ):
        # API
    #    IDENTITY_API = "http://10.159.205.6:5000/v3"
    #if  ( OPENSTACK_FROM == "10.159.205.13" ):
    # API
    #IDENTITY_API = "http://10.159.205.12:5000/v3"
    IDENTITY_API = "http://"+OPENSTACK_FROM+":5000/v3"

    # OpenStack User and Project. From the OpenRC file.
    PROJECT_NAME = "admin"
    PROJECT_DOMAIN_ID = "default"
    USER_DOMAIN_NAME = "Default"
    USERNAME = "admin"
    PASSWORD = "keystoneadmin"
    auth = v3.Password(auth_url=IDENTITY_API,
                    username=USERNAME,
                    password=PASSWORD,
                    project_name=PROJECT_NAME,
                    user_domain_name=USER_DOMAIN_NAME,
                    project_domain_id=PROJECT_DOMAIN_ID)
    # Create a session with the credentials
    sess = session.Session(auth=auth, verify=False)
    # Create nova client with the session created
    nova = nova_client.Client(version='2.1', session=sess)
    # Get hypervisor statistics over all compute nodes
    stats = nova.hypervisor_stats.statistics()._info
    hypervisors = nova.hypervisors.list()
    #print ("dentro antes do if parameter")
    if PARAMETER == "memory_use_percent":
        memory_mb_used=stats['memory_mb_used']
        memory_mb=stats['memory_mb']
        memory_use_percent=(memory_mb_used*100)/memory_mb
        return str(round(memory_use_percent))

    if PARAMETER == "vcpu_use_percent":
        vcpus=stats['vcpus']
        vcpus_used=stats['vcpus_used']        
        vcpu_use_percent=(vcpus_used*100)/vcpus
        return str(round(vcpu_use_percent))

    if PARAMETER == "local_gb_percent":
        local_gb=stats['local_gb']
        local_gb_used=stats['local_gb_used']       
        local_gb_percent=(local_gb_used*100)/local_gb
        return str(round(local_gb_percent))

    if PARAMETER == "running_vms":
        running_vms=stats['running_vms']
        return str(round(running_vms))


GetHypervisorStats("10.159.205.8", running_vms)