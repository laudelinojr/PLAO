from genericpath import getsize
from http.client import FORBIDDEN
from logging import exception
from re import search
#from winreg import REG_SZ
import gnocchiclient
from gnocchiclient.exceptions import ArchivePolicyNotFound, MetricNotFound, NamedMetricAlreadyExists, ResourceTypeAlreadyExists, ResourceTypeNotFound
import shade
import yaml
import psutil
from keystoneauth1.identity import v3
from keystoneauth1 import session
#from novaclient import client as nova_client
from gnocchiclient.v1 import client, metric, resource
#from gnocchiclient import auth
import platform
import subprocess
import threading
import time
import datetime
from datetime import datetime
import sys
import os

SERVERS_FILE="servers.yaml"
VarPlao="plao"

def collectip():

    global servers
    servers = Servers()
    print("Check iplocal exists in servers.yaml ...")

    global IPServerLocal
    
    #IPServerLocal="200.137.75.159"
    IPServerLocal="200.137.82.21"
    print (IPServerLocal)
    #IPServerLocal=servers.getSearchIPLocalServer()
    global NameServerLocal
    NameServerLocal=servers.getServerName(IPServerLocal)    
    print (NameServerLocal)


# Class to autenticate on OpenStack and return authentication session
class OpenStack_Auth():
    def __init__(self, cloud_name):
        self.cloud = shade.openstack_cloud(cloud=cloud_name)
        # Import credentials witch clouds.yaml
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

#Class to get servers
class Servers():
    def __init__(self):
        self.A=open(SERVERS_FILE, )
        self.B=yaml.full_load(self.A)
        self.C = len(self.B["servers"])

    def getbyIndexIP(self,index):
        if self.C >= index:
            return self.B["servers"][index]["ip"]   

    #Return All IP of servers
    def getAll(self):
        LISTIP_NAME={}
        for i in range(self.C):
            LISTIP_NAME.update({i:{"name":self.B["servers"][i]["name"],"ip": self.B["servers"][i]["ip"]}})
            #print (self.B["servers"][i]["name"])
            #print (self.B["servers"][i]["ip"])
        return LISTIP_NAME

    #Return All IP of servers except local IP
    def getAllnoLocal(self, IPServerLocal):
        LISTIP_NAME={}
        for i in range(self.C):
            if (self.B["servers"][i]["ip"] != IPServerLocal ):
                LISTIP_NAME.update({i:{"name":self.B["servers"][i]["name"],"ip": self.B["servers"][i]["ip"]}})
        return LISTIP_NAME

    def getAllIp(self):
        LISTIP=[]
        for i in range(self.C):
            LISTIP.append(self.B["servers"][i]["ip"])
        return LISTIP

    def getServerName(self,ip):
        for i in range(self.C):
            if (ip == self.B["servers"][i]["ip"]):
                return self.B["servers"][i]["name"]
    
    def getCheckName(self,name):
        for i in range(self.C):
            if (name == self.B["servers"][i]["name"]):
                return True

    def getServerIp(self,name):
        for i in range(self.C):
            if (name == self.B["servers"][i]["name"]):
                return self.B["servers"][i]["ip"]

    #Insert IP to check if this exists in servers.yaml
    def getCheckIp(self,ip):
        for i in range(self.C):
            if (ip == self.B["servers"][i]["ip"]):
                return True

    def getServerQtd(self):
        return self.C

    #Search server IP in servers.yaml
    def getSearchIPLocalServer(self):
        self.ipserver=""
        self.LIST_GETALLIP=[]
        self.LIST_GETALLIP=self.getAllIp()
        self.LIST_GETALLIP_LEN=(len(self.LIST_GETALLIP))
        for interface,addrs in psutil.net_if_addrs().items():
            for item in addrs:
                for i in range(self.LIST_GETALLIP_LEN):
                    if (item.address == self.B["servers"][i]["ip"]):
                        self.ipserver=self.B["servers"][i]["ip"]
        return self.ipserver

