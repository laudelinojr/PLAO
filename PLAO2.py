from ast import Try
from distutils.util import execute
from http.client import HTTPConnection
from multiprocessing.connection import Connection
from operator import eq
from random import randint
from uuid import NAMESPACE_X500, uuid4
import uuid
from wsgiref.validate import validator
from certifi import where
from psutil import users
import yaml
import threading
import subprocess
from datetime import date,timedelta
from PLAO_client2 import *
#from PLAO2_w_routes import app
from flask import Flask, request
import requests
from database.models import *
import time

from osm.osm import osm_create_token


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

class OSM_Auth():
    def __init__(self, IP):
        self.ip = IP
        self.token = ''
        self.name = ''
        self.port= 9999

    def geturls(self,url):   
        urls = { 'url_projects'  : '/osm/admin/v1/projects',  
        'url_users' : '/osm/admin/v1/users',
        'url_vim' : '/osm/admin/v1/vims' ,
        'url_vnf' : '/osm/vnfpkgm/v1/vnf_packages',
        'url_associate' : '/osm/admin/v1/users/admin',
        'url_token_osm' : '/osm/admin/v1/tokens',
        'url_ns_descriptor' : '/osm/nsd/v1/ns_descriptors_content',
        'url_vim_accounts' : '/osm/admin/v1/vim_accounts',
        'url_ns_instance' : '/osm/nslcm/v1/ns_instances',
        'url_osm' : '/osm'
        }
        return "https://"+str(self.ip)+":"+str(self.port)+str(urls.get(url))
    
    def osm_create_token(self):
        project_id='admin'
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        payload = {
            "username": 'admin',
            "password": 'admin',
            "project_id": project_id
        }
        response = requests.request(method="POST", url=str(self.geturls('url_token_osm')), headers=headers,
                                    json=payload, verify=False)
        return response.json()

    def osm_get_vim_accounts(self,token):
        # GET /admin/v1/vims Query information about multiple VIMs
        method_osm = "/admin/v1/vims/"
        #url = url_osm+method_osm
        #url=str(url)
        url=self.geturls(self.ip,'url_token_osm')
        payload = {}
        # token = token.replace('\r','')

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": 'Bearer '+str(token)
        }
        response = requests.request("GET", url, headers=headers, data=payload,verify=False)
        return response.json()

    def check_token_valid(self,token):
        #Compara unixtimestemp e se for o caso gera outro invocando o osm_create_token
        actual=time.time()
        to_expire=token['expires']
        if (to_expire < actual):
            print ("Unixtimestamp atual:")
            print(actual)
            print("Unixtimestamp do token")
            print (to_expire)
            print("Renovando token...")
            self.osm_create_token()

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
    # If the CPU High - degraded (1), we add the extra value in Price.
    def ChangeVNFPrice(self,COD_VNFD,VIMURL,PRICE,CLOUD_STATUS_DEGRADATION):
        C = len(self.B[COD_VNFD]['prices']) #Elements
        #print(C)
        if COD_VNFD < 0:
            return -1  
        if (CLOUD_STATUS_DEGRADATION == 1):
            #print ("PRICE BEFORE DEGRADATION_STATUS: "+ str(PRICE))
            PRICE=int(PRICE)+DOWN_UP_PRICE
            #print ("PRICE AFTER DEGRADATION_STATUS: "+ str(PRICE))
            #print("Add value because is in degradation status.") 
        for i in range(C):
            if self.B[COD_VNFD]['prices'][i]['vim_url'] == VIMURL: #Compare VIMURL between YAML and the new
                if self.B[COD_VNFD]['prices'][i]['price'] != int(PRICE):  #Compare new PRICE with actual Price, if equal, no change
                    print ("Change the Price "+ VIMURL + " " + str(PRICE))
                    #print(self.B[COD_VNFD]['prices'][i]['price'])
                    #if (CLOUD_STATUS_DEGRADATION == 1):
                    #    print(self.B[COD_VNFD]['prices'][i]['price'])
                    #    self.B[COD_VNFD]['prices'][i]['price']=int(PRICE)+DOWN_UP_PRICE #Change the VNF Price
                    #    print("Add value because is in degradation status.")
                    #    print(self.B[COD_VNFD]['prices'][i]['price'])
                    #else:
                    #    print("no else")
                    #    self.B[COD_VNFD]['prices'][i]['price']=int(PRICE) #Change the VNF Price
                    self.B[COD_VNFD]['prices'][i]['price']=int(PRICE) #Change the VNF Price
                    return i
                else:
                    return -1
        else:
            return -1

    #Change VNF File with new Price, change the file
    def SearchChangeVNFDPrice(self,NAME_VNFD,VIM_URL,PRICE_VNFD,CLOUD_STATUS_DEGRADATION):
        if debug == 1: print("In SearchChangeVNFDPrice")
        #print(NAME_VNFD+ VIM_URL + PRICE_VNFD+CLOUD_STATUS_DEGRADATION)
        if (self.ChangeVNFPrice(self.SearchVNFD(NAME_VNFD),VIM_URL,PRICE_VNFD,CLOUD_STATUS_DEGRADATION)) != -1: #Change price of specific VIM in specific VNFD
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

    #Receive the CPU STATUS NOW and update in list cloud, all VNF of this cloud, the CLOUD_STATUS_DEGRADATION
    def SearchDownUpVimPrice(self,STATUS_CPU_NOW,Cloud):    #VIM_URL,CLOUD_COD,STATUS_CPU_NOW):
        VIM_URL=Cloud.getVimURL() # Get vim url for use in next operations
        CLOUD_STATUS_DEGRADATION=Cloud.getCpuStatus() #int(clouds.get(str(CLOUD_COD)).get('CPU')) #Values: 0-cpu normal, 1-cpu high and cost value changed
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
                            if STATUS_CPU_NOW == 1 and CLOUD_STATUS_DEGRADATION == 0: 
                                Cloud.setCpuStatus(1)
                                self.B[i]['prices'][f]['price']=PRICE+DOWN_UP_PRICE #Change the VNF Price with the rate price
                                CHANGED_PRICE_VIM_URL=CHANGED_PRICE_VIM_URL+1 #count auxiliar variable
                                print (self.B[i]['prices'][f]['price'])

                            #If the cloud CPU now is ok (0), but in dict is high (1), we need change dict to (0)
                            if STATUS_CPU_NOW == 0 and CLOUD_STATUS_DEGRADATION == 1 and PRICE >= DOWN_UP_PRICE: 
                                Cloud.setCpuStatus(0)
                                self.B[i]['prices'][f]['price']=int(PRICE-DOWN_UP_PRICE) #Change the VNF Price with the rate price
                                CHANGED_PRICE_VIM_URL=CHANGED_PRICE_VIM_URL+1 #count auxiliar variable
                                print(self.B[i]['prices'][f]['price'])

                            #If the cloud CPU now is ok (0), but in dict is high (1), we need change dict to (0)
                            if STATUS_CPU_NOW == 0 and CLOUD_STATUS_DEGRADATION == 1 and PRICE <= DOWN_UP_PRICE: 
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
        CPU_cloud1=randint(60,99)#cloud1_gnocchi.get_last_measure("compute.node.cpu.idle.percent",cloud1_resource_id_nova,None,GRANULARITY,START,STOP)
        print (CPU_cloud1)
        print("url da cloud na thread")
        print(Cloud.getVimURL())
        print("cpu atual da cloud")
        print(CPU_cloud1)
        print("status da cpu")
        print(Cloud.getCpuStatus())
        #comparar dado da CPU com threashold da nuvem, verificar se o tipo configurado eh cpu, e se for o caso registrar a degradacao
        # fazer o mesmo para tirar o status de degradacao

        #if (int(CPU_cloud1) > THRESHOLD) and (Cloud.getCpuStatus() == 0):
        #    CPU_STATUS_NOW=1   #Values: 0-cpu normal, 1-cpu high and cost value going to change
        #    VNFFile.SearchDownUpVimPrice(CPU_STATUS_NOW,Cloud) #The cost is add by CPU bigger
        #if (int(CPU_cloud1) < THRESHOLD) and (Cloud.getCpuStatus() == 1):
        #    CPU_STATUS_NOW=0   #Values: 0-cpu normal, 1-cpu high and cost value going to change
        #    VNFFile.SearchDownUpVimPrice(CPU_STATUS_NOW,Cloud) #The cost is add by CPU bigger

        ##### FALTA CRIAR RESOURCE NOVA NOS OPENSTACK E POPULAR, BAIXAR TEMPO DE COLETA TB, ENTENDER...
        time.sleep(5)


