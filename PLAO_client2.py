from genericpath import getsize
from re import search
from winreg import REG_SZ
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

VarCloudName='mpes_n1'
SERVERS_FILE="servers.yaml"

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
            self.resource=self.gnocchi_client.resource.create(resource_type,{"host":"","id":resource_name})
        except ResourceTypeNotFound:
            return "ResourceTypeNotFound"

    #check if exists resource
    def get_resource(self,name):
        try:
            resource=self.gnocchi_client.resource.search(resource_type=name,limit=1)
            return True
        except ResourceTypeNotFound:
            return False

    #return resource id
    def get_resource_id(self,name):
        try:
            self.resource=self.gnocchi_client.resource.search(resource_type=name,limit=1,details=True)
            #print (self.resource)
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
        self.create_metric=self.gnocchi_client.archive_policy.create({'name': name, 'back_window': 0, 'definition': [{'timespan': '60 days, 0:00:00', 'granularity': '0:01:00', 'points': 86400}], 'aggregation_methods': ['mean', 'sum', 'min', 'std', 'count', 'max']})

    #To get archive-policy
    def get_archive_policy(self,name):
        try:
            self.gnocchi_client.archive_policy.get(name)
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


#Class to get servers
class Servers():
    def __init__(self):
        self.A=open(SERVERS_FILE, )
        self.B=yaml.full_load(self.A)
        self.C = len(self.B["servers"])

    def getAll(self):
        for i in range(self.C):
            print (self.B["servers"][i]["name"])
            print (self.B["servers"][i]["ip"])

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
    def getSearchServer(self):
        self.LIST_GETALLIP=[]
        self.LIST_GETALLIP=self.getAllIp()
        self.LIST_GETALLIP_LEN=(len(self.LIST_GETALLIP))
        for interface,addrs in psutil.net_if_addrs().items():
            for item in addrs:
                for i in range(self.LIST_GETALLIP_LEN):
                    if (item.address == self.B["servers"][i]["ip"]):
                        return self.B["servers"][i]["ip"]

#Ping to others servers in servers.yaml
class Latency():
    def __init__(self):
        pass

    #Test with ping to get latency.
    def execLatency(self,TARGET,QUANTITY_PCK,LOOP):
        if (LOOP == "0"):
            if platform.system().lower() == "linux":
                try:
                    self.ping = subprocess.check_output(["ping", "-c", QUANTITY_PCK, TARGET])
                except:
                    return "" #if return with error, return empty
                self.latency = self.ping.split()[-2]
                self.resp = str(self.latency, 'utf-8')
                self.resp2= self.resp.split("/")[2]
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
                print (self.resp3)
                #return self.resp3
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
                    print (self.resp3)
                    #return self.resp3

#Jitter to others servers in servers.yaml
class Jitter():
    def __init__(self):
        pass

    def execJitter(self,TARGET,QUANTITY_PCK,LOOP):
        if (LOOP == "0"):
            if platform.system().lower() == "linux":
                #if STATUS == "CLIENT":
                #iperf = subprocess.run(["iperf3", "-s", "-1", "-D"])
                try:
                    self.iperf2 = subprocess.check_output(["iperf3", "-c", TARGET,"-u", "-t", QUANTITY_PCK])
                except:
                    return -1
                self.jitter = self.iperf2.split()[-7]
                self.resp = str(self.jitter, 'utf-8')
                print(self.resp)
                #return self.resp
            else:
                #if STATUS == "CLIENT":
                #iperf = subprocess.run(["iperf3", "-s", "-1", "-D"])
                try:
                    self.iperf2 = subprocess.check_output(["utils/iperf/iperf3", "-c", TARGET,"-u", "-t", QUANTITY_PCK])
                except:
                    return -1
                #print (self.iperf2)
                self.jitter = self.iperf2.split()[-11]
                self.resp = str(self.jitter, 'utf-8')
                print(self.resp)
                #return self.resp
        else:
            while True:
                time.sleep(1)
                if platform.system().lower() == "linux":
                    #if STATUS == "CLIENT":
                    #iperf = subprocess.run(["iperf3", "-s", "-1", "-D"])
                    try:
                        self.iperf2 = subprocess.check_output(["iperf3", "-c", TARGET,"-u", "-t", QUANTITY_PCK])
                    except:
                        return -1
                    self.jitter = self.iperf2.split()[-7]
                    self.resp = str(self.jitter, 'utf-8')
                    print(self.resp)
                    #return self.resp
                else:
                    #if STATUS == "CLIENT":
                    #iperf = subprocess.run(["iperf3", "-s", "-1", "-D"])
                    try:
                        self.iperf2 = subprocess.check_output(["utils/iperf/iperf3", "-c", TARGET,"-u", "-t", QUANTITY_PCK])
                    except:
                        return -1
                    #print (self.iperf2)
                    self.jitter = self.iperf2.split()[-11]
                    self.resp = str(self.jitter, 'utf-8')
                    print(self.resp)
                    #return self.resp

