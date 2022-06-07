from distutils.util import execute
from http.client import HTTPConnection
from multiprocessing.connection import Connection
from operator import eq
from uuid import NAMESPACE_X500, uuid4
import uuid
from psutil import users
import yaml
import threading
import subprocess
from datetime import date,timedelta
from PLAO2_test_to_PLAOServer import CLOUD_COD
from PLAO_client2 import *
#from PLAO2_w_routes import app
from flask import Flask, request
import requests
from database.models import *
import time


#Teste para servidor requisicoes
#from PLAO2_w_routes import app

#FILE_VNF_PRICE="/opt/PLAO/osm/vnf_price_list.yaml"
#FILE_PIL_PRICE="/opt/PLAO/osm/pil_price_list.yaml"
FILE_VNF_PRICE="teste/vnf_price_list.yaml"
FILE_PIL_PRICE="teste/pil_price_list.yaml"
THRESHOLD=90 #THRESHOLD of CPU to apply rate in Cloud's price
PATH_LOG='log/'
#PATH_LOG='/opt/PLAO/log/'
PATH='/opt/PLAO/'
#Debug mode is 1
debug=0
debug_file = 0 #keep 0
#requisites for change all price of specif VIM (Cloud)
DOWN_UP_PRICE=10 #Number to add vnf Price

#classe arquivo vnfd

#Classe monitorar arquivo entrada_comandos_legado

#classe enviar ip para controladores clientes

class File_VNF_Price():
    def __init__(self):
        self.A=open(FILE_VNF_PRICE, )
        self.B=yaml.full_load(self.A)
        self.C = len(self.B)
        self.D = len(self.B[0]['prices'])

    #Search VNFD in configuration file vnf_price_list and return position in file
    #If no result, return -1 
    def SearchVNFD(self, NAME_VNFD):
        #C = len(self.B) #Elements
        for i in range(self.C):
            if self.B[i]['vnfd'] == NAME_VNFD: #Search and compare the VNFD name
                return i
        else:
            return -1

    #First, use the SearchVNFD function, after, this.
    #Change price of specific VIMNAME using the index (position) OF VNFD in vnf_price_list.
    #Change only in MEMORY. If no result, return -1  
    # In this, the target is to change the price cloud for specif Cloud (VIM)
    # If the CPU High - degraded (1), we add the extra THRESHOLD value in Price.
    def ChangeVNFPrice(self,COD_VNFD,VIMURL,PRICE,CLOUD_STATUS_CPU):
        C = len(self.B[COD_VNFD]['prices']) #Elements
        print(C)

        if COD_VNFD < 0:
            return -1   
        for i in range(C):
            if self.B[COD_VNFD]['prices'][i]['vim_url'] == VIMURL: #Compare VIMURL between YAML and the new
                if self.B[COD_VNFD]['prices'][i]['price'] != PRICE:  #Compare new PRICE with actual Price, if equal, no change
                    if (CLOUD_STATUS_CPU == 1):
                        print(self.B[COD_VNFD]['prices'][i]['price'])
                        self.B[COD_VNFD]['prices'][i]['price']=int(PRICE)+THRESHOLD #Change the VNF Price
                        print(self.B[COD_VNFD]['prices'][i]['price'])
                    else:
                        self.B[COD_VNFD]['prices'][i]['price']=int(PRICE) #Change the VNF Price
                    return i
                else:
                    return -1
        else:
            return -1

    #Change VNF File with new Price, change the file
    def SearchChangeVNFDPrice(self,NAME_VNFD,VIM_URL,PRICE_VNFD,CLOUD_STATUS_CPU):
        if debug == 1: print("In SearchChangeVNFDPrice")
        if (self.ChangeVNFPrice(self.SearchVNFD(NAME_VNFD),VIM_URL,PRICE_VNFD,CLOUD_STATUS_CPU)) != -1: #Change price of specific VIM in specific VNFD
            if debug == 1: print("In ChangeVNFPrice(SearchVNFD")
            with open(FILE_VNF_PRICE, 'w') as file:
                documents = yaml.dump(self.B, file, sort_keys=False) #Export changes to file without order, equal original file
            if debug == 1: print("going to copy to SearchChangeVNFDPrice ")
            print("lembrar descomentar linha para docker fazer copia vnf")
            #####ExecuteCommand('docker cp '+FILE_VNF_PRICE+' '+'$(docker ps -qf name=osm_pla):/placement/')  

            try:
                nomearquivo4=PATH_LOG+'CONFIG_OSM_history.txt' #write data in file
                with open(nomearquivo4, 'a') as arquivo:
                    arquivo.write(DATEHOURS() + '#CHANGE_VNFD#  - Changed and copied file '+ FILE_VNF_PRICE + 'to container PLA.'+'NAME_VNFD: '+NAME_VNFD+' VIM_URL: '+VIM_URL+' PRICE_VNFD: '+str(PRICE_VNFD) +'\n')

            except:
                return -1     
            if debug ==1: print("DEBUG: File changed")
            if debug ==1: print("DEBUG: Copy file to container pla...")
        else:
            if debug ==1: print ("DEBUG: File not changed")

    #Receive the CPU STATUS NOW and update in list cloud, the CLOUD_STATUS_CPU
    def SearchDownUpVimPrice(self,STATUS_CPU_NOW,Cloud):    #VIM_URL,CLOUD_COD,STATUS_CPU_NOW):
        VIM_URL=Cloud.getVimURL() # Get vim url for use in next operations
        CLOUD_STATUS_CPU=Cloud.getCpuStatus() #int(clouds.get(str(CLOUD_COD)).get('CPU')) #Values: 0-cpu normal, 1-cpu high and cost value changed
        PRICE=0 #Inicialize local variable
        CHANGED_PRICE_VIM_URL=0 #count auxiliar variable for count the total changes

        for i in range(self.C): #Search and change all the all vim url price for specific cloud
            for f in range(self.D):
                if self.B[i]['prices'][f]['vim_url'] == VIM_URL: #Compare VIMURL between YAML and the new
                        PRICE=self.B[i]['prices'][f]['price']  #Select the price of this vim_url
                        print(VIM_URL)
                        print(PRICE)
                        if PRICE >= 0:
                            #If the cloud CPU now is high (1), but in dict is normal (0), we need change dict to(1);
                            if STATUS_CPU_NOW == 1 and CLOUD_STATUS_CPU == 0: 
                                Cloud.setCpuStatus(1)
                                self.B[i]['prices'][f]['price']=PRICE+DOWN_UP_PRICE #Change the VNF Price with the rate price
                                CHANGED_PRICE_VIM_URL=CHANGED_PRICE_VIM_URL+1 #count auxiliar variable
                                print (self.B[i]['prices'][f]['price'])

                            #If the cloud CPU now is ok (0), but in dict is high (1), we need change dict to (0)
                            if STATUS_CPU_NOW == 0 and CLOUD_STATUS_CPU == 1 and PRICE >= DOWN_UP_PRICE: 
                                Cloud.setCpuStatus(0)
                                self.B[i]['prices'][f]['price']=int(PRICE-DOWN_UP_PRICE) #Change the VNF Price with the rate price
                                CHANGED_PRICE_VIM_URL=CHANGED_PRICE_VIM_URL+1 #count auxiliar variable
                                print(self.B[i]['prices'][f]['price'])

                            #If the cloud CPU now is ok (0), but in dict is high (1), we need change dict to (0)
                            if STATUS_CPU_NOW == 0 and CLOUD_STATUS_CPU == 1 and PRICE <= DOWN_UP_PRICE: 
                                Cloud.setCpuStatus(0)
                                self.B[i]['prices'][f]['price']=0 #Change the VNF Price with the rate price
                                CHANGED_PRICE_VIM_URL=CHANGED_PRICE_VIM_URL+1 #count auxiliar variable
                                print(self.B[i]['prices'][f]['price'])
                        else:
                            print("Trying update nvf_price file. There are price<=0. Check this.")

        if debug ==1: print ("DEBUG: Changed "+str(CHANGED_PRICE_VIM_URL)+" PRICES VIM_URL (CLOUDS).") #Print count auxiliar variable
        if CHANGED_PRICE_VIM_URL > 0:
            with open(FILE_VNF_PRICE, 'w') as file:
                documents = yaml.dump(self.B, file, sort_keys=False) #Export changes to file without order, equal original file
            print ("CPU CHANGE: File pil_price changed because High CPU.")

            nomearquivo5=PATH_LOG+'CPU_TRIGGER_'+ Cloud.getName() +'_history.txt' #write data in file
            with open(nomearquivo5, 'a') as arquivo:
                arquivo.write(DATEHOURS() + ','+ Cloud.getName() + ","+ Cloud.getIP() +","+ str(STATUS_CPU_NOW)+'\n')
            print("lembrar de descomentar")
            #ExecuteCommand('docker cp '+FILE_VNF_PRICE+' '+'$(docker ps -qf name=osm_pla):/placement/')
            try:
                nomearquivo6=PATH_LOG+'CONFIG_OSM_history.txt' #write data in file
                with open(nomearquivo6, 'a') as arquivo:
                    arquivo.write(DATEHOURS() + '#CHANGE_VNFD_ALL# Changed and copied file '+ FILE_VNF_PRICE + ' to container PLA. Add values in All prices to Cloud: '+VIM_URL+ '.' +'\n')
            except:
                return -1