def InsertUser(name0, username0, password0):
    TestUsers=Users.get_or_none(Users.username==username0)
    if TestUsers is None:
        return Users.insert(
            name = name0,
            username = username0,
            password = password0,
            creation_date = datetime.now()
        ).execute()
    else:
        -1

def InsertJob(userip0, ns_name0,cod_fkuser,cod_status):
    return Jobs.insert(
        userip = userip0,
        start_date = datetime.now(),
        ns_name=ns_name0,
        fk_user = cod_fkuser,
        fk_status = cod_status
    ).execute()

def UpdateJob(job_id, job_status):
    Jobs.update(fk_status = job_status,finish_date = datetime.now()).where(Jobs.id_job==job_id).execute()
    return "ExecutedUpdate"

def InsertJobVnfCloud(cost_vnf,id_fk_job,id_fk_vnf,id_fk_cloud):
    return Jobs_Vnfs_Clouds.insert(
        cost = cost_vnf,
        fk_job = id_fk_job,
        fk_vnf = id_fk_vnf,
        fk_cloud = id_fk_cloud,
        creation_date = datetime.now()
    ).execute()

def UpdateJobVnfCloud(id_jobs_vnf_cloud0, cost_vnf):
    Jobs_Vnfs_Clouds.update(cost = cost_vnf).where(Jobs_Vnfs_Clouds.id_jobs_vnf_cloud==id_jobs_vnf_cloud0).execute()
    return "ExecutedUpdate"

