#!/usr/bin/python3

# https://gnocchi.xyz/gnocchiclient/api.html
# https://docs.openstack.org//python-novaclient/latest/doc-python-novaclient.pdf

import json
import shade
import os
import datetime
import uuid
import sys
import time
import urllib3
import argparse
import pandas as pd

from keystoneauth1.identity import v3
from keystoneauth1 import session
from gnocchiclient.v1 import client
from gnocchiclient import auth
from novaclient import client as nclient


class Logger(object):
    def __init__(self, logfile):
        self.terminal = sys.stdout
        self.log = open(logfile, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass


# Get current dir
absolute_path = os.path.abspath(__file__)
script_name = os.path.basename(__file__)
current_dir = absolute_path[0:-(len(script_name))]

# Disable SSL Warnings when using self-signed certificate
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Parser dos parametros
parser = argparse.ArgumentParser()
parser.add_argument("-vmid", "--instance-id", dest='instance_id', help="OpenStack Instance ID.")
parser.add_argument("-g", "--granularity", dest='granularity', help="Metric Granularity.")
parser.add_argument("-l", "--label", dest='label', help="Traffic Label.")
#parser.add_argument("-start", "--start-time", dest='starttime', help="Start time to colect metrics. UTC ISO Format (\"YYYY-MM-DD HH:MM:SS+00:00\").")
#parser.add_argument("-stop", "--stop-time", dest='stoptime', help="End time to colect metrics. UTC ISO Format (\"YYYY-MM-DD HH:MM:SS+00:00\").")
args = parser.parse_args()
#print(sys.argv)
if len(sys.argv)<7:
    parser.print_help(sys.stderr)
    print("\n")
    exit(1)

# Command line arguments
OPENSTACK_VM_ID = args.instance_id.lower()
GRANULARITY = int(args.granularity)
LABEL = args.label.lower()
## Start/Stop in UTC ISO Format
#START = args.starttime
#STOP = args.stoptime
#START = "2021-03-23 18:35:00+00:00"
#STOP = "2021-03-23 18:41:00+00:00"
START = "2021-04-13 19:38:33+00:00"
STOP = "2021-04-13 19:43:36+00:00"
## Dataset name
DATASET_OUT_FILE = 'dataset_'+LABEL+'.csv'

# Class to autenticate on OpenStack and return authentication session
class OpenStack_Auth():
    def __init__(self, cloud_name):
        self.cloud = shade.openstack_cloud(cloud=cloud_name)
        # Import credentials witch clouds.yml
        self.auth_dict = self.cloud.auth
        self.auth = v3.Password(auth_url=str(self.auth_dict['auth_url']),
                                username=str(self.auth_dict['username']),
                                password=str(self.auth_dict['password']),
                                project_name=str(
                                    self.auth_dict['project_name']),
                                user_domain_name=str(
                                    self.auth_dict['user_domain_name']),
                                project_domain_id=str(self.auth_dict['project_domain_id']))
        # Create a session with credentials clouds.yml
        self.sess = session.Session(auth=self.auth, verify=False)

    # Return authentication session
    def get_session(self):
        return self.sess


# Class to get measures from Gnocchi
class Gnocchi():
    def __init__(self, session):
        # param verify : ignore self-signed certificate
        self.gnocchi_client = clie
        nt.Client(session=session)

    '''Get Metric CPU Utilization (%)
        Arguments: resource_id (Identification Virtual Machine)
                    granularity in format integer (granularity to retrieve (in seconds))
                    vcpus (number of vcpus alocated to Virtual Machine)
        Output: Return measure
    '''
    def get_metric_cpu_utilization(self, resource_id, granularity, vcpus, start, stop):
        # Divide per vcpus (OpenStack sum all processors times)
        operations = "(/ (* (/ (metric cpu rate:mean) "+str(granularity*1000000000.0)+") 100) "+str(vcpus)+")"
        # print(operations)
        meters = self.gnocchi_client.aggregates.fetch(operations,
                                                      # resource_type='generic',
                                                      search="id="+resource_id,
                                                      start=start,
                                                      stop=stop,
                                                      granularity=granularity)
        
        meters = meters['measures'][resource_id]['cpu']['rate:mean']
        df = pd.DataFrame(meters, columns =['timestamp', 'granularity', 'cpu'])
        print("\n")
        print(df.head())
        return(df)


    '''Get Metric memory_usage (MB)
    Argumentos: resource_id (Identification VM)
                granularity in format integer(granularity to retrieve (in seconds)) 
    '''
    def get_metric_memory_usage(self, resource_id, granularity, start, stop):
        meters = self.gnocchi_client.metric.get_measures('memory.usage',
                                                           start=start,
                                                           stop=stop,
                                                           resource_id=resource_id,
                                                           granularity=granularity)
        
        df = pd.DataFrame(meters, columns =['timestamp', 'granularity', 'memory_usage'])
        print("\n")
        print(df.head())
        return(df)

    # Metric memory.swap.in Cumulative
    def get_metric_swap_in(self, resource_id, granularity, start, stop):
        meters = self.gnocchi_client.metric.get_measures('memory.swap.in',
                                                           start=start,
                                                           stop=stop,
                                                           resource_id=resource_id,
                                                           granularity=granularity)
        
        df = pd.DataFrame(meters, columns =['timestamp', 'granularity', 'memory_swap_in'])
        print("\n")
        print(df.head())
        return(df)

    # Metric memory.swap.out Cumulative
    def get_metric_swap_out(self, resource_id, granularity, start, stop):
        meters = self.gnocchi_client.metric.get_measures('memory.swap.out',
                                                           start=start,
                                                           stop=stop,
                                                           resource_id=resource_id,
                                                           granularity=granularity)
                                                           
        
        df = pd.DataFrame(meters, columns =['timestamp', 'granularity', 'memory_swap_out'])
        print("\n")
        print(df.head())
        return(df)


    def get_metric_disk_read_requests(self, resource_id, granularity, start, stop):
        meters = self.gnocchi_client.metric.get_measures('disk.device.read.requests',
                                                           start=start,
                                                           stop=stop,
                                                           resource_id=resource_id,
                                                           granularity=granularity,
                                                           aggregation='rate:mean')
        
        df = pd.DataFrame(meters, columns =['timestamp', 'granularity', 'disk_read_requests'])
        print("\n")
        print(df.head())
        return(df)

    def get_metric_disk_write_requests(self, resource_id, granularity, start, stop):
        meters = self.gnocchi_client.metric.get_measures('disk.device.write.requests',
                                                           start=start,
                                                           stop=stop,
                                                           resource_id=resource_id,
                                                           granularity=granularity,
                                                           aggregation='rate:mean')
        
        df = pd.DataFrame(meters, columns =['timestamp', 'granularity', 'disk_write_requests'])
        print("\n")
        print(df.head())
        return(df)


    def get_metric_disk_read_bytes(self, resource_id, granularity, start, stop):
        meters = self.gnocchi_client.metric.get_measures('disk.device.read.bytes',
                                                           start=start,
                                                           stop=stop,
                                                           resource_id=resource_id,
                                                           granularity=granularity,
                                                           aggregation='rate:mean')
        
        df = pd.DataFrame(meters, columns =['timestamp', 'granularity', 'disk_read_bytes'])
        print("\n")
        print(df.head())
        return(df)

    def get_metric_disk_write_bytes(self, resource_id, granularity, start, stop):
        meters = self.gnocchi_client.metric.get_measures('disk.device.write.bytes',
                                                           start=start,
                                                           stop=stop,
                                                           resource_id=resource_id,
                                                           granularity=granularity,
                                                           aggregation='rate:mean')
        
        df = pd.DataFrame(meters, columns =['timestamp', 'granularity', 'disk_write_bytes'])
        print("\n")
        print(df.head())
        return(df)


    def get_metric_network_incoming_bytes(self, resource_id, granularity, start, stop):
        meters = self.gnocchi_client.metric.get_measures('network.incoming.bytes',
                                                           start=start,
                                                           stop=stop,
                                                           resource_id=resource_id,
                                                           granularity=granularity,
                                                           aggregation='rate:mean')
        
        df = pd.DataFrame(meters, columns =['timestamp', 'granularity', 'network_incoming_bytes'])
        print("\n")
        print(df.head())
        return(df)

    def get_metric_network_outgoing_bytes(self, resource_id, granularity, start, stop):
        meters = self.gnocchi_client.metric.get_measures('network.outgoing.bytes',
                                                           start=start,
                                                           stop=stop,
                                                           resource_id=resource_id,
                                                           granularity=granularity,
                                                           aggregation='rate:mean')
        
        df = pd.DataFrame(meters, columns =['timestamp', 'granularity', 'network_outgoing_bytes'])
        print("\n")
        print(df.head())
        return(df)


    def get_metric_network_incoming_packets(self, resource_id, granularity, start, stop):
        meters = self.gnocchi_client.metric.get_measures('network.incoming.packets',
                                                           start=start,
                                                           stop=stop,
                                                           resource_id=resource_id,
                                                           granularity=granularity,
                                                           aggregation='rate:mean')
        
        df = pd.DataFrame(meters, columns =['timestamp', 'granularity', 'network_incoming_packets'])
        print("\n")
        print(df.head())
        return(df)

    def get_metric_network_outgoing_packets(self, resource_id, granularity, start, stop):
        meters = self.gnocchi_client.metric.get_measures('network.outgoing.packets',
                                                           start=start,
                                                           stop=stop,
                                                           resource_id=resource_id,
                                                           granularity=granularity,
                                                           aggregation='rate:mean')
        
        df = pd.DataFrame(meters, columns =['timestamp', 'granularity', 'network_outgoing_packets'])
        print("\n")
        print(df.head())
        return(df)


    # OpenStack get resource for each interface
    # WARNING: Return the first interface
    def get_resource_network(self,resource_inst_id):
        list_meters = self.gnocchi_client.resource.list(resource_type='instance_network_interface')
        interfaces_id = []
        for item in list_meters:
            if str(item['original_resource_id']).find(str(resource_inst_id)) != -1:
                interfaces_id.append(item['id'])
        return interfaces_id[0]
                
    # OpenStack get resource for each disk
    # WARNING: Return the first disk
    def get_resource_disk(self,resource_inst_id):
        list_meters = self.gnocchi_client.resource.list(resource_type='instance_disk')
        disks_id = []
        for item in list_meters:
            if str(item['original_resource_id']).find(str(resource_inst_id)) != -1:
                disks_id.append(item['id'])
        return disks_id[0]
                

def main():

    auth_session = OpenStack_Auth(cloud_name='ifes_serra')
    sess = auth_session.get_session()
    gnocchi = Gnocchi(session=sess)

    nova = nclient.Client(version='2.1', session=sess)
    instance = nova.servers.get(OPENSTACK_VM_ID)
    # instance = nova.servers.find(name='vm-replaypcap')
    flavor = nova.flavors.get(instance.flavor['id'])

    # Get vcpus to calc cpu_util in %
    OPENSTACK_VM_VCPUS = flavor.vcpus
    # Get VM disk id 
    ID_DISK = gnocchi.get_resource_disk(OPENSTACK_VM_ID)
    # Get VM Network Interface ID
    ID_NET_INTERFACE = gnocchi.get_resource_network(OPENSTACK_VM_ID)
    
    # Assignment Metrics variables
    cpu = 0.0
    memory_usage = 0.0
    memory_swap_in = 0.0
    memory_swap_out = 0.0
    disk_read_requests = 0.0
    disk_write_requests = 0.0
    disk_read_bytes = 0.0
    disk_write_bytes = 0.0
    network_incoming_bytes = 0.0
    network_outgoing_bytes = 0.0
    network_incoming_packets = 0.0
    network_outgoing_packets = 0.0

    print("\n PARAMETERS:\n")
    print("{:>20}: {}".format("INSTANCE_ID", OPENSTACK_VM_ID))
    print("{:>20}: {}".format("INSTANCE_VCPUS", str(OPENSTACK_VM_VCPUS)))
    print("{:>20}: {}".format("ID_DISK", ID_DISK))
    print("{:>20}: {}".format("ID_NET_INTERFACE", ID_NET_INTERFACE))
    print("{:>20}: {}".format("GRANULARITY", str(GRANULARITY)))
    print("{:>20}: {}".format("UTC_START_TIME", str(START)))
    print("{:>20}: {}".format("UTC_STOP_TIME", str(STOP)))

    
    try:
        cpu = gnocchi.get_metric_cpu_utilization(OPENSTACK_VM_ID, GRANULARITY, OPENSTACK_VM_VCPUS, START, STOP)

        memory_usage = gnocchi.get_metric_memory_usage(OPENSTACK_VM_ID, GRANULARITY, START, STOP)
        memory_swap_in = gnocchi.get_metric_swap_in(OPENSTACK_VM_ID, GRANULARITY, START, STOP)
        memory_swap_out = gnocchi.get_metric_swap_out(OPENSTACK_VM_ID, GRANULARITY, START, STOP)

        disk_read_requests = gnocchi.get_metric_disk_read_requests(ID_DISK, GRANULARITY, START, STOP)
        disk_write_requests = gnocchi.get_metric_disk_write_requests(ID_DISK, GRANULARITY, START, STOP)
        disk_read_bytes = gnocchi.get_metric_disk_read_bytes(ID_DISK, GRANULARITY, START, STOP)
        disk_write_bytes = gnocchi.get_metric_disk_write_bytes(ID_DISK, GRANULARITY, START, STOP)

        network_incoming_bytes = gnocchi.get_metric_network_incoming_bytes(ID_NET_INTERFACE, GRANULARITY, START, STOP)
        network_outgoing_bytes = gnocchi.get_metric_network_outgoing_bytes(ID_NET_INTERFACE, GRANULARITY, START, STOP)
        network_incoming_packets = gnocchi.get_metric_network_incoming_packets(ID_NET_INTERFACE, GRANULARITY, START, STOP)
        network_outgoing_packets = gnocchi.get_metric_network_outgoing_packets(ID_NET_INTERFACE, GRANULARITY, START, STOP)
    
        print("\nDATASET INFO\n")

        # Print Shapes
        print("{:>30}: {}".format("Shape cpu", cpu.shape))
        print("{:>30}: {}".format("Shape memory_usage", memory_usage.shape))
        print("{:>30}: {}".format("Shape memory_swap_in", memory_swap_in.shape))
        print("{:>30}: {}".format("Shape memory_swap_out", memory_swap_out.shape))
        print("{:>30}: {}".format("Shape disk_read_requests", disk_read_requests.shape))
        print("{:>30}: {}".format("Shape disk_write_requests", disk_write_requests.shape))
        print("{:>30}: {}".format("Shape disk_read_bytes", disk_read_bytes.shape))
        print("{:>30}: {}".format("Shape disk_write_bytes", disk_write_bytes.shape))
        print("{:>30}: {}".format("Shape network_incoming_bytes", network_incoming_bytes.shape))
        print("{:>30}: {}".format("Shape network_outgoing_bytes", network_outgoing_bytes.shape))
        print("{:>30}: {}".format("Shape network_incoming_packets", network_incoming_packets.shape))
        print("{:>30}: {}".format("Shape network_outgoing_packets", network_outgoing_packets.shape))


        # Drop column granularity
        cpu = cpu.drop('granularity', axis=1)
        
        memory_usage = memory_usage.drop('granularity', axis=1)
        memory_swap_in = memory_swap_in.drop('granularity', axis=1)
        memory_swap_out = memory_swap_out.drop('granularity', axis=1)
        
        disk_read_requests = disk_read_requests.drop('granularity', axis=1)
        disk_write_requests = disk_write_requests.drop('granularity', axis=1)
        disk_read_bytes = disk_read_bytes.drop('granularity', axis=1)
        disk_write_bytes = disk_write_bytes.drop('granularity', axis=1)
        
        network_incoming_bytes = network_incoming_bytes.drop('granularity', axis=1)
        network_outgoing_bytes = network_outgoing_bytes.drop('granularity', axis=1)
        network_incoming_packets = network_incoming_packets.drop('granularity', axis=1)
        network_outgoing_packets = network_outgoing_packets.drop('granularity', axis=1)

        # Merge Dataset
        dataset = cpu.merge(memory_usage, how='left', on='timestamp')
        dataset = dataset.merge(memory_swap_in, how='left', on='timestamp')
        dataset = dataset.merge(memory_swap_out, how='left', on='timestamp')
        
        dataset = dataset.merge(disk_read_requests, how='left', on='timestamp')
        dataset = dataset.merge(disk_write_requests, how='left', on='timestamp')
        dataset = dataset.merge(disk_read_bytes, how='left', on='timestamp')
        dataset = dataset.merge(disk_write_bytes, how='left', on='timestamp')

        dataset = dataset.merge(network_incoming_bytes, how='left', on='timestamp')
        dataset = dataset.merge(network_outgoing_bytes, how='left', on='timestamp')
        dataset = dataset.merge(network_incoming_packets, how='left', on='timestamp')
        dataset = dataset.merge(network_outgoing_packets, how='left', on='timestamp')        
        
        dataset['label'] = LABEL
 
        print("\nDataset Shape: ", dataset.shape)
        print(dataset.head())
        
        # Rounds values to two decimal places 
        numeric_columns = dataset.select_dtypes(include='number').columns
        ## Dict with numbers columns 
        dict_round = {}
        for c in numeric_columns:
            dict_round[c] = 2       # Two decimal places
        #print(dict_round)
        ## Round values    
        dataset = dataset.round(dict_round)

        print("\Dataset with rounded values: ")
        print(dataset.head())

        # Save Dataset in CSV Format
        print("\n------------------------------------------------")
        print("Dataset file: ", DATASET_OUT_FILE)
        print("------------------------------------------------\n")
        dataset.to_csv(DATASET_OUT_FILE, index=False)

    except:
        pass

if __name__ == "__main__":
    logfile = script_name+".log"
    f = open(logfile, "w")
    f.write("------------------------------------------------------------------------------------------------\n")
    f.write("TERMINAL OUTPUT: "+script_name+"\n")
    f.write("------------------------------------------------------------------------------------------------\n\n")
    f.close()
    sys.stdout = Logger(logfile=logfile)
    main()