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
#import pandas as pd
#from PLAO_client2_w_routes import appc
from flask import Flask, request
STARTED = 0

#VarCloudName='mpes_n1'  #Alterar codigo e colocar como argu
#SERVERS_FILE="/opt/PLAO/servers.yaml"
SERVERS_FILE="servers.yaml"
VarPlao="plao"
debug_file = 0

def collectip():

    global servers
    servers = Servers()
    print("Check iplocal exists in servers.yaml ...")

    global IPServerLocal
    IPServerLocal=servers.getSearchIPLocalServer()
    global NameServerLocal
    NameServerLocal=servers.getServerName(IPServerLocal)    


def startApp():
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

    IpOthersServers=servers.getAllnoLocal(IPServerLocal)  
    for i in IpOthersServers:
            print("IP Other server is: "+str(IpOthersServers.get(i)))

    print("Creating session in Openstack...")
    #Creating session OpenStack
    #auth_session = OpenStack_Auth(cloud_name=VarCloudName)
    auth_session = OpenStack_Auth(cloud_name=NameServerLocal)
    sess = auth_session.get_session()

    print("Creating object and using session in Gnocchi...")
    #Insert Session in Gnocchi object
    gnocchi = Gnocchi(session=sess)

    print("Checking if archive_policy plao exists.")
    if (gnocchi.get_archive_policy(VarPlao) == "ArquivePolicyNotFound" or gnocchi.get_archive_policy(VarPlao)  == False):
        gnocchi.set_create_archive_policy(VarPlao)
    else:
        print("ArchivePolicy plao exists")

    #Checking when starting Agent
    print("Checking if resource_type plao exists...")
    if(gnocchi.get_resource_type(VarPlao)==False):
        print("Resource Type plao do not exist, creating...")
        gnocchi.set_create_resource_type(VarPlao)
        print ("command created resource type")
    else:
        print("Resource Type plao exists.")

    print("Checking if resource plao exists...")
    if(gnocchi.get_resource(VarPlao)==False):
        print("Resource plao do not exist, creating...")
        #executar metodo para criar novo recurso
        gnocchi.set_create_resource(VarPlao,VarPlao+":"+IPServerLocal)
        print("command created resourse")
    else:
        print("Resource plao exists.")

    print("Collecting id of resource plao...")
    resource_id=gnocchi.get_resource_id(VarPlao)
    #print (resource_id)
    if (resource_id == "" or resource_id == -1):
        print("Do not have resource id PLAO, we need to create.")
        #executar metodo para criar novo recurso
        gnocchi.set_create_resource(VarPlao,VarPlao+":"+IPServerLocal)
        print ("command to create resousre id")

    print("Checking if metric Latency exists...")      
    Metric_Lat_test=""
    for i in IpOthersServers:
        Name_Metric_Lat="Lat_To_"+str(IpOthersServers.get(i).get('external_ip'))
        Metric_Lat_test=gnocchi.get_metric_id(Name_Metric_Lat,resource_id)
        if (Metric_Lat_test == ""):
            print("The "+ Name_Metric_Lat + " do not exist. Creating metric Latency.")
            if (gnocchi.set_create_metric(Name_Metric_Lat,VarPlao,resource_id,"ms") == "MetricaJaExiste" ):
                print ("Metric already exists.")            
            else:
                print("Created Metrics.")

    print("Checking if metric Jitter exists...")      
    Metric_Jit_test=""
    for i in IpOthersServers:
        Name_Metric_Jit="Jit_To_"+str(IpOthersServers.get(i).get('ip'))
        Metric_Jit_test=gnocchi.get_metric_id(Name_Metric_Jit,resource_id)
        if (Metric_Jit_test == ""):
            print("The "+ Name_Metric_Jit + " do not exist. Creating metric Jitter.")
            if (gnocchi.set_create_metric(Name_Metric_Jit,VarPlao,resource_id,"ms") == "MetricaJaExiste" ):
                print ("Metric already exists.")            
            else:
                print("Created Metrics.")

    print("Creating Latency Threads to all servers...")
    for i in IpOthersServers:
        #to create thread for Latency
        Thread_Lat = CreateThread()
        Thread_Lat.ThreadPing(IpOthersServers.get(i).get('external_ip'),"5","1",resource_id,gnocchi)

    print("Creating Jiitter Threads to all servers...")
    for i in IpOthersServers:
        #to create thread for Latency
        Thread_Jitt = CreateThread()
        Thread_Jitt.ThreadIperf(IpOthersServers.get(i).get('external_ip'),"5","1",resource_id,gnocchi)
    #Mark variable with number 1 for started status on
    global STARTED
    STARTED=1