def SelectIdVnf_JobVnfCloud(cod):
    Jobs_Vnfs=Jobs_Vnfs_Clouds.select(Jobs_Vnfs_Clouds.id_vnf).where(Jobs_Vnfs_Clouds.id_jobs_vnf_cloud==cod)
    for row in Jobs_Vnfs:
        return str(row.id_vnf)
    return "-1"


def SelectIdCloud_JobVnfCloud(cod):
    Jobs_Vnfs=Jobs_Vnfs_Clouds.select(Jobs_Vnfs_Clouds.id_cloud).where(Jobs_Vnfs_Clouds.id_jobs_vnf_cloud==cod)
    for row in Jobs_Vnfs:
        return str(row.id_cloud)
    return "-1"

def InsertCloud(name0, ip0, external_ip0,cod_degradation_cloud_type,threshold_value):
    TestCloud=Clouds.get_or_none(Clouds.name==name0)
    if TestCloud is None:
        return Clouds.insert(
            name=name0,
            ip=ip0,
            external_ip=external_ip0,
            fk_degradation_cloud_type = cod_degradation_cloud_type,
            threshold_degradation = threshold_value,
            creation_date=datetime.now()
        ).execute()
    else:
        return -1

def GetIdCloud(name_cloud):
    cloud=Clouds.select(Clouds.id_cloud).where(Clouds.name==name_cloud)
    for row in cloud:
        return str(row.id_cloud)
    return "-1"

def InsertMetric(name_metric):
    TestMetric=Metrics.get_or_none(Metrics.name==name_metric)
    if TestMetric is None:
        return Metrics.insert(
            name = name_metric,
            creation_date = datetime.now()
        ).execute()
    else:
        return GetIdMetric(name_metric)

def InsertMetricCloud(fk_cloud0, fk_metric0):
    Metrics_Clouds.insert(
        fk_cloud = fk_cloud0,
        fk_metric = fk_metric0,
        creation_date = datetime.now()
    ).execute()

def GetIdMetric(NAME_METRIC):
    #teste = Metrics.select(Metrics.id_metric).where((Metrics.name==NAME_METRIC)&(Metrics.fk_cloud==COD_CLOUD))
    metrics = Metrics.select(Metrics.id_metric).where(Metrics.name==NAME_METRIC)
    for row in metrics:
            return str(row.id_metric)
    return "-1"

def InsertVnf(name_vnf):
    TestVnf=Vnfs.get_or_none(Vnfs.name==name_vnf)
    if TestVnf is None:
        Vnfs.insert(
            name=name_vnf,
            creation_date=datetime.now()
        ).execute()
    else:
        -1

def GetIdVNF(NAME_VNF):
    #teste = Metrics.select(Metrics.id_metric).where((Metrics.name==NAME_METRIC)&(Metrics.fk_cloud==COD_CLOUD))
    vnfs = Vnfs.select(Vnfs.id_vnf).where(Vnfs.name==NAME_VNF)
    for row in vnfs:
            return str(row.id_vnf)
    return "-1"

def GetNameVNF(COD):
    VNFGet=Vnfs.select(Vnfs.name).where(Vnfs.id_vnf==COD)
    for row in VNFGet:
        return str(row.name)
    return "-1"

def InsertMetricsVnf(metric_data, weight0, cod_vnf, cod_metric,cod_job_vnf_cloud):
    return Metrics_Vnfs.insert(
        metric_value = metric_data,
        weight = weight0,
        fk_vnf = cod_vnf,
        fk_metric = cod_metric,
        fk_job_vnf_cloud = cod_job_vnf_cloud,
        creation_date = datetime.now()
    ).execute()

