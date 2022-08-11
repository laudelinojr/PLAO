import os
import datetime
import uuid
import sys
import time
import urllib3

from keystoneauth1.identity import v3
from keystoneauth1 import session
from novaclient import client as nova_client

##novo
from gnocchiclient.v1 import client
from gnocchiclient import auth


def GetHypervisorStats(PARAMETER):

    # Disable SSL Warnings when using self-signed certificates
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # API
    #IDENTITY_API = "http://10.159.205.6:5000/v3"
    IDENTITY_API = "http://200.137.82.21:5000/v3"

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

    # Get a list of hypervisors
    hypervisors = nova.hypervisors.list()

    #for k in stats:
    #    print("{:>15}: {}".format(k, stats[k]))

    if PARAMETER == "memory_use_percent":
        memory_mb_used=stats['memory_mb_used']
        memory_mb=stats['memory_mb']
        print("memory")
        print(memory_mb_used)
        print(memory_mb)
        memory_use_percent=(memory_mb_used*100)/memory_mb
        return int(memory_use_percent)

    if PARAMETER == "vcpu_use_percent":
        print("vcpu")
        vcpus=stats['vcpus']
        vcpus_used=stats['vcpus_used']        
        print(vcpus)
        print(vcpus_used)
        vcpu_use_percent=(vcpus_used*100)/vcpus
        return int(vcpu_use_percent)


    if PARAMETER == "local_gb_percent":
        print("GB disk")
        local_gb=stats['local_gb']
        local_gb_used=stats['local_gb_used']       
        print(local_gb)
        print(local_gb_used)
        local_gb_percent=(local_gb_used*100)/local_gb
        return int(local_gb_percent)

    if PARAMETER == "running_vms":
        print("runing vms")
        running_vms=stats['running_vms']
        print(running_vms)
        return int(running_vms)

    if PARAMETER == "gnocchi":
        print("ghnocch")
        # param verify : ignore self-signed certificate
        gnocchi_client = client.Client(session=sess)

        meters = gnocchi_client.metric.list()
        meters = gnocchi_client.metric.get
        print (meters)


print("percents meomry, cpu, runing vms, local gb")
print(GetHypervisorStats("memory_use_percent"))
print(GetHypervisorStats("vcpu_use_percent"))
print(GetHypervisorStats("running_vms"))
print(GetHypervisorStats("local_gb_percent"))
print(GetHypervisorStats("gnocchi"))
    