# To execute commands in Linux
def ExecuteCommand(exec_command):
 try:
  ret = subprocess.run(exec_command, universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
  if debug_file == 1:
   print("DEBUG ON")
   print("CMD - " + exec_command)
   print("RETURN - \n" + ret.stdout)
   print (ret.stdout)
   print (+ret.returncode)
   return ret.returncode
 except:
  print('FAIL IN COMMAND EXECUTE')
  print("CMD - " + exec_command)
  print("ERROR - " + ret)
  return ret.returncode

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
            print ("set_create_resource")
            self.resource=self.gnocchi_client.resource.create(resource_type,{"host":"","id":resource_name})
        except Exception as e:
        #except ResourceTypeNotFound:
            print (e)
            return "ResourceTypeNotFound"

    #check if exists resource
    def get_resource(self,name):
        try:
            resource=self.gnocchi_client.resource.search(resource_type=name,limit=1)
            print (resource)
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
            print ("consultando metrica usando resource_id")
            print (resource_id)
            print(name)
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
                LISTIP_NAME.update({i:{"name":self.B["servers"][i]["name"],"ip": self.B["servers"][i]["ip"],"external_ip": self.B["servers"][i]["external_ip"]}})
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

#Class to Cloud
class Cloud():
    def __init__(self,ip):
        self.Ip=ip
        self.Name=""
        self.Cpu=""
        self.CPUStatus=0
        self.VimURL=""
        
    def setName(self,name):
        self.Name=name

    def getName(self):
        return self.Name

    def setVimURL(self,vimURL):
        self.VimURL=vimURL

    def getVimURL(self):
        return self.VimURL

    def getCpu(self):
        return self.Cpu

    def setCpu(self,cpu):
        #print("configurando cpu: "+cpu)
        self.Cpu=cpu

    def getCpuStatus(self):
        return self.CPUStatus

    #Configure status 0 if ok, or 1 if disaggregated
    def setCpuStatus(self,cpuStatus):
        self.CPUStatus=cpuStatus

    def getIp(self):
        return self.Ip

#Ping to others servers in servers.yaml
class Latency():
    def __init__(self):
        pass

    #Test with ping to get latency.
    def execLatency(self,TARGET,QUANTITY_PCK,LOOP,RESOURCE_ID,GNOCCHI):
        Metric_Name="Lat_To_"+TARGET
        Metric_ID=GNOCCHI.get_metric_id(Metric_Name,RESOURCE_ID)

        if (LOOP == "0"):
            if platform.system().lower() == "linux":
                try:
                    self.ping = subprocess.check_output(["ping", "-c", QUANTITY_PCK, TARGET])
                except:
                    return "" #if return with error, return empty
                self.latency = self.ping.split()[-2]
                self.resp = str(self.latency, 'utf-8')
                self.resp2= self.resp.split("/")[2]
                print("ping: "+TARGET+" "+self.resp2)
                GNOCCHI.set_add_measures_metric(Metric_ID,self.resp2)
                return self.resp2
            else: # platform.system().lower() == "windows":
                try:
                    self.ping = subprocess.check_output(["ping", "-n", QUANTITY_PCK, TARGET])
                except:
                    return "" #if return with error, return empty
                self.latency = self.ping.split()[-1]
                self.resp = str(self.latency, 'utf-8')
                self.resp2= self.resp.split("=")[0]
                self.resp3=self.resp2.split("ms")[0]
                print ("ping: "+TARGET+" "+self.resp3)
                GNOCCHI.set_add_measures_metric(Metric_ID,self.resp3)
                return self.resp3
        else:
            while True:
                time.sleep(1)
                if platform.system().lower() == "linux":
                    try:
                        self.ping = subprocess.check_output(["ping", "-c", QUANTITY_PCK, TARGET])
                    except:
                        return "" #if return with error, return empty
                    self.latency = self.ping.split()[-2]
                    self.resp = str(self.latency, 'utf-8')
                    self.resp2= self.resp.split("/")[2]
                    GNOCCHI.set_add_measures_metric(Metric_ID,self.resp2)
                    print("ping: "+TARGET+" "+self.resp2)
                else: # platform.system().lower() == "windows":
                    try:
                        self.ping = subprocess.check_output(["ping", "-n", QUANTITY_PCK, TARGET])
                    except:
                        return "" #if return with error, return empty
                    self.latency = self.ping.split()[-1]
                    self.resp = str(self.latency, 'utf-8')
                    self.resp2= self.resp.split("=")[0]
                    self.resp3=self.resp2.split("ms")[0]
                    GNOCCHI.set_add_measures_metric(Metric_ID,self.resp3)
                    print ("ping: "+TARGET+" "+self.resp3)

#Jitter to others servers in servers.yaml
class Jitter():
    def __init__(self):
        pass

    def execJitter(self,TARGET,QUANTITY_PCK,LOOP,RESOURCE_ID,GNOCCHI):
        Metric_Name="Jit_To_"+TARGET
        Metric_ID=GNOCCHI.get_metric_id(Metric_Name,RESOURCE_ID)

        if (LOOP == "0"):
            if platform.system().lower() == "linux":
                if (ExecuteCommand("ps ax | grep 'iperf3 -s -D'  | grep -v grep | wc -l")==0):
                    print("executing iperf Daemon loop 0")          
                    subprocess.check_output(["iperf3", "-s", "-D"])
                try:
                    self.iperf2 = subprocess.check_output(["iperf3", "-c", TARGET,"-u", "-t", QUANTITY_PCK])
                except:
                    return -1
                self.jitter = self.iperf2.split()[-7]
                self.resp = str(self.jitter, 'utf-8')
                GNOCCHI.set_add_measures_metric(Metric_ID,self.resp)
                print("jitter: "+TARGET+" "+self.resp)
                return self.resp
            else:
                try:
                    self.iperf2 = subprocess.check_output(["utils/iperf/iperf3", "-c", TARGET,"-u", "-t", QUANTITY_PCK])
                except:
                    return -1
                #print (self.iperf2)
                self.jitter = self.iperf2.split()[-11]
                self.resp = str(self.jitter, 'utf-8')
                GNOCCHI.set_add_measures_metric(Metric_ID,self.resp)
                print("jitter: "+TARGET+" "+self.resp)
                return self.resp
        else:
            while True:
                time.sleep(1)
                if platform.system().lower() == "linux":
                    if (ExecuteCommand("ps ax | grep 'iperf3 -s -D'  | grep -v grep | wc -l")==0):
                        print("executing iperf Daemon loop 1")            
                        subprocess.check_output(["iperf3", "-s", "-D"])
                    try:
                        print("executing iperf to: "+TARGET)
                        self.iperf2 = subprocess.check_output(["iperf3", "-c", TARGET,"-u", "-t", QUANTITY_PCK])
                    except:
                        print ("Error in iperf client")
                        return -1
                    self.jitter = self.iperf2.split()[-7]
                    self.resp = str(self.jitter, 'utf-8')
                    GNOCCHI.set_add_measures_metric(Metric_ID,self.resp)
                    print("jitter: "+TARGET+" "+self.resp)
                else:
                    try:
                        self.iperf2 = subprocess.check_output(["utils/iperf/iperf3", "-c", TARGET,"-u", "-t", QUANTITY_PCK])
                    except:
                        return -1
                    #print (self.iperf2)
                    self.jitter = self.iperf2.split()[-11]
                    self.resp = str(self.jitter, 'utf-8')
                    GNOCCHI.set_add_measures_metric(Metric_ID,self.resp)
                    print("jitter: "+TARGET+" "+self.resp)

# To create Thread
class CreateThread():
    def __init__(self):
        pass

    def ThreadPing(self,TARGET,QUANTITY_PCK,LOOP,RESOURCE_ID,GNOCCHI):
        print("funcaoThreadPing")
        self.ExecPing = Latency()
        self.thread_ping = threading.Thread(target=self.ExecPing.execLatency,args=(TARGET,QUANTITY_PCK,LOOP,RESOURCE_ID,GNOCCHI))
        self.thread_ping.start()

    def ThreadIperf(self,TARGET,QUANTITY_PCK,LOOP,RESOURCE_ID,GNOCCHI):
        print ("funcaoThreadIperf")
        self.ExecJitter = Jitter()
        self.thread_iperf = threading.Thread(target=self.ExecJitter.execJitter,args=(TARGET,QUANTITY_PCK,LOOP,RESOURCE_ID,GNOCCHI))
        self.thread_iperf.start()

        

def main():
    collectip()
    appc = Flask(__name__)

    @appc.route('/check/',methods=['GET'])
    def check():
        #If startApp() started, return 1, or 0 for not 
        return str(STARTED)
    #Start the PLAO Agent in Openstack Server and start ping to other cloud
    @appc.route('/start/',methods=['POST'])
    def start():
        if (STARTED == 0):    
            novo = startApp()
            return "System_Started"
        return "System_Already_Started"
    #Command to start ping from cloud to user
    @appc.route("/userlatency/", methods=['POST', 'GET', 'DELETE'])
    def latencia_user_plao_client():
        if request.method == "POST":
            print("entrei aqui")
            request_data = request.get_json()
            ip_user = request_data['ipuser']
            print (ip_user)
            VarPlao="plao"
            servers = Servers()
            IPServerLocal=servers.getSearchIPLocalServer()
            print ("ipserver: "+IPServerLocal)
            NameServerLocal=servers.getServerName(IPServerLocal)
            print ("nameserver: "+NameServerLocal)
            auth_session = OpenStack_Auth(cloud_name=NameServerLocal)
            sess = auth_session.get_session()
            gnocchi = Gnocchi(session=sess)
            resource_id=gnocchi.get_resource_id(VarPlao)
            print ("idRrecurso: "+resource_id)
            print("Checking if metric Latency exists...")      
            Metric_Lat_test=""
            Name_Metric_Lat="Lat_To_"+str(ip_user)
            print(Name_Metric_Lat)
            Metric_Lat_test=gnocchi.get_metric_id(Name_Metric_Lat,resource_id)
            if (Metric_Lat_test == ""):
                print("depois if metric lat test")
                print("The "+ Name_Metric_Lat + " do not exist. Creating metric Latency.")
                if (gnocchi.set_create_metric(Name_Metric_Lat,VarPlao,resource_id,"ms") == "MetricaJaExiste" ):
                    print ("Metric already exists.")            
                else:
                    print("Created Metrics.")
            print("Iniciar Thread para coletar latencia ate usuario e guardar no gnocchi.")
            Thread_Lat = CreateThread()
            #Future: to parameterize number packets and loop false(0) or true(1), and maybe to create other parameter for to configure number of attemps
            Thread_Lat.ThreadPing(ip_user,"5","0",resource_id,gnocchi)
            return "Executed"

    appc.run(IPServerLocal, '3333',debug=True)
    

if __name__ == "__main__":
    main()