# Class to get measures from Gnocchi
class Gnocchi():
    def __init__(self, session):
        # param verify : ignore self-signed certificate
        self.gnocchi_client = client.Client(session=session)

    # check if resource_type exists
    def get_resource_type(self,name):
        try:
            return self.gnocchi_client.resource_type.get(name)
        except ResourceTypeNotFound:
            return False

    # check if resource_type exists
    def get_check_resource_type(self,name):
        try:
            self.gnocchi_client.resource_type.get(name)
            return True
        except ResourceTypeNotFound:
            return False
    
    def set_create_resource_type(self,name):
        try:
            self.resource_type = {"name": name,'attributes':{"host":{"type": "string", "min_length": 0, "max_length": 255,"required": True}}}
            self.gnocchi_client.resource_type.create(self.resource_type)
        except ResourceTypeAlreadyExists:
            return "ResourceTypeJaExiste"
    
    #Create resource
    def set_create_resource(self,resource_type,resource_name):
        try:
            self.resource=self.gnocchi_client.resource.create(resource_type,{"host":"","id":resource_name})
        except ResourceTypeNotFound:
            return "ResourceTypeNotFound"

    #check if exists resource
    def get_resource(self,name):
        try:
            resource=self.gnocchi_client.resource.search(resource_type=name,limit=1)
            print(resource)
            #return True
        except ResourceTypeNotFound:
            return False

    #return resource id
    def get_resource_id(self,name):
        try:
            self.resource=self.gnocchi_client.resource.search(resource_type=name,limit=1,details=True)
            if(len(self.resource))==0:
                return -1
            else:
                return self.resource[0]["id"]
        except ResourceTypeNotFound:
            return ""

    #Check if metris to exists and return this
    def get_metric(self,name,resource_id):
        try:
            return self.gnocchi_client.metric.get(name,resource_id)
        except MetricNotFound:
            return ""

    #Check if metris to exists and return the id
    def get_metric_id(self,name,resource_id):
        try:
            self.resp= self.gnocchi_client.metric.get(name,resource_id)
            return self.resp.get('id')
        except MetricNotFound:
            return ""

    #To create metric
    def set_create_metric(self,name,archive_policy,resource_id,unit):
        try:
            self.create_metric=self.gnocchi_client.metric._create_new(name,archive_policy,resource_id,unit)
        except NamedMetricAlreadyExists:
            return "MetricaJaExiste"

    #To create archive-policy
    def set_create_archive_policy(self,name):      
        try:
            self.create_metric=self.gnocchi_client.archive_policy.create({'name': name, 'back_window': 0, 'definition': [{'timespan': '60 days, 0:00:00', 'granularity': '0:01:00', 'points': 86400}], 'aggregation_methods': ['mean', 'sum', 'min', 'std', 'count', 'max']})
        except:
            return "NoAccess"

    #To get archive-policy and reply True  our False if archive-policy exist
    def get_archive_policy(self,name):
        try:
            archive_id=self.gnocchi_client.archive_policy.get(name)
            #print(archive_id)
            #print(len(archive_id))
            if(len(archive_id))==0:
                return False
            else:
                return True
        except ArchivePolicyNotFound:
            return "ArquivePolicyNotFound"
    
    #To clean measures of all metrics
    #def set_clean_all_measures_metrics

    #To delete all metrics in plao
    #def set_delete_all_metrics

    #add measures in metrics
    def set_add_measures_metric(self,id,value):
        self.timestamp = str(datetime.now()).split('.')[0]
        self.addmeasures=self.gnocchi_client.metric.add_measures(id, [{'timestamp': self.timestamp,'value': value}])

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

    #If dont data, return -1, else return data
    def get_last_measure(self, name_metric, resource_id, aggregation, granularity, start, stop):
        dados=self.gnocchi_client.metric.get_measures(name_metric,start,stop, aggregation, granularity,resource_id)
        if len(dados) != 0:     
            return dados[0][2]
        return -1
        #df = pd.DataFrame(dados, columns =['timestamp', 'granularity', ''])
        #print("\n")
        #print(df.head())
        #return (df)

    #If dont data, return -1, else return data
    def get_measure(self, name_metric, resource_id, aggregation, granularity, start, stop):
        dados=self.gnocchi_client.metric.get_measures(name_metric,start,stop, aggregation, granularity,resource_id)
        if len(dados) != 0:     
            return dados[0][2]
        return -1
        #df = pd.DataFrame(dados, columns =['timestamp', 'granularity', ''])
        #print("\n")
        #print(df.head())
        #return (df)



def main():

    collectip()
    #startApp()

    print("Starting PLAO client...")
    print("Reading servers.yaml ...")

    
#    servers = Servers()

#    print("Check iplocal exists in servers.yaml ...")

#    global IPServerLocal
#    IPServerLocal=servers.getSearchIPLocalServer()
#    NameServerLocal=servers.getServerName(IPServerLocal)
    #IPServerLocal="192.168.56.1"
    if (IPServerLocal == ""):
        print("Did not match IP local and server.yaml...Exiting...")
        sys.exit()
    print("IP Server Local ok, is: "+IPServerLocal)
    print("Reading otheres IP to ping and iperf...")

    #IpOthersServers=servers.getAllnoLocal(IPServerLocal)  
    #for i in IpOthersServers:
    #        print("IP Other server is: "+str(IpOthersServers.get(i)))

    print("Creating session in Openstack...")
    #Creating session OpenStack
    #auth_session = OpenStack_Auth(cloud_name=VarCloudName)
    print(NameServerLocal)
    #auth_session = OpenStack_Auth(cloud_name=NameServerLocal)
    auth_session = OpenStack_Auth(cloud_name="openstack-controller")
    
    
    sess = auth_session.get_session()

    print("Creating object and using session in Gnocchi...")
    #Insert Session in Gnocchi object
    gnocchi = Gnocchi(session=sess)


    print ("vai")    
    print(gnocchi.get_archive_policy("plao"))

    print ("vai2")
    gnocchi.get_resource("plao")


if __name__ == "__main__":
    main()