def GetMetricsVnf(metric_vnf_id):
    print("imprimir metric vnf id")
    print(metric_vnf_id)
    TestMetricsVnf=Metrics_Vnfs.get_or_none(Metrics_Vnfs.id_metric_vnf==metric_vnf_id)
    if TestMetricsVnf is None:
        return -1
    else:
        metricsvnfs = Metrics_Vnfs.select(Metrics_Vnfs.metric_value,Metrics_Vnfs.weight).where(Metrics_Vnfs.id_metric_vnf==metric_vnf_id)
        for row in metricsvnfs:
            if row.metric_value > str(0):
                return str(row.metric_value+":"+row.weight)
            else:
                return str("0:"+row.weight)

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

def SelectStatusDegradationCloud(CLOUD_ID):
    CloudDegra=Degradations_Clouds.select(Degradations_Clouds.status_degradation_cloud).where((Degradations_Clouds.id_cloud==CLOUD_ID)&(Degradations_Clouds.status_degradation_cloud==1))
    for row in CloudDegra:
        return str(row.status_degradation_cloud)
    return "0"   

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
    #job_cod_uuid=uuid.uuid4()
    #print (str(job_cod_uuid))
    InsertJob("10.0.19.148","teste_mestrado",1,1)
    #Insert Jo
    JOBVNFCLOUD=InsertJobVnfCloud(20,1,1,1)
    print (JOBVNFCLOUD)
    InsertMetric("Lat_to_8.8.8.8")
    InsertMetric("Lat_to_1.1.1.1")
    InsertMetricCloud(1,1)
    InsertMetricsVnf(20,8,1,1,JOBVNFCLOUD)