class File_PIL_Price():
    def __init__(self):
        self.A=open(FILE_PIL_PRICE, )
        self.B=yaml.full_load(self.A)
        self.C = len(self.B['pil'])
        #self.D = len(self.B[0]['prices'])

    #Search in file the cloud math between from and to, in this order. If located, stop the search
    def SearchChangePILPrice(self, OPENSTACK_FROM,OPENSTACK_TO):
        for i in range(self.C):
            if self.B['pil'][i]['pil_endpoints'][0] == OPENSTACK_FROM:# or B['pil'][i]['pil_endpoints'][0] == OPENSTACK_TO:
                if self.B['pil'][i]['pil_endpoints'][1] == OPENSTACK_TO:# or B['pil'][i]['pil_endpoints'][1] == OPENSTACK_FROM:
                    return i
        return -1

    #Search cloud combination and change the price, latency and jitter
    def SearchChangePriceLatencyJitterPIL(self, PRICE,LATENCY,JITTER,OPENSTACK_FROM,OPENSTACK_TO):
        CLOUD_COD=self.SearchChangePILPrice(OPENSTACK_FROM,OPENSTACK_TO)
        #if debug == 1: print("CLOUD_COD: "+str(CLOUD_COD))
        if CLOUD_COD != -1:
            if (self.ChangePriceLatencyJitterPIL(CLOUD_COD,PRICE,LATENCY,JITTER)) != -1: #Change Price Latency and Jitter
                with open(FILE_PIL_PRICE, 'w') as file:
                    documents = yaml.dump(self.B, file, sort_keys=False) #Export changes to file without order, equal original file

                print("lembrar descomentar linha para docker fazer copia pil")
                ############ExecuteCommand('docker cp '+FILE_PIL_PRICE+' '+'$(docker ps -qf name=osm_pla):/placement/')
                try:
                    nomearquivo8=PATH_LOG+'CONFIG_OSM_history.txt' #write data in file
                    with open(nomearquivo8, 'a') as arquivo:
                        arquivo.write( DATEHOURS() + '#CHANGE_PIL# Changed and copied file '+FILE_PIL_PRICE + ' to container PLA. ' +' PRICE: '+str(PRICE)+' LATENCY: '+str(LATENCY)+' JITTER: '+str(JITTER)+'\n')
                except:
                    return -1
                if debug == 1: print("File pil_price changed")
            else:
                if debug == 1: print ("File pil_price not changed")

    def ChangePriceLatencyJitterPIL(self, CLOUD_COD,PRICE,LATENCY,JITTER):
        #if debug == 1: print ("entrei dentro de ChangePriceLatencyJitterPIL")
        #if debug == 1: print(PRICE)
        #if debug == 1: print(LATENCY)
        #if debug == 1: print(JITTER)
        PRICE=round(float(PRICE))
        LATENCY=round(float(LATENCY))
        JITTER=round(float(JITTER))
        if ((self.B['pil'][CLOUD_COD]['pil_price'] != PRICE) or (self.B['pil'][CLOUD_COD]['pil_latency'] != LATENCY) or (self.B['pil'][CLOUD_COD]['pil_jitter'] != JITTER)): #Change just one this values is different of the entry
            self.B['pil'][CLOUD_COD]['pil_price']=PRICE #change the price
            self.B['pil'][CLOUD_COD]['pil_latency']=LATENCY #change the latency - same price
            self.B['pil'][CLOUD_COD]['pil_jitter']=JITTER #change the jitter
            if debug == 1: print ("PRICE, LATENCIA e JITTER alterados no arquivo pil_price_list.yaml.")
            return 0
        else:
            return -1