# To create Thread
class CreateThread():
    def __init__(self):
        pass

    def ThreadPing(self,TARGET,QUANTITY_PCK,LOOP):
        self.ExecPing = Latency()
        self.thread_ping = threading.Thread(target=self.ExecPing.execLatency,args=(TARGET,QUANTITY_PCK,LOOP))
        self.thread_ping.start()

    def ThreadIperf(self,TARGET,QUANTITY_PCK,LOOP):
        self.ExecJitter = Jitter()
        self.thread_iperf = threading.Thread(target=self.ExecJitter.execJitter,args=(TARGET,QUANTITY_PCK,LOOP))
        self.thread_iperf.start()

def main():

    #servers = Servers()
    #servers.getAll()
    #print(servers.getServerQtd())
    #print(servers.getServerName("10.159.205.6"))
    #print(servers.getSearchIpServer())

    #Creating session OpenStack
    auth_session = OpenStack_Auth(cloud_name=VarCloudName)
    sess = auth_session.get_session()

    #Insert Session in Gnocchi object
    gnocchi = Gnocchi(session=sess)

    #Checking when starting Agent
    if(gnocchi.get_resource_type("plao")==False):
        print("Resource Type plao not exist, creating...")
        gnocchi.set_create_resource_type("plao")
        #executar metodo para criar novo recurso
    if(gnocchi.get_resource("plao")==False):
        print("Resource plao not exist, creating...")
        #executar metodo para criar novo recurso
        hostname="hirakata.mpes.gov.br3"
        gnocchi.set_create_resource("plao","plao:"+hostname)

    if (gnocchi.get_archive_policy("plao2") == "ArquivePolicyNotFound"):
        gnocchi.set_create_archive_policy("plao2")

    #type_resource_name="plao"
    #resource_name="plao2"
    #resource_id=gnocchi.get_resource_id(resource_name)
    #if (resource_id == ""):
    #    print("nao tem resource, precisamos criar um resource")
    #    gnocchi.set_resource(type_resource_name,resource_name)
    
    #metric_test=gnocchi.get_metric_id("LatToServ1",resource_id)
    #if (metric_test == ""):
    #    print("nada de metrica, precisamos criar uma metrica")
    #value=36
    #gnocchi.set_add_measures_metric(metric_test,value)

    #if( gnocchi.set_create_metric("LatToServ4","low",gnocchi.get_resource_id("plao"),"ms") == "MetricaJaExiste" ):
    #    print ("Metrica ja existe")
    #O nome da metrica colocar LatTo_xxx_xxx_xxx_xxx que sera o ip do server de destino ou JitTo_xxx_xxx_xxx_xxx

####ADICIONAR MAIS TARDE
    #to create thread
    #Thread1 = CreateThread()
    #Thread1.ThreadPing("127.0.0.1","5","0")

    #to create thread
    #Thread2 = CreateThread()
    #Thread2.ThreadIperf("127.0.0.1","5","0")


#Ler quantos e quais servidores no arquivo de configuraçao

#Iniciar Threads para ping do(s) servidor(es) no arquivo
#Obs deixar preparado para iniciar tb para latencia para o usuario, neste caso ler de outro arquivo chamado latencia_user.
#neste devera ser criado a metrica para o ip correspondente, feito ping uma vez (ou varias, a avaliar) e guardado na metrica 

#Iniciar Threads para iperf do(s) servidor(es) no arquivo

    



if __name__ == "__main__":
    main()