def main():
    print ("Iniciando Server PLAO")
    VNFFile = File_VNF_Price()
    PILFile = File_PIL_Price()

    IP_OSM="10.159.205.10"
    OSM = OSM_Auth(IP_OSM)
    token=OSM.osm_create_token()

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
    cloud2.setVimURL("https://200.137.75.159:5000/v3")
    #cloud2.setVimURL("http://10.159.205.11:5000/v3")
    print(cloud2.getIp())
    print(cloud2.getVimURL())
    print(cloud2.getName())    
    print(cloud2.getCpu())

    try:
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
    except:
        print ("Problema ao acessar Cloud 1!!!")

    
    try:
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
    except:
        print ("Problema ao acessar Cloud 2!!!")


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
        #InsertMetricsVnf(20,8,1,1,1)
        #print(InsertCloud("Aracruz2","172.16.112.40","200.137.82.31",5,90 ))
        #return GetIdMetrics("Lat_to_8.8.8.8")
        return "LoadedBase"

    @app.route('/getOSMlistvim/',methods=['GET'])
    def OSMlistvim():
        OSM.check_token_valid(token)
        return OSM.osm_get_vim_accounts(token)

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
                thread_MonitorDisaggregated1 = threading.Thread(target=Collector_Metrics_Disaggregated_cl1,args=(cloud1_gnocchi,cloud1_resource_id_nova,cloud1,VNFFile))
                thread_MonitorDisaggregated1.start()
            else:
                print("Resource nova_compute not exist, need to create.")
            print ("resource_id+cloud1: "+str(cloud1_resource_id_nova))

            cloud2_resource_id_nova=cloud2_gnocchi.get_resource_id("nova_compute")
            if cloud2_resource_id_nova != -1:
                print("Starting Thread to monitor last cpu in Cloud 2")
                thread_MonitorDisaggregated2 = threading.Thread(target=Collector_Metrics_Disaggregated_cl1,args=(cloud2_gnocchi,cloud2_resource_id_nova,cloud2,VNFFile))
                thread_MonitorDisaggregated2.start() 
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
            NS_NAME="teste_metrado" #['nsname']#alterar para pegar o parametro tb
            COD_USER=1 #request_data['coduser'] #Criar funcao para validar usuario no futuro
            METRIC1_NAME="Lat_To_"+IP_USER #request_data['metric1name']
            METRIC2_NAME="CPU" #request_data['metric2name']
            VNF1_NAME="VNFA" #request_data['vnf1name']
            VNF2_NAME="VNFB" #request_data['vnf2name']   
            NAME_CLOUD1="Serra" #request_data['cloudname1']
            NAME_CLOUD2="Aracruz" #request_data['cloudname2']
            WEIGHT_METRIC1_VNF1=0.2 #['weight_metric1_vnf1']
            WEIGHT_METRIC2_VNF1=0.8 #['weight_metric2_vnf1']
            WEIGHT_METRIC1_VNF2=0.9 #['weight_metric1_vnf2']
            WEIGHT_METRIC2_VNF2=0.1 #['weight_metric2_vnf2']
            COD_STATUS_JOB=1 #(1-Started,2-Finish)
            
            JOB_COD=InsertJob(IP_USER,NS_NAME,COD_USER,COD_STATUS_JOB)

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

            CLOUD1_COD=GetIdCloud(NAME_CLOUD1)
            CLOUD2_COD=GetIdCloud(NAME_CLOUD2)
            COD_VNF1=GetIdVNF(VNF1_NAME)
            COD_VNF2=GetIdVNF(VNF2_NAME)
            time.sleep(4) #Waiting collects
            #print("horarioInicio: "+str(START))
            #print("hoarioFinal: "+str(STOP))
            #collect data in gnocchi in each cloud
            DATA_METRIC1_CL1=cloud1_gnocchi.get_last_measure(METRIC1_NAME,cloud1_resource_id,None,GRANULARITY,START,STOP)
            DATA_METRIC2_CL1=randint(60,99)   #FALTA coletar CPU
            
            DATA_METRIC1_CL2=cloud2_gnocchi.get_last_measure(METRIC1_NAME,cloud2_resource_id,None,GRANULARITY,START,STOP)
            DATA_METRIC2_CL2=randint(70,99)   #FALTA coletar CPU



            #print(str(DATA_METRIC1_CL1))
            #print(str(DATA_METRIC1_CL2))

            #Insert metrics in METRICS plao bd
            COD_METRIC1=InsertMetric(METRIC1_NAME) #ex latency
            COD_METRIC2=InsertMetric(METRIC2_NAME) # ex cpu

            #Inser metric for cloud
            InsertMetricCloud(CLOUD1_COD,COD_METRIC1)
            InsertMetricCloud(CLOUD1_COD,COD_METRIC2)
            InsertMetricCloud(CLOUD2_COD,COD_METRIC1)
            InsertMetricCloud(CLOUD2_COD,COD_METRIC2)

            #Insert values in JOBS_VNFS_CLOUDS table, necessario math join 2 metrics and wheights
            VNF1_CL1=InsertJobVnfCloud("",JOB_COD,COD_VNF1,CLOUD1_COD)
            VNF2_CL1=InsertJobVnfCloud("",JOB_COD,COD_VNF2,CLOUD1_COD)
            VNF1_CL2=InsertJobVnfCloud("",JOB_COD,COD_VNF1,CLOUD2_COD)
            VNF2_CL2=InsertJobVnfCloud("",JOB_COD,COD_VNF2,CLOUD2_COD)

            #Insert values metrics per cloud in METRICS_VNF table
            #Data of metric one and two, each weight per vnf
            VNF1_CL1_M1=InsertMetricsVnf(DATA_METRIC1_CL1,WEIGHT_METRIC1_VNF1,COD_VNF1,COD_METRIC1,VNF1_CL1) #valor 26, peso  7, vnfa, latencia
            VNF1_CL1_M2=InsertMetricsVnf(DATA_METRIC2_CL1,WEIGHT_METRIC2_VNF1,COD_VNF1,COD_METRIC2,VNF1_CL1) #valor 10, peso 3,  vnfa, cpu
            VNF2_CL1_M1=InsertMetricsVnf(DATA_METRIC1_CL1,WEIGHT_METRIC1_VNF2,COD_VNF2,COD_METRIC1,VNF2_CL1) #valor 26, peso 1, vnfb, latencia
            VNF2_CL1_M2=InsertMetricsVnf(DATA_METRIC2_CL1,WEIGHT_METRIC2_VNF2,COD_VNF2,COD_METRIC2,VNF2_CL1) #valor 10, peso 9,  vnfb, cpu
            VNF1_CL2_M1=InsertMetricsVnf(DATA_METRIC1_CL2,WEIGHT_METRIC1_VNF1,COD_VNF1,COD_METRIC1,VNF1_CL2)
            VNF1_CL2_M2=InsertMetricsVnf(DATA_METRIC2_CL2,WEIGHT_METRIC2_VNF1,COD_VNF1,COD_METRIC2,VNF1_CL2)
            VNF2_CL2_M1=InsertMetricsVnf(DATA_METRIC1_CL2,WEIGHT_METRIC1_VNF2,COD_VNF2,COD_METRIC1,VNF2_CL2)
            VNF2_CL2_M2=InsertMetricsVnf(DATA_METRIC2_CL2,WEIGHT_METRIC2_VNF2,COD_VNF2,COD_METRIC2,VNF2_CL2)

            #print ( "INSERTED RECORDS IN METRICSVNF TABLE:" +
            #" VNF1_CL1_M1: " + str(VNF1_CL1_M1) + 
            #" VNF1_CL1_M2: " + str(VNF1_CL1_M2) +
            #" VNF2_CL1_M1: " + str(VNF2_CL1_M1) +
            #" VNF2_CL1_M2: " + str(VNF2_CL1_M2) +
            #" VNF1_CL2_M1: " + str(VNF1_CL2_M1) +
            #" VNF1_CL2_M2: " + str(VNF1_CL2_M2) +
            #" VNF1_CL2_M1: " + str(VNF1_CL2_M1) +
            #" VNF1_CL2_M2: " + str(VNF1_CL2_M2))
            
            #Calc VNF1 CL1 M1
            print("Calc VNF1 CL1 M1")
            VNF1_CL1_M1_BD=GetMetricsVnf(VNF1_CL1_M1)
            VNF1_CL1_M1_BD=VNF1_CL1_M1_BD.split(':')
            VNF1_CL1_M1_BD_VALUE=VNF1_CL1_M1_BD[0]
            VNF1_CL1_M1_BD_WEIGHT=VNF1_CL1_M1_BD[1]
            VNF1_CL1_M1_CALC=(float(VNF1_CL1_M1_BD_VALUE)*float(VNF1_CL1_M1_BD_WEIGHT))
            print (str(VNF1_CL1_M1_BD_VALUE) + "x" +str(VNF1_CL1_M1_BD_WEIGHT) + "=" +str(VNF1_CL1_M1_CALC))

            #Calc VNF1 CL1 M2
            print("Calc VNF1 CL1 M2")
            VNF1_CL1_M2_BD=GetMetricsVnf(VNF1_CL1_M2)
            print(VNF1_CL1_M2_BD)
            VNF1_CL1_M2_BD=VNF1_CL1_M2_BD.split(':')
            VNF1_CL1_M2_BD_VALUE=VNF1_CL1_M2_BD[0]
            VNF1_CL1_M2_BD_WEIGHT=VNF1_CL1_M2_BD[1]
            VNF1_CL1_M2_CALC=(float(VNF1_CL1_M2_BD_VALUE)*float(VNF1_CL1_M2_BD_WEIGHT))
            print (str(VNF1_CL1_M2_BD_VALUE) + "x" +str(VNF1_CL1_M2_BD_WEIGHT) + "=" +str(VNF1_CL1_M2_CALC))

            #Sum for Calc VNF1 in CL1
            print("Sum for Calc VNF1 in CL1")
            VNF1_CL1_CALC=VNF1_CL1_M1_CALC+VNF1_CL1_M2_CALC
            #print(VNF1_CL1_CALC)
            VNF1_CL1_CALC=round(VNF1_CL1_CALC) #round
            #print(VNF1_CL1_CALC)
            print ("Cost of VNF1 CL1 is "+str(VNF1_CL1_CALC))

            ###############################################################

            #Calc VNF2 CL1 M1
            VNF2_CL1_M1_BD=GetMetricsVnf(VNF2_CL1_M1)
            VNF2_CL1_M1_BD=VNF2_CL1_M1_BD.split(':')
            VNF2_CL1_M1_BD_VALUE=VNF2_CL1_M1_BD[0]
            VNF2_CL1_M1_BD_WEIGHT=VNF2_CL1_M1_BD[1]
            VNF2_CL1_M1_CALC=(float(VNF2_CL1_M1_BD_VALUE)*float(VNF2_CL1_M1_BD_WEIGHT))
            print (str(VNF2_CL1_M1_BD_VALUE) + "x" +str(VNF2_CL1_M1_BD_WEIGHT) + "=" +str(VNF2_CL1_M1_CALC))

            #Calc VNF2 CL1 M2
            VNF2_CL1_M2_BD=GetMetricsVnf(VNF2_CL1_M2)
            VNF2_CL1_M2_BD=VNF2_CL1_M2_BD.split(':')
            VNF2_CL1_M2_BD_VALUE=VNF2_CL1_M2_BD[0]
            VNF2_CL1_M2_BD_WEIGHT=VNF2_CL1_M2_BD[1]
            VNF2_CL1_M2_CALC=(float(VNF2_CL1_M2_BD_VALUE)*float(VNF2_CL1_M2_BD_WEIGHT))
            print (str(VNF2_CL1_M2_BD_VALUE) + "x" +str(VNF2_CL1_M2_BD_WEIGHT) + "=" +str(VNF2_CL1_M2_CALC))

            #Sum for Calc VNF1 in CL1
            VNF2_CL1_CALC=VNF2_CL1_M1_CALC+VNF2_CL1_M2_CALC
            #print(VNF2_CL1_CALC)
            VNF2_CL1_CALC=round(VNF2_CL1_CALC) #round
            #print(VNF2_CL1_CALC)
            print ("Cost of VNF2 CL1 is "+str(VNF2_CL1_CALC))

            ###############################################################

            #Calc VNF1 CL2 M1
            VNF1_CL2_M1_BD=GetMetricsVnf(VNF1_CL2_M1)
            VNF1_CL2_M1_BD=VNF1_CL2_M1_BD.split(':')
            VNF1_CL2_M1_BD_VALUE=VNF1_CL2_M1_BD[0]
            VNF1_CL2_M1_BD_WEIGHT=VNF1_CL2_M1_BD[1]
            VNF1_CL2_M1_CALC=(float(VNF1_CL2_M1_BD_VALUE)*float(VNF1_CL2_M1_BD_WEIGHT))
            print (str(VNF1_CL2_M1_BD_VALUE) + "x" +str(VNF1_CL2_M1_BD_WEIGHT) + "=" +str(VNF1_CL2_M1_CALC))

            #Calc VNF1 CL1 M2
            VNF1_CL2_M2_BD=GetMetricsVnf(VNF1_CL2_M2)
            VNF1_CL2_M2_BD=VNF1_CL2_M2_BD.split(':')
            VNF1_CL2_M2_BD_VALUE=VNF1_CL2_M2_BD[0]
            VNF1_CL2_M2_BD_WEIGHT=VNF1_CL2_M2_BD[1]
            VNF1_CL2_M2_CALC=(float(VNF1_CL2_M2_BD_VALUE)*float(VNF1_CL2_M2_BD_WEIGHT))
            print (str(VNF1_CL2_M2_BD_VALUE) + "x" +str(VNF1_CL2_M2_BD_WEIGHT) + "=" +str(VNF1_CL2_M2_CALC))

            #Sum for Calc VNF1 in CL1
            VNF1_CL2_CALC=VNF1_CL2_M1_CALC+VNF1_CL2_M2_CALC
            #print(VNF1_CL2_CALC)
            VNF1_CL2_CALC=round(VNF1_CL2_CALC) #round
            #print(VNF1_CL2_CALC)
            print ("Cost of VNF1 CL2 is "+str(VNF1_CL2_CALC))

            ###############################################################

            #Calc VNF2 CL2 M1
            VNF2_CL2_M1_BD=GetMetricsVnf(VNF2_CL2_M1)
            VNF2_CL2_M1_BD=VNF2_CL2_M1_BD.split(':')
            VNF2_CL2_M1_BD_VALUE=VNF2_CL2_M1_BD[0]
            VNF2_CL2_M1_BD_WEIGHT=VNF2_CL2_M1_BD[1]
            VNF2_CL2_M1_CALC=(float(VNF2_CL2_M1_BD_VALUE)*float(VNF2_CL2_M1_BD_WEIGHT))
            print (str(VNF2_CL1_M1_BD_VALUE) + "x" +str(VNF2_CL2_M1_BD_WEIGHT) + "=" +str(VNF2_CL2_M1_CALC))

            #Calc VNF2 CL1 M2
            VNF2_CL2_M2_BD=GetMetricsVnf(VNF2_CL2_M2)
            VNF2_CL2_M2_BD=VNF2_CL2_M2_BD.split(':')
            VNF2_CL2_M2_BD_VALUE=VNF2_CL2_M2_BD[0]
            VNF2_CL2_M2_BD_WEIGHT=VNF2_CL2_M2_BD[1]
            VNF2_CL2_M2_CALC=(float(VNF2_CL2_M2_BD_VALUE)*float(VNF2_CL2_M2_BD_WEIGHT))
            print (str(VNF2_CL2_M2_BD_VALUE) + "x" +str(VNF2_CL2_M2_BD_WEIGHT) + "=" +str(VNF2_CL2_M2_CALC))

            #Sum for Calc VNF2 in CL2
            VNF2_CL2_CALC=VNF2_CL2_M1_CALC+VNF2_CL2_M2_CALC
            #print(VNF2_CL2_CALC)
            VNF2_CL2_CALC=round(VNF2_CL2_CALC) #round
            #print(VNF2_CL2_CALC)
            print ("Cost of VNF2 CL2 is "+str(VNF2_CL2_CALC))

            ###############################################################

            #Update Costs in BD
            UpdateJobVnfCloud(VNF1_CL1,VNF1_CL1_CALC)
            UpdateJobVnfCloud(VNF2_CL1,VNF2_CL1_CALC)
            UpdateJobVnfCloud(VNF1_CL2,VNF1_CL2_CALC)
            UpdateJobVnfCloud(VNF2_CL2,VNF2_CL2_CALC)

            #Check degradation
            #if has degradation now in specifc cloud, plus 10 units in vnf cost 
            VNF1_CL1_STATUS_DEGRADATION=SelectStatusDegradationCloud(SelectIdCloud_JobVnfCloud(VNF1_CL1))
            VNF2_CL1_STATUS_DEGRADATION=SelectStatusDegradationCloud(SelectIdCloud_JobVnfCloud(VNF2_CL1))
            VNF1_CL2_STATUS_DEGRADATION=SelectStatusDegradationCloud(SelectIdCloud_JobVnfCloud(VNF1_CL2))
            VNF2_CL2_STATUS_DEGRADATION=SelectStatusDegradationCloud(SelectIdCloud_JobVnfCloud(VNF2_CL2))
            print("id clouds from vnf")
            print (SelectIdCloud_JobVnfCloud(VNF1_CL1), SelectIdCloud_JobVnfCloud(VNF2_CL1), SelectIdCloud_JobVnfCloud(VNF1_CL2), SelectIdCloud_JobVnfCloud(VNF2_CL2) )
            
            print("vnf degradation")
            print(VNF1_CL1_STATUS_DEGRADATION,VNF2_CL1_STATUS_DEGRADATION,VNF1_CL2_STATUS_DEGRADATION,VNF2_CL2_STATUS_DEGRADATION )

            #store somewhere values link for logs          
            NAME_VNF=GetNameVNF(SelectIdVnf_JobVnfCloud(VNF1_CL1))
            VIM_URL=cloud1.getVimURL()
            PRICE_VNFD=str(VNF1_CL1_CALC)
            CLOUD_STATUS_DEGRADATION=int(VNF1_CL1_STATUS_DEGRADATION) #1 se a cpu estiver degradada select degradacao da nuvem
            #print("testando SearchChangeVNFDPrice") #Este devera se executaod por thrad que ira coletar das nuvens a latencia e cpu para formar o custo da VNF
            VNFFile.SearchChangeVNFDPrice(NAME_VNF,VIM_URL,PRICE_VNFD,CLOUD_STATUS_DEGRADATION)
            print((NAME_VNF,VIM_URL,PRICE_VNFD,CLOUD_STATUS_DEGRADATION))

            NAME_VNF=GetNameVNF(SelectIdVnf_JobVnfCloud(VNF2_CL1))
            VIM_URL=cloud1.getVimURL()
            PRICE_VNFD=str(VNF2_CL1_CALC)
            CLOUD_STATUS_DEGRADATION=int(VNF2_CL1_STATUS_DEGRADATION) #1 se a cpu estiver degradada select degradacao da nuvem
            #print("testando SearchChangeVNFDPrice") #Este devera se executaod por thrad que ira coletar das nuvens a latencia e cpu para formar o custo da VNF
            VNFFile.SearchChangeVNFDPrice(NAME_VNF,VIM_URL,PRICE_VNFD,CLOUD_STATUS_DEGRADATION)
            print((NAME_VNF,VIM_URL,PRICE_VNFD,CLOUD_STATUS_DEGRADATION))

            NAME_VNF=GetNameVNF(SelectIdVnf_JobVnfCloud(VNF1_CL2))
            VIM_URL=cloud2.getVimURL()
            PRICE_VNFD=str(VNF1_CL2_CALC)
            CLOUD_STATUS_DEGRADATION=int(VNF1_CL2_STATUS_DEGRADATION) #1 se a cpu estiver degradada select degradacao da nuvem
            #print("testando SearchChangeVNFDPrice") #Este devera se executaod por thrad que ira coletar das nuvens a latencia e cpu para formar o custo da VNF
            VNFFile.SearchChangeVNFDPrice(NAME_VNF,VIM_URL,PRICE_VNFD,CLOUD_STATUS_DEGRADATION)
            print((NAME_VNF,VIM_URL,PRICE_VNFD,CLOUD_STATUS_DEGRADATION))

            NAME_VNF=GetNameVNF(SelectIdVnf_JobVnfCloud(VNF2_CL2))
            VIM_URL=cloud2.getVimURL()
            PRICE_VNFD=str(VNF2_CL2_CALC)
            CLOUD_STATUS_DEGRADATION=int(VNF2_CL2_STATUS_DEGRADATION) #1 se a cpu estiver degradada select degradacao da nuvem
            #print("testando SearchChangeVNFDPrice") #Este devera se executaod por thrad que ira coletar das nuvens a latencia e cpu para formar o custo da VNF
            VNFFile.SearchChangeVNFDPrice(NAME_VNF,VIM_URL,PRICE_VNFD,CLOUD_STATUS_DEGRADATION)
            print((NAME_VNF,VIM_URL,PRICE_VNFD,CLOUD_STATUS_DEGRADATION))

            #Instanciate NS in OSM

            #Update Status Job
            UpdateJob(JOB_COD,2) #Finished the job
            return "Finished"

        #Criar rota retorna lista de NS
        #Criar rota retorna lista de VNFD

    #servers = Servers()
    #IPServerLocal="10.159.205.10"
    IPServerLocal="127.0.0.1"
    #Alterar para IP do servidor do PLAO
    app.run(IPServerLocal, '3332',debug=True)
 
    
if __name__ == "__main__":
    main()