def DATEHOURS():
    DATEHOUR = datetime.now().strftime('%d.%m.%y-%H:%M:%S')  # converte hora para string do cliente
    return DATEHOUR

def ExecuteCommand(exec_command):
    try:
        ret = subprocess.run(exec_command, universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
        if debug_file == 1:
            print("DEBUG ON")
            print("CMD - " + exec_command)
            print("RETURN - \n" + ret.stdout)
        return ret.returncode
    except:
        print('FAIL IN COMMAND EXECUTE')
        print("CMD - " + exec_command)
        print("ERROR - " + ret)
        return ret.returncode

def DATEHOURS():
    DATEHOUR = datetime.now().strftime('%d.%m.%y-%H:%M:%S')  # converte hora para string do cliente
    return DATEHOUR

#Collect metric links from cloud1 to cloud2.
def Collector_Metrics_Links_cl1(cloud1_gnocchi,cloud1_resource_id,cloud2,PILFile,CLOUD_FROM,CLOUD_TO):
    while True:
        now=datetime.now()
        intervalo=30
        delta = timedelta(seconds=intervalo)
        time_past=now-delta
        #START = "2021-08-01 13:30:33+00:00"
        #STOP = "2021-08-01 13:35:36+00:00"
        START=time_past
        STOP=now
        GRANULARITY=60.0
        print("horarioInicio: "+str(START))
        print("hoarioFinal: "+str(STOP))
        Latencia_to_cloud2=cloud1_gnocchi.get_last_measure("Lat_To_"+cloud2.getExternalIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)
        print("LatenciatoCloud2: "+str(Latencia_to_cloud2))
        Jitter_to_cloud2=cloud1_gnocchi.get_last_measure("Jit_To_"+cloud2.getExternalIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)
        print("JittertoCloud2: "+str(Jitter_to_cloud2))
        PILFile.SearchChangePriceLatencyJitterPIL(Latencia_to_cloud2,Latencia_to_cloud2,Jitter_to_cloud2,CLOUD_FROM,CLOUD_TO)
        time.sleep(10)

def Collector_Metrics_Links_Demand_Interval_cl1(cloud1_gnocchi,cloud1_resource_id,cloud2,PILFile,CLOUD_FROM,CLOUD_TO,interval,metric_name):
    now=datetime.now()
    delta = timedelta(seconds=interval)
    time_past=now-delta
    START=time_past
    STOP=now
    GRANULARITY=60.0
    return cloud1_gnocchi.get_last_measure(metric_name+cloud2.getExternalIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)

def Collector_Metrics_Links_Demand_Date_cl1(cloud1_gnocchi,cloud1_resource_id,cloud2,PILFile,CLOUD_FROM,CLOUD_TO,start,stop,metric_name):
    #time_past=now-delta
    #START=time_past
    #STOP=now
    ###START='2022-05-21 22:50:00'
    ####STOP='2022-05-21 23:20:00'
    START=start
    STOP=stop
    GRANULARITY=60.0
    return cloud1_gnocchi.get_last_measure_Date(metric_name+cloud2.getExternalIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)

def Collector_Metrics_Demand_Date(cloud,cloud1_gnocchi,cloud1_resource_id,cloud2_gnocchi,cloud2_resource_id,cloud2,PILFile,CLOUD_FROM,CLOUD_TO,start,stop,metric_name):
    START=start
    STOP=stop
    GRANULARITY=60.0    
    if cloud == "1":
        print ("passei cloud 1")
        return cloud1_gnocchi.get_last_measure_Date(metric_name,cloud1_resource_id,None,GRANULARITY,START,STOP)
    if cloud == "2":
        print ("passei cloud 2")
        return cloud2_gnocchi.get_last_measure_Date(metric_name,cloud2_resource_id,None,GRANULARITY,START,STOP)


#Collect metric links from cloud1 to cloud2
def Monitor_Request_LatencyUser_Cloud1(cloud1_gnocchi,cloud1_resource_id,VNFFile,CLOUD_FROM):
    while True:
        #START = "2021-08-01 13:30:33+00:00"
        #STOP = "2021-08-01 13:35:36+00:00"
        START=start
        STOP=stop
        GRANULARITY=60.0
        print("horarioInicio: "+str(START))
        print("hoarioFinal: "+str(STOP))
        Latencia_to_cloud2=cloud1_gnocchi.get_last_measure(cloud1_resource_id,None,GRANULARITY,START,STOP)
        print(Latencia_to_cloud2)
        #Jitter_to_cloud2=cloud1_gnocchi.get_last_measure("Jit_To_"+cloud2.getIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)
        #print(Jitter_to_cloud2)
        #PILFile.SearchChangePriceLatencyJitterPIL(Latencia_to_cloud2,Latencia_to_cloud2,Jitter_to_cloud2,CLOUD_FROM,CLOUD_TO)
        #time.sleep(5)

def Collector_Metrics_Disaggregated_cl1(cloud1_gnocchi,cloud1_resource_id_nova,Cloud,VNFFile):
    while True:
        now=datetime.now()
        intervalo=30
        delta = timedelta(seconds=intervalo)
        time_past=now-delta
        START=time_past
        STOP=now
        GRANULARITY=60.0
        print("horarioInicio: "+str(START))
        print("hoarioFinal: "+str(STOP))
        CPU_cloud1=cloud1_gnocchi.get_last_measure("compute.node.cpu.idle.percent",cloud1_resource_id_nova,None,GRANULARITY,START,STOP)
        print (CPU_cloud1)
        print("url da cloud na thread")
        print(Cloud.getVimURL())
        print("cpu atual da cloud")
        print(CPU_cloud1)
        print("status da cpu")
        print(Cloud.getCpuStatus())

        #if (int(CPU_cloud1) > THRESHOLD) and (Cloud.getCpuStatus() == 0):
        #    CPU_STATUS_NOW=1   #Values: 0-cpu normal, 1-cpu high and cost value going to change
        #    VNFFile.SearchDownUpVimPrice(CPU_STATUS_NOW,Cloud) #The cost is add by CPU bigger
        #if (int(CPU_cloud1) < THRESHOLD) and (Cloud.getCpuStatus() == 1):
        #    CPU_STATUS_NOW=0   #Values: 0-cpu normal, 1-cpu high and cost value going to change
        #    VNFFile.SearchDownUpVimPrice(CPU_STATUS_NOW,Cloud) #The cost is add by CPU bigger

        ##### FALTA CRIAR RESOURCE NOVA NOS OPENSTACK E POPULAR, BAIXAR TEMPO DE COLETA TB, ENTENDER...
        time.sleep(5)


def Collector_Metrics_VNF():
    pass

def InsertUser(name0, username0, password0):
    TestUsers=Users.get_or_none(Users.username==username0)
    if TestUsers is None:
        print ("The user will be insert.")
        Users.insert(
            name = name0,
            username = username0,
            password = password0,
            creation_date = datetime.now()
        ).execute()
        return "UserInserted"
    else:
        return "UserNotInserted"

def InsertJob(cod_uuid0,userip0, ns_name0,cod_fkuser,cod_status):
    Jobs.insert(
        userip = userip0,
        cod_uuid= cod_uuid0,
        start_date = datetime.now(),
        ns_name=ns_name0,
        fk_user = cod_fkuser,
        fk_status = cod_status
    ).execute()

def InsertJobVnfCloud(cost_vnf,id_fk_job,id_fk_vnf,id_fk_cloud):
    Jobs_Vnfs_Clouds.insert(
        cost = cost_vnf,
        fk_job = id_fk_job,
        fk_vnf = id_fk_vnf,
        fk_cloud = id_fk_cloud,
        creation_date = datetime.now()
    ).execute()

def InsertCloud(name0, ip0, external_ip0,cod_degradation_cloud_type,threshold_value):
    Clouds.insert(
        name=name0,
        ip=ip0,
        external_ip=external_ip0,
        fk_degradation_cloud_type = cod_degradation_cloud_type,
        threshold_degradation = threshold_value,
        creation_date=datetime.now()
    ).execute()

def InsertMetric(name_metric, cloud_cod):
    Metrics.insert(
        name = name_metric,
        fk_cloud = cloud_cod,
        creation_date = datetime.now()
    ).execute()

def InsertVnf(name_vnf):
    Vnfs.insert(
        name=name_vnf,
        creation_date=datetime.now()
    ).execute()

def InsertMetricsVnf(metric_data, weight_percent0, cod_vnf, cod_metric):
    Metrics_Vnfs.insert(
        metric_value = metric_data,
        weight_percent = weight_percent0,
        fk_vnf = cod_vnf,
        fk_metric = cod_metric,
        creation_date = datetime.now()
    ).execute()

def InsertStatusJobs(nameStatus):
    Status_Jobs.insert(
        name = nameStatus,
        creation_date = datetime.now()
    ).execute()

def InsertDegradationsCloudsTypes(name_type):
    Degradations_Clouds_Types.insert(
        name = name_type,
        creation_date = datetime.now()
    ).execute()

def InsertDegradations_Clouds(id_fk_cloud, status_degradation_cloud, current_value_degradation0):
    Degradations_Clouds.insert(
        status_degradation_cloud = status_degradation_cloud, #1 if degration start, and 0 if stoped
        current_value_degradation = current_value_degradation0,
        fk_cloud = id_fk_cloud,
        creation_date = datetime.now()
    ).execute()


def TestLoadBD():
    print("Iniciando carga BD.")
    #PreLoadDefault
    InsertDegradationsCloudsTypes("CPU")
    InsertDegradationsCloudsTypes("Memoria")
    InsertCloud("Serra","10.50.0.159","200.137.75.160",1,90)
    InsertCloud("Aracruz","172.16.112.60","200.137.82.21",2,91 )
    InsertDegradations_Clouds(1,1,98)
    InsertVnf("VNFA")
    InsertVnf("VNFB")
    InsertStatusJobs("Started")
    InsertStatusJobs("Finished")
    InsertUser("Jose Carlos","jcarlos","abc")
    InsertUser("Amarildo de Jesus","ajesus","abcd")
    #UsingSystem
    #Insert Job with User IP, name NS, cod administrator user and cod job status
    cod_uuid=uuid.uuid4()
    print (str(cod_uuid))
    InsertJob(cod_uuid,"10.0.19.148","teste_mestrado",1,1)
    #Insert Jo
    InsertJobVnfCloud(20,1,1,1)
    InsertMetric("Lat_to_8.8.8.8",1)
    InsertMetric("Lat_to_1.1.1.1",1)
    InsertMetricsVnf(20,8,1,1)


def main():
    print ("Iniciando Server PLAO")
    VNFFile = File_VNF_Price()
    PILFile = File_PIL_Price()

    NAME_VNFD="VNFA"

    #print receber a posicao do VNF no arquivo confi VNF OSM
    #print("testando SearchVNFD")
    #teste1 = VNFFile.SearchVNFD(NAME_VNFD)
    #print(teste1)
    #print("     ")

    #print("testando ChangeVNFPrice")
#    VIM_URL="http://10.159.205.6:5000/v3"
#    PRICE_VNFD=78
#    CLOUD_STATUS_CPU=1 #1 se a cpu estiver degradada
    #teste2 = VNFFile.ChangeVNFPrice(2,VIM_URL,PRICE_VNFD,CLOUD_STATUS_CPU)
    #print(teste2)

#    print("testando SearchChangeVNFDPrice") #Este devera se executaod por thrad que ira coletar das nuvens a latencia e cpu para formar o custo da VNF
#    VNFFile.SearchChangeVNFDPrice(NAME_VNFD,VIM_URL,PRICE_VNFD,CLOUD_STATUS_CPU)

    servers = Servers()

    print("Loading Cloud Class with Clouds")
    cloud1 = Cloud(servers.getbyIndexIP(0),servers.getbyIndexExternalIP(0))   
    cloud1.setName(servers.getServerName(cloud1.getIp()))
    print(cloud1.getName())
    cloud1.setVimURL("http://200.137.82.21:5000/v3")
    #cloud1.setVimURL("http://10.159.205.8:5000/v3")
    print(cloud1.getIp())
    print(cloud1.getVimURL())
    print(cloud1.getName())       
    print(cloud1.getCpu())

    cloud2 = Cloud(servers.getbyIndexIP(1),servers.getbyIndexExternalIP(1))
    cloud2.setName(servers.getServerName(cloud2.getIp()))
    #cloud2.setVimURL("https://200.137.75.159:5000/v3")
    #cloud2.setVimURL("http://10.159.205.11:5000/v3")
    print(cloud2.getIp())
    print(cloud2.getVimURL())
    print(cloud2.getName())    
    print(cloud2.getCpu())


    print("Creating session in Openstack1...")
    #Creating session OpenStack
    #auth_session = OpenStack_Auth(cloud_name=VarCloudName)
    cloud1_auth_session = OpenStack_Auth(cloud_name=cloud1.getName())
    cloud1_sess = cloud1_auth_session.get_session()
    print("Creating object and using session in Gnocchi...")
    #Insert Session in Gnocchi object   
    cloud1_gnocchi = Gnocchi(session=cloud1_sess)
    cloud1_resource_id=cloud1_gnocchi.get_resource_id("plao")

    #######print ("resource_id: "+str(cloud1_resource_id)) 

 

    print("Creating session in Openstack2...")
    #Creating session OpenStack
    #auth_session = OpenStack_Auth(cloud_name=VarCloudName)
    print(cloud2.getName())
    cloud2_auth_session = OpenStack_Auth(cloud_name=cloud2.getName())
    cloud2_sess = cloud2_auth_session.get_session()
    print("Creating object and using session in Gnocchi...")
    #Insert Session in Gnocchi object   
    cloud2_gnocchi = Gnocchi(session=cloud2_sess)
    cloud2_resource_id=cloud2_gnocchi.get_resource_id("plao")   
    #print ("resource_id: "+cloud1_resource_id)

    #Test for consult data in gnocchi
    #teste(Gnocchi,cloud1_resource_id,cloud2.getIp(),GRANULARITY,START,STOP)
    #


    #Latencia_to_cloud2=cloud1_gnocchi.get_last_measure("Lat_To_"+cloud2.getIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)
    #print (Latencia_to_cloud2)
    #Latencia_to_cloud2=cloud1_gnocchi.get_last_measure("Lat_To_"+cloud2.getIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)

    #Latencia_to_cloud2 = Latencia_to_cloud2.drop(["granularity","timestamp"],axis=1)
    #teste_Latencia_to_cloud2=Latencia_to_cloud2.head(1)
    #teste_Latencia_to_cloud2=Latencia_to_cloud2.head(1).values
    ##print("valorLatenciatoCloud2: "+str(Latencia_to_cloud2))
    ##print (Latencia_to_cloud2)
    ##Jitter_to_cloud2=cloud1_gnocchi.get_last_measure("Jit_To_"+cloud2.getIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)
    #print (Latencia_to_cloud2)
    #Latencia_to_cloud2 = Latencia_to_cloud2.drop(["granularity","timestamp"],axis=1)
    #teste_Latencia_to_cloud2=Latencia_to_cloud2.head(1)
    #teste_Latencia_to_cloud2=Latencia_to_cloud2.head(1).values
   ##print("valorJittertoCloud2: "+str(Jitter_to_cloud2))

    #print ('teste banco')
    #teste=Users.get_or_none(Users.id_user=='6', Users.name!="")
    #print (teste)
    #if teste is None:



    #File in Clouds
    app = Flask(__name__)

    # The payload is the user ip address.
    #nuvem1="10.159.205.8"
    nuvem1="200.137.82.21"
    #nuvem2="10.159.205.11"
    nuvem2="200.137.75.159"

    #Start aplication in server and clients, and start Thread of collector links metrics.
    @app.route('/start/',methods=['POST'])
    def start():
        if request.method == "POST":

            ret_status = 0 #status of return cloud
            request_data = request.get_json()
            payload = request_data['ipuser']
            
            try:
                a = requests.request(
                    method="POST", url='http://'+nuvem1+':3333/start/', json=payload)

                if a.text == "System_Already_Started" :
                    ret_status=ret_status+2
                    print("PLAO_client_Already_Started:"+ nuvem1)
                if a.text == "System_Started" :
                    ret_status=ret_status+3
                    print("PLAO_client_Started:"+ nuvem1)

            except requests.ConnectionError:
                print("OOPS!! Connection Error. Make sure you are connected to Internet.\n")           
            except requests.Timeout:
                print("OOPS!! Timeout Error")
            except requests.RequestException:
                print("OOPS!! General Error")
            except KeyboardInterrupt:
                print("Someone closed the program")

            try:
                a = requests.request(
                    method="POST", url='http://'+nuvem2+':3333/start/', json=payload)
                #print(a.text+" Enviando start para "+nuvem2)
                if a.text == "System_Already_Started" :
                    ret_status=ret_status+2
                    print("PLAO_client_Already_Started:"+ nuvem2)
                if a.text == "System_Started" :
                    ret_status=ret_status+3
                    print("PLAO_client_Started:"+ nuvem2)
            except requests.ConnectionError:
                print("OOPS!! Connection Error. Make sure you are connected to Internet.\n")
                return ""            
            except requests.Timeout:
                print("OOPS!! Timeout Error")
            except requests.RequestException:
                print("OOPS!! General Error")
            except KeyboardInterrupt:
                print("Someone closed the program")

            if ret_status == 3:
                return "Started_PLAO_JustOneCloud"
            if ret_status == 2:
                return "PLAO_client_Already_Started_One_Cloud"
            if ret_status == 4:
                return "PLAO_client_Already_Started_All_Clouds"
            if ret_status == 5:
                return "Started_PLAO_OneClouds_and_AlreadyStartedOneCloud"
            if ret_status == 6:
                return "Started_PLAO_AllClouds"
            else:
                return "Started"

    @app.route('/TestLoadBD/',methods=['POST'])
    def cargabd():
        TestLoadBD()
        return "LoadedBase"

    @app.route('/stop/',methods=['POST'])
    def stop():
        if request.method == "POST":

            request_data = request.get_json()
            payload = request_data['ipuser']
            
            try:
                a = requests.request(
                    method="POST", url='http://'+nuvem1+':3333/stop/', json=payload)

            except requests.ConnectionError:
                print("OOPS!! Connection Error. Make sure you are connected to Internet.\n")           
            except requests.Timeout:
                print("OOPS!! Timeout Error")
            except requests.RequestException:
                print("OOPS!! General Error")
            except KeyboardInterrupt:
                print("Someone closed the program")

            try:
                a = requests.request(
                    method="POST", url='http://'+nuvem2+':3333/stop/', json=payload)
            except requests.ConnectionError:
                print("OOPS!! Connection Error. Make sure you are connected to Internet.\n")
                return ""            
            except requests.Timeout:
                print("OOPS!! Timeout Error")
            except requests.RequestException:
                print("OOPS!! General Error")
            except KeyboardInterrupt:
                print("Someone closed the program")
            return "Stoped"

    @app.route('/monitor/',methods=['POST'])
    def monitor():
        if request.method == "POST":
            print("Starting Thread to monitor last latency and Jitter betweeen Cloud1 and Cloud2")
            thread_MonitorLinks = threading.Thread(target=Collector_Metrics_Links_cl1,args=(cloud1_gnocchi,cloud1_resource_id,cloud2,PILFile,"openstack1","openstack2"))
            thread_MonitorLinks.start()

            cloud1_resource_id_nova=cloud1_gnocchi.get_resource_id("nova_compute")
            if cloud1_resource_id_nova != -1:
                print("Starting Thread to monitor last cpu in Cloud 1")
                #thread_MonitorDisaggregated1 = threading.Thread(target=Collector_Metrics_Disaggregated_cl1,args=(cloud1_gnocchi,cloud1_resource_id_nova,cloud1,VNFFile))
                #thread_MonitorDisaggregated1.start()
            else:
                print("Resource nova_compute not exist, need to create.")
            print ("resource_id+cloud1: "+str(cloud1_resource_id_nova))

            cloud2_resource_id_nova=cloud2_gnocchi.get_resource_id("nova_compute")
            if cloud2_resource_id_nova != -1:
                print("Starting Thread to monitor last cpu in Cloud 2")
                #thread_MonitorDisaggregated2 = threading.Thread(target=Collector_Metrics_Disaggregated_cl1,args=(cloud2_gnocchi,cloud2_resource_id,cloud2,VNFFile))
                #thread_MonitorDisaggregated2.start() 
            else:
                print("Resource nova_compute not exist, need to create.")
            print ("resource_id_cloud2: "+str(cloud2_resource_id_nova))
       
            return "MonitorStarted"

    @app.route('/selectMetricTime_old/',methods=['POST'])
    def selectMetricTime_old():
        if request.method == "GET":
            interval=60
            request_data = request.get_json()
            print(request_data)
            START = request_data['startdate']
            STOP = request_data['stopdate']
            result = Collector_Metrics_Links_Demand_Date_cl1(cloud1_gnocchi,cloud1_resource_id,cloud2,PILFile,"openstack1","openstack2",START,STOP,"Lat_To_")
            return str(result)
        return "ok"
 
    @app.route('/selectMetricTime/',methods=['GET'])
    def selectMetricTime():
        if request.method == "POST":
            interval=60
            request_data = request.get_json()
            print(request_data)
            START = request_data['startdate']
            STOP = request_data['stopdate']
            METRIC_NAME = request_data['metricname']
            CLOUD_COD = request_data['cloudcod']
            result = Collector_Metrics_Demand_Date(CLOUD_COD,cloud1_gnocchi,cloud1_resource_id,cloud2_gnocchi,cloud2_resource_id,cloud2,PILFile,"openstack1","openstack2",START,STOP,METRIC_NAME)
            return str(result)
        return "ok"

    #Latency between clouds and user
    @app.route("/userlatency/", methods=['POST', 'GET', 'DELETE'])
    def latencia_user_plao():
        if request.method == "POST":
            request_data = request.get_json()
            controle=0
            try:          
                #Future: To read config file and start theese request automaticaly, for example to 1, 2, 3, 4 clouds...
                print("Inicio Teste na nuvem 1")
                # Request to cloud. Is necessary in http URL the cloud ip address
                a = requests.request(
                    method="POST", url='http://'+nuvem1+':3333/userlatency/', json=request_data)
                print(a.text)
                print("Fim Teste na nuvem 1")
                print("Inicio Teste na nuvem 2")
                a = requests.request(
                    method="POST", url='http://'+nuvem2+':3333/userlatency/', json=request_data)
                print(a.text)
                print("Fim Teste na nuvem 2")
                return "Executado"
            except Exception:
                print("erro ao conectar na porta 3333")
                return "Executado"

    #List of VNF in BD
    @app.route("/listvnf/", methods=['GET'])
    def listvnf():
        if request.method == "GET":
            CHECK_VNF=Vnfs.get_or_none()   
            if CHECK_VNF is not None: 
                VNF_LIST=Vnfs.select().dicts()#.get(Vnfs.name!="VNF*")
                df = pd.DataFrame(VNF_LIST, columns =['id_vnf', 'name', 'creation_date'])
                if (df.__len__() == 0):
                    return -1
                df2=json.dumps(json.loads(df.to_json(orient = 'records')), indent=2)
                return (df2) 
                #for row in VNF_LIST:
                #    print(row)
                #return "ok"
            return "NO VNFS IN BD"

    @app.route("/sendjob/", methods=['POST', 'GET', 'DELETE'])
    def send_job():
        if request.method == "POST":

            ret_status = 0 #status of return cloud
            request_data = request.get_json()
            IP_USER=request_data['ipuser']
            NS_NAME="teste_metrado" #alterar para pegar o parametro tb
            COD_USER=1 #Criar funcao para validar usuario no futuro
            COD_STATUS_JOB=1 #(1-Started,2-Finish)
            COD_UUID=uuid.uuid4()
            METRIC_NAME = request_data['metricname']
            METRIC1="Lat_To_"+IP_USER
            METRIC2="CPU"
            COD_VNF1=1 #request_data['codvnf1']
            COD_VNF2=2 #request_data['codvnf2']       
            WEIGHT_PERCENT_METRIC1_CL1=20 #['weight_percent_metric1_cl1']
            WEIGHT_PERCENT_METRIC2_CL1=80 #['weight_percent_metric1_cl1']
            WEIGHT_PERCENT_METRIC1_CL2=20 #['weight_percent_metric1_cl1']
            WEIGHT_PERCENT_METRIC2_CL2=80 #['weight_percent_metric1_cl1']
            
            InsertJob(COD_UUID,IP_USER,NS_NAME,COD_USER,COD_STATUS_JOB) #Desejavel retornar o uuid com o codigo unico do job

            try:          
                #Future: To read config file and start theese request automaticaly, for example to 1, 2, 3, 4 clouds...
                print("Inicio Teste na nuvem 1")
                # Request to cloud. Is necessary in http URL the cloud ip address
                a = requests.request(
                    method="POST", url='http://'+nuvem1+':3333/userlatency/', json=request_data)

                if a.text == "System_Already_Started" :
                    ret_status=ret_status+2
                    print("PLAO_client_Already_Started:"+ nuvem1)
                if a.text == "Executed" :
                    ret_status=ret_status+3
                    print("UserLatencyExecuted:"+ nuvem1)

                print(a.text)
                print("Fim Teste na nuvem 1")
            except requests.ConnectionError:
                print("OOPS!! Connection Error. Make sure you are connected to Internet.\n")           
            except requests.Timeout:
                print("OOPS!! Timeout Error")
            except requests.RequestException:
                print("OOPS!! General Error")
            except KeyboardInterrupt:
                print("Someone closed the program")


            try:          
                #Future: To read config file and start theese request automaticaly, for example to 1, 2, 3, 4 clouds...
                print("Inicio Teste na nuvem 2")
                a = requests.request(
                    method="POST", url='http://'+nuvem2+':3333/userlatency/', json=request_data)
                print(a.text)
                print("Fim Teste na nuvem 2")

                if a.text == "System_Already_Started" :
                    ret_status=ret_status+2
                    print("PLAO_client_Already_Started:"+ nuvem2)
                if a.text == "Executed" :
                    ret_status=ret_status+3
                    print("UserLatencyExecuted:"+ nuvem2)

            except requests.ConnectionError:
                print("OOPS!! Connection Error. Make sure you are connected to Internet.\n")           
            except requests.Timeout:
                print("OOPS!! Timeout Error")
            except requests.RequestException:
                print("OOPS!! General Error")
            except KeyboardInterrupt:
                print("Someone closed the program")


            now=datetime.now()
            intervalo=60
            delta = timedelta(seconds=intervalo)
            time_past=now-delta
            START=time_past
            STOP=now
            GRANULARITY=60.0
            CLOUD1_COD=1
            CLOUD2_COD=2
            #print("horarioInicio: "+str(START))
            #print("hoarioFinal: "+str(STOP))
            DATA_METRIC1_CL1=cloud1_gnocchi.get_last_measure(METRIC1,cloud1_resource_id,None,GRANULARITY,START,STOP)
            DATA_METRIC2_CL1=30   #FALTA coletar CPU

            DATA_METRIC1_CL2=cloud2_gnocchi.get_last_measure(METRIC1,cloud2_resource_id,None,GRANULARITY,START,STOP)
            DATA_METRIC2_CL2=30   #FALTA coletar CPU

            #Insert metrics in METRICS table
            InsertMetric(METRIC1,CLOUD1_COD)
            InsertMetric(METRIC2,CLOUD1_COD)
            InsertMetric(METRIC1,CLOUD2_COD)
            InsertMetric(METRIC2,CLOUD2_COD)

            #Insert values metrics in METRICS_VNF table
            InsertMetricsVnf(DATA_METRIC1_CL1,WEIGHT_PERCENT_METRIC1_CL1,COD_VNF1,codigoselectmetric1pelonometabelametrics)
            InsertMetricsVnf(DATA_METRIC2_CL1,WEIGHT_PERCENT_METRIC2_CL1,COD_VNF1,codigoselectmetric1pelonometabelametrics)
            InsertMetricsVnf(DATA_METRIC1_CL2,WEIGHT_PERCENT_METRIC1_CL2,COD_VNF2,codigoselectmetric1pelonometabelametrics)
            InsertMetricsVnf(DATA_METRIC2_CL2,WEIGHT_PERCENT_METRIC2_CL2,COD_VNF2,codigoselectmetric1pelonometabelametrics)

            #Insert values in JOBS_VNFS_CLOUDS table, necessario math join 2 metrics and wheights



            #COD_CLOUD1=request_data['cod_cloud1'] #talvez nao
            #VNF1=request_data['cod_vnf1']
            #TYPE_METRIC1=request_data['typemetric1'] #cpu or memory or latency
            #            WEIgHT_PERCENT_METRIC1=request_data['weight_percent_metric1']
            #if TYPE_METRIC1 == "CPU":
                #4 cadastrar ultimo valor na tabela metricas
                #5 de acordo com os pesos, calcular o que vai gravar em cost, tabela Jobs_Vnfs_Clouds



            

            VNF_COST1=""
            
            COD_CLOUD2=request_data['cod_cloud2'] #talvez nao
            VNF2=request_data['cod_vnf2']
            TYPE_METRIC2=request_data['typemetric2'] #cpu or memory
            WEIHT_PERCENT_METRIC2=request_data['weight_percent_metric2']
            VNF_COST2=""

            CHECK_METRIC_CL1=cloud1_gnocchi.get_metric(METRIC_NAME,cloud1_resource_id)
            if CHECK_METRIC_CL1 != "":
                print ("EXITS METRIC CL1")
            CHECK_METRIC_CL2=cloud2_gnocchi.get_metric(METRIC_NAME,cloud2_resource_id)
            if CHECK_METRIC_CL2 != "":
                print ("EXITS METRIC CL2")

            InsertJobVnfCloud(VNF_COST1,COD_UUID,VNF1,1)
            InsertJobVnfCloud(VNF_COST2,COD_UUID,VNF2,2)

            if ret_status == 3:
                return "UserLatency_JustOneCloud"
            if ret_status == 2:
                return "UserLatency_Already_Started_One_Cloud"
            if ret_status == 4:
                return "UserLatency_Already_Started_All_Clouds"
            if ret_status == 5:
                return "UserLatency_OneClouds_and_AlreadyStartedOneCloud"
            if ret_status == 6:
                return "UserLatency_Executed_PLAO_AllClouds"
            else:
                return "Started"
            

            #Agora pesquisar o valor da coleta de latencia das nuvens para o ip do usuario, cpu da nuvem 1 e cpu da nuvem2, pegar os ultimos valores
            #Criar job no BD com o id do job e guardar: verificado (sim ou nao),ip do usuario, latencia p nuvem1, latencia p nuvem2, ping da nuvem 1 p 2, jitter da nuvem 1 p 2

            #Em paralelo thread que fica olhando tabela de jobs, compara arquivos e altera se tiver diferenca
            #entrar regras de mudar depois de determinada variacao ou modulo xx

        #Criar rota retorna lista de NS
        #Criar rota retorna lista de VNFD
        #Criar rota retorna dados de metricas latencia, jitter, cpu num intervalor de tempo start e stop escolhido
        #Criar rota retorna 

    #servers = Servers()
    #IPServerLocal="10.159.205.10"
    IPServerLocal="127.0.0.1"
    #Alterar para IP do servidor do PLAO
    app.run(IPServerLocal, '3332',debug=True)
 

    #Thread para enviar request 
    #thread_MonitorLatencyUser = threading.Thread(target=Request_LatencyUser_Cloud1,args=(cloud1_gnocchi,cloud1_resource_id,cloud2,VNFFile,"openstack1","openstack2"))
    ###thread_MonitorLatencyUser.start()

    #Jitter_to_cloud2=cloud1_gnocchi.get_measure("Jit_To_"+cloud2.getIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)
    #Jitter_to_cloud2 = Jitter_to_cloud2.drop("granularity",axis=1)
    #dataset = Latencia_to_cloud2.merge(Jitter_to_cloud2, how='left',on='timestamp',suffixes=["Lat_To_"+cloud2.getIp(),"Jit_To_"+cloud2.getIp()])
    #print(dataset)
    #DataSet(cloud1_gnocchi)

    #Creating vector with objects Cloud 
    #To add clouds in vector
    #clouds = []
    #for i in range(servers.getServerQtd()):
    #    clouds.append(Cloud(servers.getbyIndexIP(i))) 
    #for i in range(len(clouds)):
    #    print(clouds[i].getIp())
    #clouds[0].setCpu(20)
    #print (clouds[0].getCpu())
    #https://www.geeksforgeeks.org/how-to-create-a-list-of-object-in-python-class/
    
if __name__ == "__main__":
    main()