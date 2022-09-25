from ast import Try
from cgi import test
import csv
from distutils.util import execute
from http.client import HTTPConnection
from multiprocessing.connection import Connection
from operator import contains, eq
from random import randint
from sqlite3 import Date
from uuid import NAMESPACE_X500, uuid4
import uuid
from webbrowser import get
from wsgiref.validate import validator
from attr import has
#import bson
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
import openpyxl

#Block to active log
import logging
#logger = logging.getLogger('peewee')
#logger.addHandler(logging.StreamHandler())
#logger.setLevel(logging.DEBUG)


#FILE_VNF_PRICE="/opt/PLAO/osm/vnf_price_list.yaml"
#FILE_PIL_PRICE="/opt/PLAO/osm/pil_price_list.yaml"
FILE_VNF_PRICE="/opt/PLAO/teste/vnf_price_list.yaml"
FILE_PIL_PRICE="/opt/PLAO/teste/pil_price_list.yaml"
THRESHOLD=90 #THRESHOLD of CPU to apply rate in Cloud's price
PATH_LOG='log/'
#PATH_LOG='/opt/PLAO/log/'
PATH='/opt/PLAO/'
#Debug mode is 1
debug=0
debug_file = 0 #keep 0
#requisites for change all price of specif VIM (Cloud)
DOWN_UP_PRICE=10 #Number to add vnf Price
COMMAND_MON_PLAO=0

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
        'url_vnf_instances' : '/osm/nslcm/v1/vnf_instances/',
        'url_associate' : '/osm/admin/v1/users/admin',
        'url_token_osm' : '/osm/admin/v1/tokens',
        'url_ns_descriptors' : "/osm/nsd/v1/ns_descriptors/",
        'url_ns_descriptor' : '/osm/nsd/v1/ns_descriptors_content',
        'url_vim_accounts' : '/osm/admin/v1/vim_accounts',
        'url_ns_instances' : '/osm/nslcm/v1/ns_instances/',
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

    def osm_delete_vim(self,token,vimID):
        #print ("vai")
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": 'Bearer ' + str(token)
        }
        #print(str(token))
        payload = {
        }
        response = requests.request("DELETE", url=str(self.geturls('url_vim')+"/"+vimID), headers=headers,verify=False)
        #print(response.json())
        return response.json()

    def osm_delete_instance_ns(self, token, nsId_instance):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": 'Bearer ' + str(token)
        }
        payload = {
            "autoremove": True
        }
        response = requests.request(method="POST", url=str(self.geturls('url_ns_instances'))+str(nsId_instance)+'/terminate/', headers=headers,
                                    json=payload, verify=False)
        return response.json()

    def osm_get_instance_vnf(self, token):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": 'Bearer ' + str(token)
        }
        #print(str(self.geturls('url_vnf_instances')))
        response = requests.request(method="GET", url=str(self.geturls('url_vnf_instances')), headers=headers,
                                     verify=False)
        return response.json()

    def osm_get_instance_ns(self, token):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": 'Bearer ' + str(token)
        }
        #print(str(self.geturls('url_ns_instances')))
        response = requests.request(method="GET", url=str(self.geturls('url_ns_instances')), headers=headers,
                                     verify=False)
        return response.json()

    def osm_get_instance_ns_byid(self, token, id):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": 'Bearer ' + str(token)
        }
        response = requests.request(method="GET", url=str(self.geturls('url_ns_instances'))+str(id), headers=headers,
                                     verify=False)
        return response.json()

    def osm_create_instance_ns(self, token, nsName, nsId, vimAccountId):
        nsDescription="created by PLAO"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": 'Bearer ' + str(token)
        }
        payload = {
            "nsdId": nsId,
            "nsName": nsName,
            "nsDescription": nsDescription,
            "vimAccountId": vimAccountId
        }
        response = requests.request(method="POST", url=str(self.geturls('url_ns_instances')), headers=headers,
                                    json=payload, verify=False)
        return response.json()

    def osm_create_instance_ns_scheduled(self, token, nsName, nsIdscheduled, vimAccountId, nsdID,constraint_operacao,constraint_latency,constraint_jitter,constraint_vld_id):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": 'Bearer ' + str(token)
        }
        #contraint_operacao=1 #operation 1: without constraints, operation2: just latency, operation3: just jiter, operation4: latency and jitter 
        #constraint_latency=2 #need integer
        #constraint_jitter=20 #need integer
        #constraint_vld_id="ns_vl_2mlm" #need string
        if constraint_operacao == 1:
            payload = {
                "nsName": nsName,
                "nsdId": nsdID,
                "vimAccountId": vimAccountId,
                "wimAccountId": False,
                "placement-engine": "PLA",
            }
        if constraint_operacao == 2:
            payload = {
                "nsName": nsName,
                "nsdId": nsdID,
                "vimAccountId": vimAccountId,
                "wimAccountId": False,
                "placement-engine": "PLA",
                "placement-constraints": {"vld-constraints": [{"id": constraint_vld_id, "link-constraints": {"latency": constraint_latency} }]},
            }
        if constraint_operacao == 3:
            payload = {
                "nsName": nsName,
                "nsdId": nsdID,
                "vimAccountId": vimAccountId,
                "wimAccountId": False,
                "placement-engine": "PLA",
                "placement-constraints": {"vld-constraints": [{"id": constraint_vld_id, "link-constraints": {"jitter": constraint_jitter}}]},
            }
        if constraint_operacao == 4:
            payload = {
                "nsName": nsName,
                "nsdId": nsdID,
                "vimAccountId": vimAccountId,
                "wimAccountId": False,
                "placement-engine": "PLA",
                "placement-constraints": {"vld-constraints": [{"id": constraint_vld_id, "link-constraints": {"latency": constraint_latency, "jitter": constraint_jitter}}]},
            }

        #tratar apara ns_vl_2mlm ser resultado de uma recuperacao no nsd
        response = requests.request(method="POST", url=str(self.geturls('url_ns_instances'))+str(nsIdscheduled)+'/instantiate/', headers=headers,
                                    json=payload, verify=False)
        return response.json()


    def osm_get_vim_accounts(self,token):
        url=self.geturls('url_vim_accounts')
        payload = {}

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": 'Bearer '+str(token)
        }
        response = requests.request("GET", url, headers=headers, data=payload,verify=False)
        return response.json()

    def osm_get_nsvnf(self,token):

        url=self.geturls('url_ns_descriptors')
        url=str(url)
        payload = {}

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": 'Bearer '+str(token)
        }
        response = requests.request("GET", url, headers=headers, data=payload,verify=False)
        return response.json()


    def osm_get_nsd_id_byname(self,token,name0):
        url=self.geturls('url_ns_descriptors')
        url=str(url)
        payload = {}
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": 'Bearer '+str(token)
        }
        response = requests.request("GET", url, headers=headers, data=payload,verify=False)
        #print(response.json())
        for i in (response.json()):
            #print(type(i['name']))
            #print(type(name0))
            if i['name'] == name0:
                return i['_id']
        return "-1"

    def check_token_valid(self,token):
        #Compara unixtimestemp e se for o caso gera outro invocando o osm_create_token
        #print("Checking token")
        actual=time.time()
        #print(actual)
        to_expire=token['expires']
        #print(to_expire)
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
    def ChangeVNFPrice(self,COD_VNFD,VIMURL,PRICE,CLOUD_STATUS_DEGRADATION,COD_TEST):
        C = len(self.B[COD_VNFD]['prices']) #Elements
        #print(C)
        if COD_VNFD < 0:
            return -1  
        if (CLOUD_STATUS_DEGRADATION == 1):
            print ("PRICE BEFORE DEGRADATION_STATUS: "+ str(PRICE))
            PRICE=int(PRICE)+DOWN_UP_PRICE
            InsertActionsTests(COD_TEST,4,datetime.timestamp(datetime.now().utcnow()))
            print ("PRICE AFTER DEGRADATION_STATUS: "+ str(PRICE))
            print("Add value because is in degradation status.") 
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
                    InsertActionsTests(COD_TEST,3,datetime.timestamp(datetime.now().utcnow()))
                    return i
                else:
                    return -1
        else:
            return -1

    #Change VNF File with new Price, change the file
    def SearchChangeVNFDPrice(self,NAME_VNFD,VIM_URL,PRICE_VNFD,CLOUD_STATUS_DEGRADATION,COD_TEST):
        if debug == 1: print("In SearchChangeVNFDPrice")
        #print(NAME_VNFD+ VIM_URL + PRICE_VNFD+CLOUD_STATUS_DEGRADATION)
        if (self.ChangeVNFPrice(self.SearchVNFD(NAME_VNFD),VIM_URL,PRICE_VNFD,CLOUD_STATUS_DEGRADATION,COD_TEST)) != -1: #Change price of specific VIM in specific VNFD
            if debug == 1: print("In ChangeVNFPrice(SearchVNFD")
            with open(FILE_VNF_PRICE, 'w') as file:
                documents = yaml.dump(self.B, file, sort_keys=False) #Export changes to file without order, equal original file
            if debug == 1: print("going to copy to SearchChangeVNFDPrice ")
            #print("lembrar descomentar linha para docker fazer copia vnf")
            ExecuteCommand('docker cp '+FILE_VNF_PRICE+' '+'$(docker ps -qf name=osm_pla):/placement/')  

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
    def SearchDownUpVimPrice(self,STATUS_CPU_NOW,Cloud,fk_test):    #VIM_URL,CLOUD_COD,STATUS_CPU_NOW):
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
            #InsertActionsTests(fk_test,4,datetime.timestamp(datetime.now().utcnow()))
            nomearquivo5=PATH_LOG+'CPU_TRIGGER_'+ Cloud.getName() +'_history.txt' #write data in file
            with open(nomearquivo5, 'a') as arquivo:
                arquivo.write(DATEHOURS() + ','+ Cloud.getName() + ","+ Cloud.getIP() +","+ str(STATUS_CPU_NOW)+'\n')
            print("lembrar de descomentar")
            ExecuteCommand('docker cp '+FILE_VNF_PRICE+' '+'$(docker ps -qf name=osm_pla):/placement/')
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
    def SearchChangePriceLatencyJitterPIL(self, PRICE,LATENCY,JITTER,OPENSTACK_FROM,OPENSTACK_TO,COD_TEST):
        CLOUD_COD=self.SearchChangePILPrice(OPENSTACK_FROM,OPENSTACK_TO)
        #if debug == 1: print("CLOUD_COD: "+str(CLOUD_COD))
        #if debug == 1: print("PRICE: "+str(PRICE))
        #if debug == 1: print("PRICE: "+str(LATENCY))
        #if debug == 1: print("PRICE: "+str(JITTER))        
        #if debug == 1: print("PRICE: "+str(OPENSTACK_FROM))
        #if debug == 1: print("PRICE: "+str(OPENSTACK_TO))
        #if debug == 1: print("PRICE: "+str(COD_TEST))

        if CLOUD_COD != -1:
            if (self.ChangePriceLatencyJitterPIL(CLOUD_COD,PRICE,LATENCY,JITTER)) != -1: #Change Price Latency and Jitter
                with open(FILE_PIL_PRICE, 'w') as file:
                    documents = yaml.dump(self.B, file, sort_keys=False) #Export changes to file without order, equal original file
                InsertActionsTests(COD_TEST,2,datetime.timestamp(datetime.now().utcnow()))
                #print("lembrar descomentar linha para docker fazer copia pil")
                ExecuteCommand('docker cp '+FILE_PIL_PRICE+' '+'$(docker ps -qf name=osm_pla):/placement/')
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
        if debug == 1: print ("entrei dentro de ChangePriceLatencyJitterPIL")
        if debug == 1: print(PRICE)
        if debug == 1: print(LATENCY)
        if debug == 1: print(JITTER)
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
        #print("horarioInicio: "+str(START))
        #print("hoarioFinal: "+str(STOP))
        Latencia_to_cloud2=cloud1_gnocchi.get_last_measure("Lat_To_"+cloud2.getExternalIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)
        #print("LatenciatoCloud2: "+str(Latencia_to_cloud2))
        Jitter_to_cloud2=cloud1_gnocchi.get_last_measure("Jit_To_"+cloud2.getExternalIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)
        #print("JittertoCloud2: "+str(Jitter_to_cloud2))
        PILFile.SearchChangePriceLatencyJitterPIL(Latencia_to_cloud2,Latencia_to_cloud2,Jitter_to_cloud2,CLOUD_FROM,CLOUD_TO,0)
        time.sleep(5)

#Collect CPU in PLAO Server
def Collector_CPU_PLAO_Server(tempo_coleta,id_test):
    #comando: 1 start / 0 stop
    #tempo_coleta: 1.0 / 5.0
    #TEST_ID
    dt_obj = datetime.utcnow()  # input datetime object
    unixstime=int(float(dt_obj.strftime('%s.%f')) * 1e3)
    GRANULARITY=tempo_coleta
    COD_DATA_TYPE=1 #CPU
    COD_CLOUD=3
    while True:
        cpuso = psutil.cpu_percent(interval=1)
        cpuso2 = round(cpuso)
        #print("cpu")
        #print(cpuso2)
        InsertDataTests(unixstime,id_test,cpuso2,GRANULARITY,COD_DATA_TYPE,COD_CLOUD)
        if (COMMAND_MON_PLAO == 0):
            break
        time.sleep(tempo_coleta)

#Collect Memory in PLAO Server
def Collector_Memory_PLAO_Server(tempo_coleta,id_test):
    #comando: 1 start / 0 stop
    #tempo_coleta: 1.0 / 5.0
    #TEST_ID
    dt_obj = datetime.utcnow()  # input datetime object
    unixstime=int(float(dt_obj.strftime('%s.%f')) * 1e3)
    GRANULARITY=tempo_coleta
    COD_DATA_TYPE=4 #MEMORY
    COD_CLOUD=3
    while True:
        mem = psutil.virtual_memory()
        memoryso = round(mem.percent)
        #print("memory")
        #print(memoryso)
        InsertDataTests(unixstime,id_test,memoryso,GRANULARITY,COD_DATA_TYPE,COD_CLOUD)
        if (COMMAND_MON_PLAO == 0):
            break
        time.sleep(tempo_coleta)

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
        return cloud1_gnocchi.get_last_measure_Date(metric_name,cloud1_resource_id,None,GRANULARITY,START,STOP,1,1,1)
    if cloud == "2":
        print ("passei cloud 2")
        return cloud2_gnocchi.get_last_measure_Date(metric_name,cloud2_resource_id,None,GRANULARITY,START,STOP,1,1,1)


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
    TestUsers=Users.get_or_none(Users.username_user==username0)
    if TestUsers is None:
        return Users.insert(
            name_user = name0,
            username_user = username0,
            password_user = password0,
            creation_date_user = datetime.now()
        ).execute()
    else:
        -1

def InsertMethods(name):
    return Methods.insert(
        name_methods = name
    ).execute()

def InsertDataTestsTypes(name):
    return Data_Tests_Types.insert(
        name_data_tests = name
    ).execute()

def InsertDataTests(date, id_test, value, granularity, id_data_test_type, id_cloud ):
    return Data_Tests.insert(
        date_data_tests = date,
        fk_tests = id_test,
        value_data_tests = value,
        granularity_data_tests = granularity,
        fk_data_tests_types = id_data_test_type,
        fk_cloud = id_cloud
    ).execute()

    id_data_tests=BigIntegerField( unique=True, primary_key=True,
            constraints=[SQL('AUTO_INCREMENT')])
    granularity_data_tests = CharField(max_length=100)



def InsertTests(desc):
    return Tests.insert(
        description = desc,
        start_date_test = datetime.timestamp(datetime.now().utcnow())
    ).execute()

def InsertActionsTestsTypes(name_test_type):
    return Actions_Tests_Types.insert(
        name_action_test_type = name_test_type
    ).execute()

def InsertActionsTests(id_fk_test,cod_test_type,date_actions_tests):
    return Actions_Tests.insert(
        date_actions_tests = date_actions_tests,
        fk_tests = id_fk_test,
        fk_actions_tests_types = cod_test_type
    ).execute()

def InsertTestsMethods(cod_test,cod_method,cod_cloud):
    return Tests_Methods.insert(
        start_date_test_methods = datetime.timestamp(datetime.now().utcnow()),
        fk_tests = cod_test,
        fk_methods=cod_method,
        fk_clouds=cod_cloud
    ).execute()

def InsertDegradationVnfType(nametype):
    return Degradations_Vnfs_Clouds_Types.insert(
        creation_date_degradations_vnfs_clouds_types=datetime.now(),
        name_degradations_vnfs_clouds_types = nametype
    ).execute()


def UpdateFinishTestsMethods(cod_method_test):
    return Tests_Methods.update(finish_date_test_methods=datetime.timestamp(datetime.now().utcnow())).where(Tests_Methods.id_tests_methods==cod_method_test).execute()
    #print(datetime.timestamp(datetime.now().utcnow()))
    #time.sleep(2)
    #return timetestmethod

def UpdateFinishTestsMethodsifNone(cod_method_test):
    return Tests_Methods.update(finish_date_test_methods=datetime.timestamp(datetime.now().utcnow())).where((Tests_Methods.id_tests_methods==cod_method_test)&(Tests_Methods.finish_date_test_methods=="")).execute()
    #print(datetime.timestamp(datetime.now().utcnow()))
    #time.sleep(2)
    #return timetestmethod

def UpdateFinishDateTestsbyId(id):
    return Tests.update(finish_date_test=datetime.timestamp(datetime.now().utcnow())).where(Tests.id_tests==id).execute()
    #print(datetime.timestamp(datetime.now().utcnow()))
    #time.sleep(2)
    #return timetest

def SelectTestbyId(id):
    return (Tests.select(Tests.start_date_test,Tests.finish_date_test)
    .where(Tests.id_tests==id).dicts().get())

#def UpdateFinishTestsMethods(cod_method_test):
#    return Tests_Methods.update(finish_date_test_methods=datetime.now().utcnow()).where(Tests_Methods.id_tests_methods==cod_method_test).execute()

#def UpdateFinishDateTestsbyId(id):
#    return Tests.update(finish_date_test=datetime.now().utcnow()).where(Tests.id_tests==id).execute()

def InsertJob(userip0, nsd_name0,cod_fkuser,cod_status, cod_test):
    return Jobs.insert(
        userip_job = userip0,
        start_date_job = datetime.now(),
        nsd_name_job=nsd_name0,
        fk_user = cod_fkuser,
        fk_status = cod_status,
        fk_tests = cod_test
    ).execute()

def UpdateJob(job_id, job_status):
    Jobs.update(fk_status = job_status,finish_date_job = datetime.now().utcnow()).where(Jobs.id_job==job_id).execute()
    return "ExecutedUpdate"

def insertJobVnfCloud(cost_vnf,id_fk_job,id_fk_vnf,id_fk_cloud,vnf_threshold,vnf_threshold_type,degradation_monitoring_value):
    return Jobs_Vnfs_Clouds.insert(
        cost = cost_vnf,
        fk_job = id_fk_job,
        fk_vnf = id_fk_vnf,
        fk_cloud = id_fk_cloud,
        degradation_threshold_jobs_vnfs_clouds = vnf_threshold,
        fk_degradation_vnfs_clouds_types = vnf_threshold_type,
        degradation_monitoring_value_now_jobs_vnfs_clouds = degradation_monitoring_value,
        creation_date = datetime.now()
    ).execute()

def InsertStatusNsInstanced(name):
    return Status_NS_Instanciateds.insert(
        name_osm_status_ns_instanciated = name,
        creation_date_status_ns_instanciated = datetime.now()
    ).execute()  

def InsertNsInstanciated(name0,id_osm0,id_status0,id_job0):
    return NS_Instanciateds.insert(
        name_ns_instanciated = name0,
        id_osm_ns_instanciated = id_osm0,
        fk_status = id_status0,
        fk_job = id_job0,
        creation_date_ns_instanciated = datetime.now()
    ).execute()

def UpdateNsInstanciated(id_osm0,id_status0,id_job0):
    NS_Instanciateds.update(fk_status = id_status0,finish_date_ns_instanciated=datetime.now().utcnow()).where((NS_Instanciateds.id_osm_ns_instanciated == id_osm0)&(NS_Instanciateds.fk_job==id_job0)).execute()
    return "ExecutedUpdate"

def InsertStatusVnfInstanced(name):
    return Status_Vnf_Instanciateds.insert(
        name_osm_status_vnf_instanciated = name,
        creation_date_status_vnf_instanciated = datetime.now()
    ).execute()  

def InsertVnfInstanciated(id_osm0,name_osm,id_fk_cloud,id_status,id_ns_instanciated):
    return Vnf_Instanciateds.insert(
        id_osm_vnf_instanciated = id_osm0,
        name_osm_vnf_instanciated = name_osm,
        fk_cloud = id_fk_cloud,
        fk_status = id_status,
        fk_ns_instanciated = id_ns_instanciated,
        creation_date_vnf_instanciated = datetime.now()
    ).execute()

def SelectVnfInstanciated(cod):
    return (Vnf_Instanciateds.select()
    .join(Status_Vnf_Instanciateds)
    .where((Vnf_Instanciateds.id_osm_vnf_instanciated==cod)&(NS_Instanciateds.fk_status==Status_NS_Instanciateds.id_status_vnf_instanciated)).dicts().get())

def SelectNsInstanciated(cod):
    return (NS_Instanciateds.select()
    .join(Status_NS_Instanciateds)
    .where((NS_Instanciateds.id_osm_ns_instanciated==cod)&(Vnf_Instanciateds.fk_status==Status_Vnf_Instanciateds.id_status)).dicts().get())

def SelectTests():
    result = (Tests.select(
        Tests.id_tests,
        Tests.start_date_test,
        Tests.finish_date_test,
        Tests.description,
        Tests_Methods.id_tests_methods,
        Tests_Methods.start_date_test_methods,
        Tests_Methods.finish_date_test_methods,
        Tests_Methods.fk_tests,
        Tests_Methods.fk_methods,
        Methods.id_methods,
        Methods.name_methods,
        #fn.AVG(Tests.finish_date_test-Tests.start_date_test).alias('diftimeTest'),
        #fn.AVG(Tests_Methods.finish_date_test_methods-Tests_Methods.start_date_test_methods).alias('diftimeMethod')
    )
    .join(Tests_Methods)
    .join(Methods)
    #.group_by(Tests.id_tests,Methods.id_methods)
    .dicts())
    print(result)
    df = pd.DataFrame(result)
    #df['start_date_test']=df['start_date_test'].astype(float)
    #df['finish_date_test']=df['finish_date_test'].astype(float)
    #df['diftimeTest']=df['finish_date_test']-df['start_date_test']

    #df['start_date_test_methods']=df['start_date_test_methods'].astype(float)
    #df['finish_date_test_methods']=df['finish_date_test_methods'].astype(float)
    #df['diftimeMethod']=df['finish_date_test_methods']-df['start_date_test_methods']

    #print(df.groupby(['id_methods','name_methods']).mean())
    #df2=df.groupby(['id_methods']).mean()

    #print(df['start_date_test'].sum())
    #print(df)
    #print(df2)
    df.to_csv("coleta2/teste.csv", index=False)
    #df2.to_excel("coleta2teste2.xlsx", index=False)
    return 1

def SelectNsjoinVNFInstanciated(cod):
    return (Jobs.select(
                                    Jobs.id_job,
                                    Jobs.fk_user,
                                    NS_Instanciateds.name_ns_instanciated,
                                    NS_Instanciateds.id_osm_ns_instanciated,
                                    NS_Instanciateds.creation_date_ns_instanciated,
                                    NS_Instanciateds.fk_status,
                                    #Status_NS_Instanciateds.name_osm_status_ns_instanciated,
                                    Vnf_Instanciateds.id_osm_vnf_instanciated,
                                    Vnf_Instanciateds.name_osm_vnf_instanciated,
                                    Vnf_Instanciateds.creation_date_vnf_instanciated,
                                    Vnf_Instanciateds.fk_status,
                                    Vnf_Instanciateds.fk_cloud,
                                    Clouds.name,
                                    Clouds.id_cloud,
                                    Clouds.external_ip
                                    #Status_NS_Instanciateds.name_osm_status_ns_instanciated
                                    )
    .join(NS_Instanciateds)
    .join(Vnf_Instanciateds)  
    #.join(Status_Vnf_Instanciateds) 
    #.join(Status_NS_Instanciateds)
    .join(Clouds)                            
    .dicts())

def updateCostJobVnfCloud(id_jobs_vnf_cloud0, cost_vnf):
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

def getVnfStatusDegradation(id_job_vnf):
    THRESHOLD=Jobs_Vnfs_Clouds.select(Jobs_Vnfs_Clouds.degradation_threshold_jobs_vnfs_clouds).where(Jobs_Vnfs_Clouds.id_jobs_vnf_cloud==id_job_vnf)
    THRESHOLD2=0
    VALUE2=0
    
    for row in THRESHOLD:
        THRESHOLD2=row.degradation_threshold_jobs_vnfs_clouds
    
    VALUE=Jobs_Vnfs_Clouds.select(Jobs_Vnfs_Clouds.degradation_monitoring_value_now_jobs_vnfs_clouds).where(Jobs_Vnfs_Clouds.id_jobs_vnf_cloud==id_job_vnf) 
    for row2 in VALUE:
        VALUE2=row2.degradation_monitoring_value_now_jobs_vnfs_clouds

    print(" value")
    print (VALUE2)
    print (" mais detalhes")
    print(THRESHOLD2)
    if VALUE2 > THRESHOLD2:
        print (" esta degradado ")
        return 1
    else:
        print (" nao esta degradado ")
        return 0

def InsertCloud(name0, ip0, external_ip0,cod_degradation_cloud_type,threshold_value,vim_id_osm0):
    TestCloud=Clouds.get_or_none(Clouds.name==name0)
    if TestCloud is None:
        return Clouds.insert(
            name=name0,
            ip=ip0,
            external_ip=external_ip0,
            fk_degradation_cloud_type = cod_degradation_cloud_type,
            threshold_degradation = threshold_value,
            vim_id_osm = vim_id_osm0,
            creation_date=datetime.now()
        ).execute()
    else:
        return -1

def GetIdCloud(name_cloud):
    cloud=Clouds.select(Clouds.id_cloud).where(Clouds.name==name_cloud)
    for row in cloud:
        return str(row.id_cloud)
    return "-1"

def GetIdCloudbyvimidosm(vim_id_osm0):
    cloud=Clouds.select(Clouds.id_cloud).where(Clouds.vim_id_osm==vim_id_osm0)
    for row in cloud:
        return str(row.id_cloud)
    return "-1"

def insertMetric(name_metric):
    TestMetric=Metrics.get_or_none(Metrics.name==name_metric)
    if TestMetric is None:
        return Metrics.insert(
            name = name_metric,
            creation_date = datetime.now()
        ).execute()
    else:
        return GetIdMetric(name_metric)

def insertMetricCloud(fk_cloud0, fk_metric0):
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

def insertMetricsVnf(metric_data, weight0,  cod_metric,cod_job_vnf_cloud):
    return Metrics_Vnfs.insert(
        metric_value = metric_data,
        weight = weight0,
        #fk_vnf = cod_vnf,
        fk_metric = cod_metric,
        fk_job_vnf_cloud = cod_job_vnf_cloud,
        creation_date = datetime.now()
    ).execute()

def GetMetricsVnf(metric_vnf_id):
    #print("metric vnf id:")
    #print(metric_vnf_id)
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
        name_status_jobs = nameStatus,
        creation_date_status_jobs = datetime.now()
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

def FirstLoadBD():
    print("Iniciando carga BD.")
    #PreLoadDefault
    InsertMethods("insertJob()")
    InsertMethods("userLatency()")
    InsertMethods("getLastMeasureClouds()")
    InsertMethods("insertMetric()")
    InsertMethods("insertMetricCloud()")
    InsertMethods("insertJobVnfCloud()")
    InsertMethods("insertMetricsVnf()")
    InsertMethods("getMetricsVnfApplyWeight()")
    InsertMethods("updateCostJobVnfCloud()")
    InsertMethods("getVnfStatusDegradation()")
    #InsertMethods("SetProcessModel()")
    InsertMethods("configVNFsCostsOSM()")
    InsertMethods("createNSInstanceOSM()")
    InsertActionsTestsTypes("Start Instanciação de NS.")
    InsertActionsTestsTypes("Alteração do custo do link, considerando latência e jitter entre nuvens.")
    InsertActionsTestsTypes("Alteração do custo das VNFDs de acordo com a latência para o usuário final e percentual de uso de CPU da nuvem.")
    InsertActionsTestsTypes("Aumento dos custos de todos os VNFDs da nuvem após degradação do uso de CPU.")
    InsertActionsTestsTypes("Finish Instanciação de NS.")
    InsertActionsTestsTypes("Finish Instanciação de VNF Cloud 1.")
    InsertActionsTestsTypes("Finish Instanciação de VNF Cloud 2.")
    InsertDegradationVnfType("CPU")
    InsertDegradationVnfType("Memoria")
    InsertDegradationsCloudsTypes("CPU")
    InsertDegradationsCloudsTypes("Memoria")
    InsertCloud("Serra","10.50.0.159","200.137.75.160",1,90,"9f104eee-5470-4e23-a8dd-3f64a53aa547")
    InsertCloud("Aracruz","172.16.112.60","200.137.82.21",2,91,"6ba02d24-6320-4322-9177-eb4987ad9465")
    InsertCloud("PLAOServerOSM","127.0.0.1","127.0.0.1",2,91,"0")
    InsertDegradations_Clouds(1,1,98)
    InsertDataTestsTypes("CPU1")
    InsertDataTestsTypes("CPU2")
    InsertDataTestsTypes("NVNF")
    InsertDataTestsTypes("Memoria")
    InsertDataTestsTypes("Latencia_Serra_to_Aracruz")
    InsertDataTestsTypes("Jitter_Serra_to_Aracruz")
    InsertDataTestsTypes("Latencia_Aracruz_to_Serra")
    InsertDataTestsTypes("Jitter_Aracruz_to_Serra")
    InsertDataTestsTypes("Latencia_Serra_to_User_Test")
    InsertDataTestsTypes("Latencia_Aracruz_to_User_Test")
    InsertVnf("VNFA")
    InsertVnf("VNFB")
    InsertStatusJobs("Started")
    InsertStatusJobs("Finished")
    InsertStatusJobs("Running")
    InsertUser("Jose Carlos","jcarlos","abc")
    InsertUser("Amarildo de Jesus","ajesus","abcd")
    #UsingSystem
    #Insert Job with User IP, name NS, cod administrator user and cod job status
    #job_cod_uuid=uuid.uuid4()
    #print (str(job_cod_uuid))
    ##########InsertJob("10.0.19.148","teste_mestrado",1,1)
    #Insert Jo
    ############JOBVNFCLOUD=InsertJobVnfCloud(20,1,1,1)
    ###########print (JOBVNFCLOUD)
    insertMetric("Lat_to_8.8.8.8")  ###proximos a comentar, verificar
    insertMetric("Lat_to_1.1.1.1")   #proximos a comentar, verificar 
    insertMetricCloud(1,1)
    ###########InsertMetricsVnf(20,8,1,JOBVNFCLOUD)
    InsertStatusNsInstanced('BUILDING')
    InsertStatusNsInstanced('READY')
    InsertStatusNsInstanced('DELETED')
    InsertStatusVnfInstanced('INSTANTIATED')
    InsertStatusVnfInstanced('DELETED')

def main():
    print ("Iniciando Server PLAO")
    VNFFile = File_VNF_Price()
    PILFile = File_PIL_Price()

    #IP_OSM="10.159.205.10"
    #IP_OSM="200.137.82.24"
    IP_OSM="127.0.0.1"
    OSM = OSM_Auth(IP_OSM)
    token=OSM.osm_create_token()

    servers = Servers()
    print("Loading Cloud Class with Clouds")
    cloud1 = Cloud(servers.getbyIndexIP(0),servers.getbyIndexExternalIP(0))   
    cloud1.setName(servers.getServerName(cloud1.getIp()))
    print(cloud1.getName())
    cloud1.setVimURL("https://200.137.75.159:5000/v3")
    print(cloud1.getIp())
    print(cloud1.getVimURL())
    print(cloud1.getName())       
    print(cloud1.getCpu())

    cloud2 = Cloud(servers.getbyIndexIP(1),servers.getbyIndexExternalIP(1))
    cloud2.setName(servers.getServerName(cloud2.getIp()))
    #cloud2.setVimURL("http://200.137.82.21:5000/v3")
    cloud2.setVimURL("http://200.137.75.159:5000/v3")
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
        cloud1_resource_ids_nova=cloud1_gnocchi.get_resource_ids("nova_compute")
        cloud1.setStatus(1)

    except:
        print ("Problema ao acessar Cloud 1!!!")
        cloud1_resource_id=""
        cloud1_resource_ids_nova=""
        cloud1.setStatus(0)
    
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
        cloud2_resource_ids_nova=cloud2_gnocchi.get_resource_ids("nova_compute")
        cloud2.setStatus(1)
    except:
        print ("Problema ao acessar Cloud 2!!!")
        cloud2_resource_id=""
        cloud2_resource_ids_nova=""
        cloud1.setStatus(0)
        
    #File in Clouds
    app = Flask(__name__)

    # The payload is the user ip address.
    #nuvem1="10.159.205.11"
    nuvem1="200.137.75.159"
    #nuvem2="10.159.205.8"
    #nuvem2="200.137.82.21"
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


    @app.route('/uplatencylink/',methods=['POST'])
    def uplatency2():
        if request.method == "POST":

            request_data = request.get_json()
            INCREASE = request_data['INCREASE']
            payload = {"INCREASE" : str(INCREASE)}            
            try:
                requests.request(
                    method="POST", url='http://'+nuvem1+':3333/uplatencylink/', json=payload)

            except requests.ConnectionError:
                print("OOPS!! Connection Error. Make sure you are connected to Internet.\n")           
            except requests.Timeout:
                print("OOPS!! Timeout Error")
            except requests.RequestException:
                print("OOPS!! General Error")
            except KeyboardInterrupt:
                print("Someone closed the program")

            try:
                requests.request(
                    method="POST", url='http://'+nuvem2+':3333/uplatencylink/', json=payload)

            except requests.ConnectionError:
                print("OOPS!! Connection Error. Make sure you are connected to Internet.\n")
                return ""            
            except requests.Timeout:
                print("OOPS!! Timeout Error")
            except requests.RequestException:
                print("OOPS!! General Error")
            except KeyboardInterrupt:
                print("Someone closed the program")
            else:
                return "Started"


    @app.route('/uplatencytouser/',methods=['POST'])
    def uplatencytouser():
        if request.method == "POST":

            request_data = request.get_json()
            IPCLOUD = request_data['IPCLOUD']
            IPUSERTEST = request_data['IPUSERTEST']
            INCREASE = request_data['INCREASE']

            payload = {"IPCLOUD" : str(IPCLOUD),"IPUSERTEST" : str(IPUSERTEST),"INCREASE" : str(INCREASE)}            
            try:
                requests.request(
                    method="POST", url='http://'+nuvem1+':3333/uplatencytouser/', json=payload)

            except requests.ConnectionError:
                print("OOPS!! Connection Error. Make sure you are connected to Internet.\n")           
            except requests.Timeout:
                print("OOPS!! Timeout Error")
            except requests.RequestException:
                print("OOPS!! General Error")
            except KeyboardInterrupt:
                print("Someone closed the program")

            try:
                requests.request(
                    method="POST", url='http://'+nuvem2+':3333/uplatencytouser/', json=payload)

            except requests.ConnectionError:
                print("OOPS!! Connection Error. Make sure you are connected to Internet.\n")
                return ""            
            except requests.Timeout:
                print("OOPS!! Timeout Error")
            except requests.RequestException:
                print("OOPS!! General Error")
            except KeyboardInterrupt:
                print("Someone closed the program")
            else:
                return "Started"



    #Start aplication in server and clients, and start Thread of collector links metrics.
    @app.route('/resetlatency/',methods=['POST'])
    def resetlatency2():
        if request.method == "POST":

            #request_data = request.get_json()
            #payload = request_data['ipuser']
            
            try:
                requests.request(
                    method="POST", url='http://'+nuvem1+':3333/resetlatency/')#, json=payload)

            except requests.ConnectionError:
                print("OOPS!! Connection Error. Make sure you are connected to Internet.\n")           
            except requests.Timeout:
                print("OOPS!! Timeout Error")
            except requests.RequestException:
                print("OOPS!! General Error")
            except KeyboardInterrupt:
                print("Someone closed the program")

            try:
                requests.request(
                    method="POST", url='http://'+nuvem2+':3333/resetlatency/')#, json=payload)

            except requests.ConnectionError:
                print("OOPS!! Connection Error. Make sure you are connected to Internet.\n")
                return ""            
            except requests.Timeout:
                print("OOPS!! Timeout Error")
            except requests.RequestException:
                print("OOPS!! General Error")
            except KeyboardInterrupt:
                print("Someone closed the program")
            else:
                return "Started"


    #Load BD after to create BD
    @app.route('/firstloadbd/',methods=['POST'])
    def cargabd():
        FirstLoadBD()
        return "LoadedBase"

    #Load BD after to create BD
    @app.route('/stopcoletaplao/',methods=['POST'])
    def stopcoletaplao():
        COMMAND_MON_PLAO=0
        return "StopColetaPlao"

    #Load BD after to create BD
    @app.route('/startcoletaplao/',methods=['POST'])
    def startcoletaplao():
        
        return "StopColetaPlao"

    #Load BD after to create BD
    @app.route('/selecttestes/',methods=['GET'])
    def selecttests():
        SelectTests()
        return "SelectTests"

    @app.route('/deletevims/',methods=['GET'])
    def getvims():
        OSM.check_token_valid(token)
        OSM.osm_delete_vim(token['id'],"59ea6654-25f4-4196-a362-9745498721e1")
        return "ok"

    @app.route('/getOSMlistvim/',methods=['GET'])
    def OSMlistvim():
        OSM.check_token_valid(token)
        print(OSM.osm_get_vim_accounts(token['id']))
        return "ok"


    @app.route('/getvnf3/',methods=['GET'])
    def OSMgetvnf3():
        OSM.check_token_valid(token)
        for i in OSM.osm_get_instance_vnf(token['id']):
            print (i)
        return "ok"

    @app.route('/getns/',methods=['GET'])
    def OSMgetns():
        OSM.check_token_valid(token)
        #id_ns_scheduled=(OSM.osm_create_instance_ns((token['id']),"teste_metrado_plao","de0bf24c-a3b4-4b7f-9066-61b4cb90f883","9f104eee-5470-4e23-a8dd-3f64a53aa547"))
        #OSM.osm_create_instance_ns_scheduled((token['id']),"teste_metrado_plao",str(id_ns_scheduled['id']),"9f104eee-5470-4e23-a8dd-3f64a53aa547")
        for i in OSM.osm_get_instance_ns(token['id']):
            print (i['_id'])
            print (i)
            #OSM.osm_delete_instance_ns(token['id'],i['_id'])
        return "ok"

    #Delete rows in database
    @app.route('/deleteallbdns/',methods=['POST'])
    def OSMdeleteallbdns():
        OSM.check_token_valid(token)
        for i in OSM.osm_get_instance_ns(token['id']):
            OSM.osm_delete_instance_ns(token['id'],i['_id'])
            Vnf_Instanciateds.delete().execute()
            NS_Instanciateds.delete().execute()
            return "DeletedAll"
        return "-1"

    #Change de status to deleted, but not delete the row
    @app.route('/deleteallns/',methods=['POST'])
    def OSMdeleteallns():
        OSM.check_token_valid(token)
        for i in OSM.osm_get_instance_ns(token['id']):
            OSM.osm_delete_instance_ns(token['id'],i['_id'])
            Vnf_Instanciateds.update(fk_status=2).where(Vnf_Instanciateds.fk_ns_instanciated==i['_id']).execute()
            NS_Instanciateds.update(fk_status=3).where(NS_Instanciateds.id_osm_ns_instanciated==i['_id']).execute()
            return "DeletedAll"
        return "-1"

    @app.route('/setns/',methods=['POST'])
    def OSMsetns():
        OSM.check_token_valid(token)
        #coletarNSid
        #coletarNSVIM_1
        #Falta inserir constraint PLA no ns scheduled, e tb restricao de jitter e latencia
        id_ns_scheduled=(OSM.osm_create_instance_ns((token['id']),"teste_metrado_plao","de0bf24c-a3b4-4b7f-9066-61b4cb90f883","9f104eee-5470-4e23-a8dd-3f64a53aa547"))
        OSM.osm_create_instance_ns_scheduled((token['id']),"teste_metrado_plao",str(id_ns_scheduled['id']),"9f104eee-5470-4e23-a8dd-3f64a53aa547")
        return "ok"

    @app.route('/getnsbyid/',methods=['GET'])
    def OSMsetns2():
        OSM.check_token_valid(token)
        id_ns_scheduled="fe97314c-df28-4477-8b23-97f7778ebdc6"
        return OSM.osm_get_instance_ns_byid(token['id'],id_ns_scheduled)['nsState']

    @app.route('/getnsbd/',methods=['GET'])
    def OSMgetnsbd():
        OSM.check_token_valid(token)
        id_ns_scheduled="fe97314c-df28-4477-8b23-97f7778ebdc6"
        for i in SelectNsjoinVNFInstanciated(id_ns_scheduled):
            print (i)
        return 'ok'

    #Get NS Join VNF Instanciated All
    @app.route('/getnsjoinvnfall/',methods=['GET'])
    def OSMgetvnf2():
        OSM.check_token_valid(token)
        id_ns_scheduled="fe97314c-df28-4477-8b23-97f7778ebdc6"
        LIST=(SelectNsjoinVNFInstanciated(id_ns_scheduled))
        df = pd.DataFrame(LIST)
        if (df.__len__() == 0):
            return -1
        df2=json.dumps(json.loads(df.to_json(orient = 'records')), indent=2)
        return df2

    #Mark wifh flag Delete specific ns instanciated
    @app.route('/deletensinstanciated/',methods=['POST'])
    ########################Falta coletar informacao com id e usar no metodo
    def OSMdeletensbyjob():
        OSM.check_token_valid(token)
        ID_JOB=1
        ID_NS_INSTANCIATED=NS_Instanciateds.select(NS_Instanciateds.id_osm_ns_instanciated).where(NS_Instanciateds.fk_job==ID_JOB)
        OSM.osm_delete_instance_ns((token['id']),ID_NS_INSTANCIATED)
        Vnf_Instanciateds.update(Vnf_Instanciatedsfk_status=2).where(Vnf_Instanciateds.fk_ns_instanciated==ID_NS_INSTANCIATED).execute()
        NS_Instanciateds.update(fk_status=3).where(NS_Instanciateds.id_osm_ns_instanciated==ID_NS_INSTANCIATED).execute()
        #Mark in bd deleted vnf and ns instanciateds
        return "ok"

    #Return token for user
    #Return resultado de check token user
    #Inserir em todas as rotas um check do usuario e seu respectivo token

    @app.route('/selectidtest/',methods=['GET'])
    def SelectIdTests():
        test=SelectTestbyId(2)
        print(test)
        print (test.get('start_date_test'))
        print (test.get('finish_date_test'))       
        return "ok"

    #Return NS packages and VNFS pakages of OSMs
    @app.route('/listnsvnfpackage/',methods=['GET'])
    def OSMlistNSVNF():
        OSM.check_token_valid(token)
        listnsvnf=OSM.osm_get_nsvnf(token['id'])
        VNFDLISTSUM={}
        for i in (listnsvnf):
            ID=i['id']
            VNFDLIST=[]
            
            VLD=(i['vld'])
            for i in VLD:
                VNFD=(i['vnfd-connection-point-ref'])
                for i in VNFD:
                    NEWVNFD=i['vnfd-id-ref']
                    if (not VNFDLIST.__contains__(NEWVNFD)):
                        VNFDLIST.append(i['vnfd-id-ref'])
            VNFDLISTSUM.update({ID:VNFDLIST})
        return (json.dumps(VNFDLISTSUM, indent=2))

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

            #cloud1_resource_id_nova=cloud1_gnocchi.get_resource_id("nova_compute")
            #if cloud1_resource_id_nova != -1:
            #    print("Starting Thread to monitor last cpu in Cloud 1")
            #    thread_MonitorDisaggregated1 = threading.Thread(target=Collector_Metrics_Disaggregated_cl1,args=(cloud1_gnocchi,cloud1_resource_id_nova,cloud1,VNFFile))
            #    thread_MonitorDisaggregated1.start()
            #else:
            #    print("Resource nova_compute not exist, need to create.")
            #print ("resource_id+cloud1: "+str(cloud1_resource_id_nova))

            #cloud2_resource_id_nova=cloud2_gnocchi.get_resource_id("nova_compute")
            #if cloud2_resource_id_nova != -1:
            #    print("Starting Thread to monitor last cpu in Cloud 2")
            #    thread_MonitorDisaggregated2 = threading.Thread(target=Collector_Metrics_Disaggregated_cl1,args=(cloud2_gnocchi,cloud2_resource_id_nova,cloud2,VNFFile))
            #    thread_MonitorDisaggregated2.start() 
            #else:
            #    print("Resource nova_compute not exist, need to create.")
            #print ("resource_id_cloud2: "+str(cloud2_resource_id_nova))
       
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
        if request.method == "GET":
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

    @app.route('/selecttest/',methods=['GET'])
    def selectsest():
        if request.method == "GET":


            now=datetime.now()
            intervalo=600
            delta = timedelta(seconds=intervalo)
            #deltagm= timedelta(seconds=10600)
            time_past=now-delta
            START=time_past
            STOP=now
            GRANULARITY=60
            print (cloud1_gnocchi)
            Latencia_to_cloud2=cloud1_gnocchi.get_last_measure("Lat_To_"+cloud2.getExternalIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)
            print("LatenciatoCloud2: "+str(Latencia_to_cloud2))
            Jitter_to_cloud2=cloud1_gnocchi.get_last_measure("Jit_To_"+cloud2.getExternalIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)
            print("JittertoCloud2: "+str(Jitter_to_cloud2))

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
            global COMMAND_MON_PLAO
            COMMAND_MON_PLAO=1

            OSM.check_token_valid(token)

            TEST_ID=InsertTests("Teste_send_job")

            CriaThreadColetaCPU_Memoria(1.0,TEST_ID)

            ret_status = 0 #status of return cloud
            request_data = request.get_json()
            IP_USER=request_data['ipuser']
            NSD_NAME="teste_mestrado" #['nsdname']#a interface vai enviar depois de receber lista
            NS_NAME_INSTANCIATED="ns_name-username"  #['nsname'] #sugiro ser NS_User_namex
            COD_USER=1 #request_data['coduser'] #Criar funcao para validar usuario no futuro
            METRIC1_NAME="Lat_To_"+IP_USER #request_data['metric1name']
            METRIC2_NAME="CPU" #request_data['metric2name']
            if METRIC2_NAME=="CPU":
                METRIC2_NAME="compute.node.cpu.percent"
            VNF1_NAME="VNFA" #request_data['vnf1name']
            VNF2_NAME="VNFB" #request_data['vnf2name']   
            NAME_CLOUD1="Serra" #request_data['cloudname1']
            NAME_CLOUD2="Aracruz" #request_data['cloudname2']
            WEIGHT_METRIC1_VNF1=0.7 #['weight_metric1_vnf1']
            WEIGHT_METRIC2_VNF1=0.3 #['weight_metric2_vnf1']
            WEIGHT_METRIC1_VNF2=0.1 #['weight_metric1_vnf2']
            WEIGHT_METRIC2_VNF2=0.9 #['weight_metric2_vnf2']
            COD_STATUS_JOB=1 #(1-Started,2-Finish)
            VIMACCOUNTID="9f104eee-5470-4e23-a8dd-3f64a53aa547"#fixo por enquanto
            CONSTRAINT_OPERACAO=int(request_data['constraint_operation'])
            #print(CONSTRAINT_OPERACAO)
            CONSTRAINT_LATENCY=2 #['constraint_latency']
            CONSTRAINT_JITTER=20 #['constraint_jitter']
            CONSTRAINT_VLD_ID="ns_vl_2mlm" #['constraint_vld_id']
            #['threshold_metric_cloud']
            #['threshold_cloud']
            DEGRADATION_THRESHOLD_VNF1=70 #['degradation_threshold_vnf1']
            DEGRADATION_THRESHOLD_TYPE_VNF1=1 #['degradation_threshold_type_vnf1']
            DEGRADATION_THRESHOLD_VNF2=70 #['degradation_threshold_vnf2']
            DEGRADATION_THRESHOLD_TYPE_VNF2=1 #['degradation_threshold_type_vnf2']
            DEGRADATION_VNF1_METRIC_NAME="compute.node.cpu.percent"
            DEGRADATION_VNF2_METRIC_NAME="compute.node.cpu.percent"

            METHOD_1_CL1=InsertTestsMethods(TEST_ID,1,1)
            METHOD_1_CL2=InsertTestsMethods(TEST_ID,1,2)
            JOB_COD=InsertJob(IP_USER,NSD_NAME,COD_USER,COD_STATUS_JOB,TEST_ID)
            UpdateFinishTestsMethods(METHOD_1_CL1)
            UpdateFinishTestsMethods(METHOD_1_CL2)

            METHOD_2_CL1=InsertTestsMethods(TEST_ID,2,1)
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
                cloud1.setStatus(0)          
            except requests.Timeout:
                print("OOPS!! Timeout Error")
                cloud1.setStatus(0)  
            except requests.RequestException:
                print("OOPS!! General Error")
                cloud1.setStatus(0)  
            except KeyboardInterrupt:
                print("Someone closed the program")
                cloud1.setStatus(0)  
            UpdateFinishTestsMethods(METHOD_2_CL1)


            try:     
                METHOD_2_CL2=InsertTestsMethods(TEST_ID,2,2)     
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
                cloud2.setStatus(0)  
            except requests.Timeout:
                print("OOPS!! Timeout Error")
                cloud2.setStatus(0)  
            except requests.RequestException:
                print("OOPS!! General Error")
                cloud2.setStatus(0)  
            except KeyboardInterrupt:
                print("Someone closed the program")
                cloud2.setStatus(0)  
            UpdateFinishTestsMethods(METHOD_2_CL2)

            time.sleep(5)

            now=datetime.now().utcnow()
            print("horario atual")
            print(now)
            intervalo=600
            delta = timedelta(seconds=intervalo)
            #deltagm= timedelta(seconds=10600)
            time_past=now-delta
            START=time_past
            STOP=now
            GRANULARITY=60

            CLOUD1_COD=GetIdCloud(NAME_CLOUD1)
            CLOUD2_COD=GetIdCloud(NAME_CLOUD2)
            COD_VNF1=GetIdVNF(VNF1_NAME)
            COD_VNF2=GetIdVNF(VNF2_NAME)

            #time.sleep(4) #Waiting collects
            #print("horarioInicio: "+str(START))
            #print("hoarioFinal: "+str(STOP))
            #collect data in gnocchi in each cloud
            # nova cpu 7c4d2383-1e6f-5bb3-a1f9-e210c10017e6    496967e6-8f56-54bb-8c1c-adca3318a52b
            #print(" id nova compute cloud1 ")
            #print(str(cloud1_resource_ids_nova)) 
            #print(" id nova compute cloud2 ")
            #print(str(cloud2_resource_ids_nova))    

            #Para seguir script do teste do artigo
            time.sleep(30)

            if(cloud1.getStatus()==1):
                METHOD_3_CL1=InsertTestsMethods(TEST_ID,3,1)
                #####Test#####Start#####get_last_measure()
                DATA_METRIC1_CL1=getLastMeasureClouds(METRIC1_NAME,cloud1_gnocchi,cloud1_resource_ids_nova,cloud1_resource_id,GRANULARITY,START,STOP)
                DATA_METRIC2_CL1=getLastMeasureClouds(METRIC2_NAME,cloud1_gnocchi,cloud1_resource_ids_nova,cloud1_resource_id,GRANULARITY,START,STOP)
                DATA_METRIC_DEGRADATION_VNF1_CL1=getLastMeasureClouds(DEGRADATION_VNF1_METRIC_NAME,cloud1_gnocchi,cloud1_resource_ids_nova,cloud1_resource_id,GRANULARITY,START,STOP)
                DATA_METRIC_DEGRADATION_VNF2_CL1=getLastMeasureClouds(DEGRADATION_VNF2_METRIC_NAME,cloud1_gnocchi,cloud1_resource_ids_nova,cloud1_resource_id,GRANULARITY,START,STOP)
                #time.sleep(20)
                #Alterado para testes
                #Latencia_to_cloud2=cloud1_gnocchi.get_last_measure("Lat_To_"+cloud1.getExternalIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)
                #print("LatenciatoCloud2: "+str(Latencia_to_cloud2))
                UpdateFinishTestsMethods(METHOD_3_CL1)
                
                Latencia_to_cloud2=cloud2_gnocchi.get_last_measure("Lat_To_"+cloud1.getExternalIp(),cloud2_resource_id,None,GRANULARITY,START,STOP)
                print("LatenciatoCloud2: "+str(Latencia_to_cloud2))
                Jitter_to_cloud2=cloud1_gnocchi.get_last_measure("Jit_To_"+cloud2.getExternalIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)
                print("JittertoCloud2: "+str(Jitter_to_cloud2))
                PILFile.SearchChangePriceLatencyJitterPIL(Latencia_to_cloud2,Latencia_to_cloud2,Jitter_to_cloud2,"openstackSerra","openstackAracruz2",TEST_ID)
                #time.sleep(20)
                #UpdateFinishTestsMethods(METHOD_3_CL1)

            if(cloud2.getStatus()==1):
                METHOD_3_CL2=InsertTestsMethods(TEST_ID,3,2)
                DATA_METRIC1_CL2=getLastMeasureClouds(METRIC1_NAME,cloud2_gnocchi,cloud2_resource_ids_nova,cloud2_resource_id,GRANULARITY,START,STOP)
                DATA_METRIC2_CL2=getLastMeasureClouds(METRIC2_NAME,cloud2_gnocchi,cloud2_resource_ids_nova,cloud2_resource_id,GRANULARITY,START,STOP)
                DATA_METRIC_DEGRADATION_VNF1_CL2=getLastMeasureClouds(DEGRADATION_VNF1_METRIC_NAME,cloud2_gnocchi,cloud2_resource_ids_nova,cloud1_resource_id,GRANULARITY,START,STOP)
                DATA_METRIC_DEGRADATION_VNF2_CL2=getLastMeasureClouds(DEGRADATION_VNF2_METRIC_NAME,cloud2_gnocchi,cloud2_resource_ids_nova,cloud2_resource_id,GRANULARITY,START,STOP)
                #####Test#####Stop#####get_last_measure()
                UpdateFinishTestsMethods(METHOD_3_CL2)
            
            #return "ok"

            METHOD_4_CL1=InsertTestsMethods(TEST_ID,4,1)
            METHOD_4_CL2=InsertTestsMethods(TEST_ID,4,2)
            #####Test#####Start#####InsertMetric()
            #Insert metrics in METRICS plao bd
            COD_METRIC1=insertMetric(METRIC1_NAME) #ex latency
            COD_METRIC2=insertMetric(METRIC2_NAME) # ex cpu
            #####Test#####Stop#####InsertMetric()
            UpdateFinishTestsMethods(METHOD_4_CL1)
            UpdateFinishTestsMethods(METHOD_4_CL2)


            METHOD_5_CL1=InsertTestsMethods(TEST_ID,5,1)
            #####Test#####Start#####InsertMetricCloud()
            #Inser metric for cloud
            insertMetricCloud(CLOUD1_COD,COD_METRIC1)
            insertMetricCloud(CLOUD1_COD,COD_METRIC2)
            UpdateFinishTestsMethods(METHOD_5_CL1)

            METHOD_5_CL2=InsertTestsMethods(TEST_ID,5,2)
            insertMetricCloud(CLOUD2_COD,COD_METRIC1)
            insertMetricCloud(CLOUD2_COD,COD_METRIC2)
            #####Test#####Stop#####InsertMetricCloud()
            UpdateFinishTestsMethods(METHOD_5_CL2)

            
            if(cloud1.getStatus()==1):
                METHOD_6_CL1=InsertTestsMethods(TEST_ID,6,1)
                #####Test#####Start#####InsertJobVnfCloud()
                #Insert values in JOBS_VNFS_CLOUDS table, necessario math join 2 metrics and wheights
                VNF1_CL1=insertJobVnfCloud("",JOB_COD,COD_VNF1,CLOUD1_COD,DEGRADATION_THRESHOLD_VNF1,DEGRADATION_THRESHOLD_TYPE_VNF1,DATA_METRIC_DEGRADATION_VNF1_CL1)
                VNF2_CL1=insertJobVnfCloud("",JOB_COD,COD_VNF2,CLOUD1_COD,DEGRADATION_THRESHOLD_VNF2,DEGRADATION_THRESHOLD_TYPE_VNF2,DATA_METRIC_DEGRADATION_VNF2_CL1)
                UpdateFinishTestsMethods(METHOD_6_CL1)

            
            if(cloud2.getStatus()==1):
                METHOD_6_CL2=InsertTestsMethods(TEST_ID,6,2)
                VNF1_CL2=insertJobVnfCloud("",JOB_COD,COD_VNF1,CLOUD2_COD,DEGRADATION_THRESHOLD_VNF1,DEGRADATION_THRESHOLD_TYPE_VNF1,DATA_METRIC_DEGRADATION_VNF1_CL2)
                VNF2_CL2=insertJobVnfCloud("",JOB_COD,COD_VNF2,CLOUD2_COD,DEGRADATION_THRESHOLD_VNF2,DEGRADATION_THRESHOLD_TYPE_VNF2,DATA_METRIC_DEGRADATION_VNF2_CL2)
                #####Test#####Stop#####InsertJobVnfCloud()
                UpdateFinishTestsMethods(METHOD_6_CL2)


            if(cloud1.getStatus()==1):
                METHOD_7_CL1=InsertTestsMethods(TEST_ID,7,1)
                #####Test#####Start#####InsertMetricsVnf()
                #Insert values metrics per cloud in METRICS_VNF table
                #Data of metric one and two, each weight per vnf
                VNF1_CL1_M1=insertMetricsVnf(DATA_METRIC1_CL1,WEIGHT_METRIC1_VNF1,COD_METRIC1,VNF1_CL1) #valor 26, peso  7, vnfa, latencia
                VNF1_CL1_M2=insertMetricsVnf(DATA_METRIC2_CL1,WEIGHT_METRIC2_VNF1,COD_METRIC2,VNF1_CL1) #valor 10, peso 3,  vnfa, cpu
                VNF2_CL1_M1=insertMetricsVnf(DATA_METRIC1_CL1,WEIGHT_METRIC1_VNF2,COD_METRIC1,VNF2_CL1) #valor 26, peso 1, vnfb, latencia
                VNF2_CL1_M2=insertMetricsVnf(DATA_METRIC2_CL1,WEIGHT_METRIC2_VNF2,COD_METRIC2,VNF2_CL1) #valor 10, peso 9,  vnfb, cpu
                UpdateFinishTestsMethods(METHOD_7_CL1)

            if(cloud2.getStatus()==1):
                METHOD_7_CL2=InsertTestsMethods(TEST_ID,7,2)
                VNF1_CL2_M1=insertMetricsVnf(DATA_METRIC1_CL2,WEIGHT_METRIC1_VNF1,COD_METRIC1,VNF1_CL2)
                VNF1_CL2_M2=insertMetricsVnf(DATA_METRIC2_CL2,WEIGHT_METRIC2_VNF1,COD_METRIC2,VNF1_CL2)
                VNF2_CL2_M1=insertMetricsVnf(DATA_METRIC1_CL2,WEIGHT_METRIC1_VNF2,COD_METRIC1,VNF2_CL2)
                VNF2_CL2_M2=insertMetricsVnf(DATA_METRIC2_CL2,WEIGHT_METRIC2_VNF2,COD_METRIC2,VNF2_CL2)
                #####Test#####Stop#####InsertMetricsVnf()
                UpdateFinishTestsMethods(METHOD_7_CL2)
            
            if(cloud1.getStatus()==1):
                METHOD_8_CL1=InsertTestsMethods(TEST_ID,8,1)
                #####Test#####Start#####GetMetricsVnfbyWeight()
                VNF1_CL1_M1_CALC=getMetricsVnfApplyWeight(VNF1_CL1_M1)#Calc VNF1 CL1 M1
                VNF1_CL1_M2_CALC=getMetricsVnfApplyWeight(VNF1_CL1_M2)#Calc VNF1 CL1 M2
                VNF1_CL1_CALC=VNF1_CL1_M1_CALC+VNF1_CL1_M2_CALC#Sum for Calc VNF1 in CL1
                VNF1_CL1_CALC=round(VNF1_CL1_CALC) #round
                print ("Cost of VNF1 CL1 (VNFA SERRA) is "+str(VNF1_CL1_CALC))
                ############################
                VNF2_CL1_M1_CALC=getMetricsVnfApplyWeight(VNF2_CL1_M1)#Calc VNF2 CL1 M1
                VNF2_CL1_M2_CALC=getMetricsVnfApplyWeight(VNF2_CL1_M2)#Calc VNF2 CL1 M2
                VNF2_CL1_CALC=VNF2_CL1_M1_CALC+VNF2_CL1_M2_CALC#Sum for Calc VNF2 in CL1
                VNF2_CL1_CALC=round(VNF2_CL1_CALC) #round
                print ("Cost of VNF2 CL1 (VNFB SERRA) is "+str(VNF2_CL1_CALC))
                UpdateFinishTestsMethods(METHOD_8_CL1)

            if(cloud2.getStatus()==1):
                METHOD_8_CL2=InsertTestsMethods(TEST_ID,8,2)
                ############################
                VNF1_CL2_M1_CALC=getMetricsVnfApplyWeight(VNF1_CL2_M1)#Calc VNF1 CL2 M1
                VNF1_CL2_M2_CALC=getMetricsVnfApplyWeight(VNF1_CL2_M2)#Calc VNF1 CL2 M2
                VNF1_CL2_CALC=VNF1_CL2_M1_CALC+VNF1_CL2_M2_CALC #Sum for Calc VNF1 in CL2
                VNF1_CL2_CALC=round(VNF1_CL2_CALC) #round
                print ("Cost of VNF1 CL2 (VNFA Aracruz) is "+str(VNF1_CL2_CALC))
                ############################    
                VNF2_CL2_M1_CALC=getMetricsVnfApplyWeight(VNF2_CL2_M1)#Calc VNF2 CL2 M1   
                VNF2_CL2_M2_CALC=getMetricsVnfApplyWeight(VNF2_CL2_M2)#Calc VNF2 CL2 M2
                VNF2_CL2_CALC=VNF2_CL2_M1_CALC+VNF2_CL2_M2_CALC#Sum for Calc VNF2 in CL2
                VNF2_CL2_CALC=round(VNF2_CL2_CALC) #round
                print ("Cost of VNF2 CL2 (VNFB Aracruz) is "+str(VNF2_CL2_CALC))
                ############################
                UpdateFinishTestsMethods(METHOD_8_CL2)

            if(cloud1.getStatus()==1):
                METHOD_9_CL1=InsertTestsMethods(TEST_ID,9,1)
                ############################
                #Update Costs in BD
                updateCostJobVnfCloud(VNF1_CL1,VNF1_CL1_CALC)
                updateCostJobVnfCloud(VNF2_CL1,VNF2_CL1_CALC)
                UpdateFinishTestsMethods(METHOD_9_CL1)

            if(cloud2.getStatus()==1):
                METHOD_9_CL2=InsertTestsMethods(TEST_ID,9,2)
                updateCostJobVnfCloud(VNF1_CL2,VNF1_CL2_CALC)
                updateCostJobVnfCloud(VNF2_CL2,VNF2_CL2_CALC)
                ############################
                UpdateFinishTestsMethods(METHOD_9_CL2)

            if(cloud1.getStatus()==1):
                METHOD_10_CL1=InsertTestsMethods(TEST_ID,10,1)
                #Check degradation
                #if has degradation now in specifc cloud, plus 10 units in vnf cost 
                #VNF1_CL1_STATUS_DEGRADATION=SelectStatusDegradationCloud(SelectIdCloud_JobVnfCloud(VNF1_CL1))
                #VNF2_CL1_STATUS_DEGRADATION=SelectStatusDegradationCloud(SelectIdCloud_JobVnfCloud(VNF2_CL1))
                #VNF1_CL2_STATUS_DEGRADATION=SelectStatusDegradationCloud(SelectIdCloud_JobVnfCloud(VNF1_CL2))
                #VNF2_CL2_STATUS_DEGRADATION=SelectStatusDegradationCloud(SelectIdCloud_JobVnfCloud(VNF2_CL2))
                VNF1_CL1_STATUS_DEGRADATION=getVnfStatusDegradation(VNF1_CL1)
                VNF2_CL1_STATUS_DEGRADATION=getVnfStatusDegradation(VNF2_CL1)
                UpdateFinishTestsMethods(METHOD_10_CL1)

            if(cloud2.getStatus()==1):
                METHOD_10_CL2=InsertTestsMethods(TEST_ID,10,2)
                VNF1_CL2_STATUS_DEGRADATION=getVnfStatusDegradation(VNF1_CL2)
                VNF2_CL2_STATUS_DEGRADATION=getVnfStatusDegradation(VNF2_CL2)
                #print (VNF1_CL1_STATUS_DEGRADATION + VNF2_CL1_STATUS_DEGRADATION + VNF1_CL2_STATUS_DEGRADATION + VNF2_CL2_STATUS_DEGRADATION)
                UpdateFinishTestsMethods(METHOD_10_CL2)
            

            #print("id clouds from vnf")
            #print (SelectIdCloud_JobVnfCloud(VNF1_CL1), SelectIdCloud_JobVnfCloud(VNF2_CL1), SelectIdCloud_JobVnfCloud(VNF1_CL2), SelectIdCloud_JobVnfCloud(VNF2_CL2) )
            
            #print("vnf degradation")
            #print(VNF1_CL1_STATUS_DEGRADATION,VNF2_CL1_STATUS_DEGRADATION,VNF1_CL2_STATUS_DEGRADATION,VNF2_CL2_STATUS_DEGRADATION +VNF1_CL2_STATUS_DEGRADATION + VNF2_CL2_STATUS_DEGRADATION)


            if(cloud1.getStatus()==1):
                #Refatorar para virar um metodo #####configVNFsCostsOSM()
                METHOD_11_CL1=InsertTestsMethods(TEST_ID,11,1)
                #store somewhere values link for logs          
                NAME_VNF=GetNameVNF(SelectIdVnf_JobVnfCloud(VNF1_CL1))
                VIM_URL=cloud1.getVimURL()
                PRICE_VNFD=str(VNF1_CL1_CALC)
                CLOUD_STATUS_DEGRADATION=int(VNF1_CL1_STATUS_DEGRADATION) #1 se a cpu estiver degradada select degradacao da nuvem
                #print("testando SearchChangeVNFDPrice") #Este devera se executaod por thrad que ira coletar das nuvens a latencia e cpu para formar o custo da VNF
                VNFFile.SearchChangeVNFDPrice(NAME_VNF,VIM_URL,PRICE_VNFD,CLOUD_STATUS_DEGRADATION,TEST_ID)
                print((NAME_VNF,VIM_URL,PRICE_VNFD,CLOUD_STATUS_DEGRADATION))

                NAME_VNF=GetNameVNF(SelectIdVnf_JobVnfCloud(VNF2_CL1))
                VIM_URL=cloud1.getVimURL()
                PRICE_VNFD=str(VNF2_CL1_CALC)
                CLOUD_STATUS_DEGRADATION=int(VNF2_CL1_STATUS_DEGRADATION) #1 se a cpu estiver degradada select degradacao da nuvem
                #print("testando SearchChangeVNFDPrice") #Este devera se executaod por thrad que ira coletar das nuvens a latencia e cpu para formar o custo da VNF
                VNFFile.SearchChangeVNFDPrice(NAME_VNF,VIM_URL,PRICE_VNFD,CLOUD_STATUS_DEGRADATION,TEST_ID)
                print((NAME_VNF,VIM_URL,PRICE_VNFD,CLOUD_STATUS_DEGRADATION))
                UpdateFinishTestsMethods(METHOD_11_CL1)

            if(cloud2.getStatus()==1):
                METHOD_11_CL2=InsertTestsMethods(TEST_ID,11,2)
                NAME_VNF=GetNameVNF(SelectIdVnf_JobVnfCloud(VNF1_CL2))
                VIM_URL=cloud2.getVimURL()
                PRICE_VNFD=str(VNF1_CL2_CALC)
                CLOUD_STATUS_DEGRADATION=int(VNF1_CL2_STATUS_DEGRADATION) #1 se a cpu estiver degradada select degradacao da nuvem
                #print("testando SearchChangeVNFDPrice") #Este devera se executaod por thrad que ira coletar das nuvens a latencia e cpu para formar o custo da VNF
                VNFFile.SearchChangeVNFDPrice(NAME_VNF,VIM_URL,PRICE_VNFD,CLOUD_STATUS_DEGRADATION,TEST_ID)
                print((NAME_VNF,VIM_URL,PRICE_VNFD,CLOUD_STATUS_DEGRADATION))

                NAME_VNF=GetNameVNF(SelectIdVnf_JobVnfCloud(VNF2_CL2))
                VIM_URL=cloud2.getVimURL()
                PRICE_VNFD=str(VNF2_CL2_CALC)
                CLOUD_STATUS_DEGRADATION=int(VNF2_CL2_STATUS_DEGRADATION) #1 se a cpu estiver degradada select degradacao da nuvem
                #print("testando SearchChangeVNFDPrice") #Este devera se executaod por thrad que ira coletar das nuvens a latencia e cpu para formar o custo da VNF
                VNFFile.SearchChangeVNFDPrice(NAME_VNF,VIM_URL,PRICE_VNFD,CLOUD_STATUS_DEGRADATION,TEST_ID)
                print((NAME_VNF,VIM_URL,PRICE_VNFD,CLOUD_STATUS_DEGRADATION))
                UpdateFinishTestsMethods(METHOD_11_CL2)


            METHOD_12_CL1=InsertTestsMethods(TEST_ID,12,1)
            METHOD_12_CL2=InsertTestsMethods(TEST_ID,12,2)
            #Instanciate NS in OSM
            OSM.check_token_valid(token)
            #print(token['id'])
            print("nsd name")
            print(NSD_NAME)
            NSDID=OSM.osm_get_nsd_id_byname(token['id'],NSD_NAME)
            
            if (NSDID) == "-1":
                return "NSD not exits"

            id_ns_scheduled=(OSM.osm_create_instance_ns((token['id']),NS_NAME_INSTANCIATED,NSDID,VIMACCOUNTID))

            id_ns_instanciated=InsertNsInstanciated(NS_NAME_INSTANCIATED,id_ns_scheduled['id'],1,JOB_COD)


           # InsertVnfInstanciated()
            #class Vnf_Instanciateds(BaseModel):
            #    id_vnf_instanciated=BigIntegerField( unique=True, primary_key=True,
            #            constraints=[SQL('AUTO_INCREMENT')])
            #    id_osm_vnf_instanciated = CharField(max_length=100)  #'_id'
            #    name_osm_vnf_instanciated = CharField(max_length=100) #'vnfd-ref'
            #    fk_cloud = ForeignKeyField(Clouds, db_column='id_cloud') #'vim-account-id'
            #    fk_status = ForeignKeyField(Status, db_column='id_status') #1
            #    fk_ns_instanciated = ForeignKeyField(NS_Instanciateds, db_column='id_ns_instanciated') #id_ns_scheduled['id']
            #    creation_date_vnf_instanciated = DateTimeField()      #now
            #    finish_date_vnf_instanciated = DateTimeField()

            #insert table BD as informacoes vnf
            OSM.check_token_valid(token)

            OSM.osm_create_instance_ns_scheduled((token['id']),NS_NAME_INSTANCIATED,str(id_ns_scheduled['id']),VIMACCOUNTID,NSDID,CONSTRAINT_OPERACAO,CONSTRAINT_LATENCY,CONSTRAINT_JITTER,CONSTRAINT_VLD_ID)
            InsertActionsTests(TEST_ID,1,datetime.timestamp(datetime.now().utcnow())) #Instaciating VNF
            #criar metodo passar o codigo osm da nuvem e retorar o codigo primary key nele na tabela Cloud
            #out=False
            #while out==False:
            #    for i in OSM.osm_get_instance_vnf(token['id']):
            #        if i['nsr-id-ref'] == id_ns_scheduled['id']:
            #            if i['_admin']['nsState'] == 'INSTANTIATED':
            #                #InsertVnfInstanciated(i['_id'],i['vnfd-ref'],GetIdCloudbyvimidosm(i['vim-account-id']),1,id_ns_instanciated)
            #                print(i)
            #                print("id vnf")
            #                print (i['_id'])
            #                print("vim account id")
            #                print(i['vim-account-id'])
            #                print(i['_admin']['nsState'])
            #                out=True
            VNF_ALREADY=[]

            out=False
            out2=False
            timeout=0
            while out==False:
                test=OSM.osm_get_instance_ns_byid(token['id'],id_ns_scheduled['id'])
                #print("dentro while")
                if 'nsState' in test:
                    #print("condicao test ok")
                    #if test['nsState'] == "READY": #BUILDING whilen making
                    while out2==False:
                        #time.sleep(2)
                        print('NS pronto, registrando VNFs')
                        for i in OSM.osm_get_instance_vnf(token['id']):
                            #time.sleep(1)
                            if i['nsr-id-ref'] == id_ns_scheduled['id']:
                                if i['_admin']['nsState'] == 'INSTANTIATED':
                                    ####print(i['vim-account-id'])
                                    InsertVnfInstanciated(i['_id'],i['vnfd-ref'],GetIdCloudbyvimidosm(i['vim-account-id']),1,id_ns_instanciated)
                                    ####print("imprimindo teste")
                                    ###print(test)
                                    ###print("imprimindo VNFs")
                                    #print(i)
                                    #print("id vnf")
                                    #print (i['_id'])
                                    #print(i['ip-address'])
                                    #print("vim account id")
                                    #print(i['vim-account-id'])
                                    #print(VNF_ALREADY)
                                    if i['ip-address'] is not None:
                                        ###print(i['ip-address'])
                                        if not (VNF_ALREADY.__contains__(i['ip-address'])):
                                            if (i['vim-account-id']=="9f104eee-5470-4e23-a8dd-3f64a53aa547"):
                                                VNF_ALREADY.append(i['ip-address'])
                                                #print("registrando cloud 1")
                                                #print("eh este 9f104eee-5470-4e23-a8dd-3f64a53aa547")
                                                InsertActionsTests(TEST_ID,6,datetime.timestamp(datetime.now().utcnow())) #Registrar Instanciado nuvem 1
                                                UpdateFinishTestsMethodsifNone(METHOD_12_CL1) #CL1                                    
                                            if (i['vim-account-id']=="6ba02d24-6320-4322-9177-eb4987ad9465"):
                                                VNF_ALREADY.append(i['ip-address'])
                                                #print("registrando cloud 2")
                                                #print("eh este 6ba02d24-6320-4322-9177-eb4987ad9465")
                                                InsertActionsTests(TEST_ID,7,datetime.timestamp(datetime.now().utcnow())) #Registrar instanciado nuvem 2
                                                UpdateFinishTestsMethodsifNone(METHOD_12_CL2) #CL2
                                                
                                    #print(VNF_ALREADY)
                                    #print(i['_admin']['nsState'])
                        if(len(VNF_ALREADY)==2):
                            out2=True
                    if(test['nsState'] == "READY"):
                        ###print("VNFS ALREADY and nState READY")
                        InsertActionsTests(TEST_ID,5,datetime.timestamp(datetime.now().utcnow())) #Registrar acao ao ser executado/Criar outro tipo para finalizado
                        UpdateNsInstanciated(id_ns_scheduled,2,JOB_COD)
                        out=True
                timeout=timeout+1
                print(str(timeout))
                if(timeout==90000):
                    print("saiu por timeout")
                    out=True
            #return "ok"
            if (timeout != 80000) :
                # UpdateFinishTestsMethodsifNone(METHOD_12_CL1)
                # UpdateFinishTestsMethodsifNone(METHOD_12_CL2)
                TestTimes_check=SelectTestbyId(TEST_ID)
                #return("ok")
                START_TEST_CHECK=TestTimes_check.get('start_date_test')
                TEST_NOW = float(datetime.timestamp(datetime.now().utcnow()))
                LEN_TEST=TEST_NOW-float(START_TEST_CHECK)
                print("falta para os 210 segundos")
                print(round(LEN_TEST))
                if (LEN_TEST <= 210):
                    ESPERAR=(210-LEN_TEST)
                    time.sleep(round(ESPERAR))

                #Update Status Jobs
                UpdateJob(JOB_COD,2) #Finished the job

                DesativaThreadColetaCPU_Memoria() #Desativa coleta cpu e memoria # SE FOR TER VARIOS JOBS AO MESMO TEMPOS, REPENSAR
                UpdateFinishDateTestsbyId(TEST_ID)

                TestTimes=SelectTestbyId(TEST_ID)
                START_TEST=TestTimes.get('start_date_test')
                STOP_TEST=TestTimes.get('finish_date_test')

                START_TEST=datetime.fromtimestamp(float(START_TEST))
                STOP_TEST=datetime.fromtimestamp(float(STOP_TEST))

                #print ("start test")
                #print(START_TEST)
                #print("stop test")
                #print(STOP_TEST)

                OSM.check_token_valid(token)

                #print(datetime.fromtimestamp(START_TEST))
                #print(datetime.fromtimestamp(STOP_TEST))

                ###DADOS NVNF
                CLOUD_GNOCCHI=cloud1_gnocchi
                CLOUD_RESOURCE=cloud1_resource_id
                GRANULARITY=5.0
                METRIC="NVNF"
                AGGREGATION="max"
                COD_DATA_TYPE=3 #NVNF
                COD_CLOUD=1
                get_data=CLOUD_GNOCCHI.get_last_measure_Date(METRIC,CLOUD_RESOURCE,AGGREGATION,GRANULARITY,START_TEST,STOP_TEST,TEST_ID,COD_CLOUD,COD_DATA_TYPE)
                #print(get_data)
                if get_data == -1:
                    print ("Error-NVNF Cloud 1") 
                else:
                    metrics_test=json.loads(get_data)
                    #print(metrics_test)
                    Data_Tests.insert_many(metrics_test, fields=[Data_Tests.date_data_tests, Data_Tests.granularity_data_tests, Data_Tests.value_data_tests, Data_Tests.fk_tests, Data_Tests.fk_data_tests_types, Data_Tests.fk_cloud]).execute()


                CLOUD_GNOCCHI=cloud2_gnocchi
                CLOUD_RESOURCE=cloud2_resource_id
                GRANULARITY=5.0
                METRIC="NVNF"
                AGGREGATION="max"
                COD_DATA_TYPE=3 #NVNF
                COD_CLOUD=2
                get_data=CLOUD_GNOCCHI.get_last_measure_Date(METRIC,CLOUD_RESOURCE,AGGREGATION,GRANULARITY,START_TEST,STOP_TEST,TEST_ID,COD_CLOUD,COD_DATA_TYPE)
                #print(get_data)
                if get_data == -1:
                    print ("Error-NVNF Cloud 2") 
                else:
                    metrics_test=json.loads(get_data)
                    #print(metrics_test)
                    Data_Tests.insert_many(metrics_test, fields=[Data_Tests.date_data_tests, Data_Tests.granularity_data_tests, Data_Tests.value_data_tests, Data_Tests.fk_tests, Data_Tests.fk_data_tests_types, Data_Tests.fk_cloud]).execute()

                print("vai comecar cpu n1")
                ###DADOS CPU
                CLOUD_GNOCCHI=cloud1_gnocchi
                CLOUD_RESOURCE=cloud1_resource_ids_nova[0]
                GRANULARITY=60.0
                METRIC=METRIC2_NAME
                AGGREGATION="mean"
                COD_DATA_TYPE=1 #CPU
                COD_CLOUD=1
                get_data=CLOUD_GNOCCHI.get_last_measure_Date(METRIC,CLOUD_RESOURCE,AGGREGATION,GRANULARITY,START_TEST,STOP_TEST,TEST_ID,COD_CLOUD,COD_DATA_TYPE)
                #print(get_data)
                if get_data == -1:
                    print ("Error-CPU Cloud 1 60")
                else:
                    metrics_test=json.loads(get_data)
                    #print(metrics_test)
                    Data_Tests.insert_many(metrics_test, fields=[Data_Tests.date_data_tests, Data_Tests.granularity_data_tests, Data_Tests.value_data_tests, Data_Tests.fk_tests, Data_Tests.fk_data_tests_types, Data_Tests.fk_cloud]).execute()


                print("vai comecar latencia n1 to n2")
                ###DADOS Latencia
                CLOUD_GNOCCHI=cloud1_gnocchi
                CLOUD_RESOURCE=cloud1_resource_id
                GRANULARITY=5.0
                METRIC="Lat_To_200.137.82.21"
                AGGREGATION="mean"
                COD_DATA_TYPE=5 #Latency Serra to Aracruz
                COD_CLOUD=1
                get_data=CLOUD_GNOCCHI.get_last_measure_Date(METRIC,CLOUD_RESOURCE,AGGREGATION,GRANULARITY,START_TEST,STOP_TEST,TEST_ID,COD_CLOUD,COD_DATA_TYPE)
                #print(get_data)
                if get_data == -1:
                    print ("Error-Latencia Cloud 1 5")
                else:
                    metrics_test=json.loads(get_data)
                    #print(metrics_test)
                    Data_Tests.insert_many(metrics_test, fields=[Data_Tests.date_data_tests, Data_Tests.granularity_data_tests, Data_Tests.value_data_tests, Data_Tests.fk_tests, Data_Tests.fk_data_tests_types, Data_Tests.fk_cloud]).execute()


                print("vai comecar jitter n1 to n2")
                ###DADOS Latencia
                CLOUD_GNOCCHI=cloud1_gnocchi
                CLOUD_RESOURCE=cloud1_resource_id
                GRANULARITY=5.0
                METRIC="Jit_To_200.137.82.21"
                AGGREGATION="mean"
                COD_DATA_TYPE=6 #Jitter Serra to Aracruz
                COD_CLOUD=1
                get_data=CLOUD_GNOCCHI.get_last_measure_Date(METRIC,CLOUD_RESOURCE,AGGREGATION,GRANULARITY,START_TEST,STOP_TEST,TEST_ID,COD_CLOUD,COD_DATA_TYPE)
                #print(get_data)
                if get_data == -1:
                    print ("Error-Jitter Cloud 1 to n2 5")
                else:
                    metrics_test=json.loads(get_data)
                    #print(metrics_test)
                    Data_Tests.insert_many(metrics_test, fields=[Data_Tests.date_data_tests, Data_Tests.granularity_data_tests, Data_Tests.value_data_tests, Data_Tests.fk_tests, Data_Tests.fk_data_tests_types, Data_Tests.fk_cloud]).execute()


                print("vai comecar latencia n2 to n1")
                ###DADOS Latencia
                CLOUD_GNOCCHI=cloud2_gnocchi
                CLOUD_RESOURCE=cloud2_resource_id
                GRANULARITY=5.0
                METRIC="Lat_To_200.137.75.160"
                AGGREGATION="mean"
                COD_DATA_TYPE=7 #Latency to Serra
                COD_CLOUD=2
                get_data=CLOUD_GNOCCHI.get_last_measure_Date(METRIC,CLOUD_RESOURCE,AGGREGATION,GRANULARITY,START_TEST,STOP_TEST,TEST_ID,COD_CLOUD,COD_DATA_TYPE)
                #print(get_data)
                if get_data == -1:
                    print ("Error-Latencia Cloud 2 5")
                else:
                    metrics_test=json.loads(get_data)
                    #print(metrics_test)
                    Data_Tests.insert_many(metrics_test, fields=[Data_Tests.date_data_tests, Data_Tests.granularity_data_tests, Data_Tests.value_data_tests, Data_Tests.fk_tests, Data_Tests.fk_data_tests_types, Data_Tests.fk_cloud]).execute()

                print("vai comecar Jitter n2 to n1")
                ###DADOS Latencia
                CLOUD_GNOCCHI=cloud2_gnocchi
                CLOUD_RESOURCE=cloud2_resource_id
                GRANULARITY=5.0
                METRIC="Jit_To_200.137.75.160"
                AGGREGATION="mean"
                COD_DATA_TYPE=8 #Jitter to Serra
                COD_CLOUD=2
                get_data=CLOUD_GNOCCHI.get_last_measure_Date(METRIC,CLOUD_RESOURCE,AGGREGATION,GRANULARITY,START_TEST,STOP_TEST,TEST_ID,COD_CLOUD,COD_DATA_TYPE)
                #print(get_data)
                if get_data == -1:
                    print ("Error-Latencia Cloud 2 5")
                else:
                    metrics_test=json.loads(get_data)
                    #print(metrics_test)
                    Data_Tests.insert_many(metrics_test, fields=[Data_Tests.date_data_tests, Data_Tests.granularity_data_tests, Data_Tests.value_data_tests, Data_Tests.fk_tests, Data_Tests.fk_data_tests_types, Data_Tests.fk_cloud]).execute()


                print("vai comecar latencia n1 to user")
                ###DADOS Latencia
                CLOUD_GNOCCHI=cloud1_gnocchi
                CLOUD_RESOURCE=cloud1_resource_id
                GRANULARITY=5.0
                METRIC="Lat_To_200.137.82.11"
                AGGREGATION="mean"
                COD_DATA_TYPE=9 #Latencia to User
                COD_CLOUD=1
                get_data=CLOUD_GNOCCHI.get_last_measure_Date(METRIC,CLOUD_RESOURCE,AGGREGATION,GRANULARITY,START_TEST,STOP_TEST,TEST_ID,COD_CLOUD,COD_DATA_TYPE)
                #print(get_data)
                if get_data == -1:
                    print ("Error-latencia Cloud 1 to user 5")
                else:
                    metrics_test=json.loads(get_data)
                    #print(metrics_test)
                    Data_Tests.insert_many(metrics_test, fields=[Data_Tests.date_data_tests, Data_Tests.granularity_data_tests, Data_Tests.value_data_tests, Data_Tests.fk_tests, Data_Tests.fk_data_tests_types, Data_Tests.fk_cloud]).execute()

                print("vai comecar latencia n2 to user")
                ###DADOS Latencia
                CLOUD_GNOCCHI=cloud2_gnocchi
                CLOUD_RESOURCE=cloud2_resource_id
                GRANULARITY=5.0
                METRIC="Lat_To_200.137.82.11"
                AGGREGATION="mean"
                COD_DATA_TYPE=10 #Latencia to User
                COD_CLOUD=2
                get_data=CLOUD_GNOCCHI.get_last_measure_Date(METRIC,CLOUD_RESOURCE,AGGREGATION,GRANULARITY,START_TEST,STOP_TEST,TEST_ID,COD_CLOUD,COD_DATA_TYPE)
                #print(get_data)
                if get_data == -1:
                    print ("Error-latencia Cloud 2 to user 5")
                else:
                    metrics_test=json.loads(get_data)
                    #print(metrics_test)
                    Data_Tests.insert_many(metrics_test, fields=[Data_Tests.date_data_tests, Data_Tests.granularity_data_tests, Data_Tests.value_data_tests, Data_Tests.fk_tests, Data_Tests.fk_data_tests_types, Data_Tests.fk_cloud]).execute()

                print("vai comecar cpu n1")
                ###DADOS CPU
                CLOUD_GNOCCHI=cloud1_gnocchi
                CLOUD_RESOURCE=cloud1_resource_ids_nova[0]
                GRANULARITY=5.0
                METRIC=METRIC2_NAME
                AGGREGATION="mean"
                COD_DATA_TYPE=1 #CPU
                COD_CLOUD=1
                get_data=CLOUD_GNOCCHI.get_last_measure_Date(METRIC,CLOUD_RESOURCE,AGGREGATION,GRANULARITY,START_TEST,STOP_TEST,TEST_ID,COD_CLOUD,COD_DATA_TYPE)
                #print(get_data)
                if get_data == -1:
                    print ("Error-CPU Cloud 1 cpu1 5")
                else:   
                    metrics_test=json.loads(get_data)
                    #print(metrics_test)
                    Data_Tests.insert_many(metrics_test, fields=[Data_Tests.date_data_tests, Data_Tests.granularity_data_tests, Data_Tests.value_data_tests, Data_Tests.fk_tests, Data_Tests.fk_data_tests_types, Data_Tests.fk_cloud]).execute()

                print("vai comecar cpu cloud2")
                ###DADOS CPU
                CLOUD_GNOCCHI=cloud2_gnocchi
                CLOUD_RESOURCE=cloud2_resource_ids_nova[0]
                GRANULARITY=60.0
                METRIC=METRIC2_NAME
                AGGREGATION="mean"
                COD_DATA_TYPE=1 #CPU
                COD_CLOUD=2
                get_data=CLOUD_GNOCCHI.get_last_measure_Date(METRIC,CLOUD_RESOURCE,AGGREGATION,GRANULARITY,START_TEST,STOP_TEST,TEST_ID,COD_CLOUD,COD_DATA_TYPE)
                #print(get_data)
                if get_data == -1:
                    print ("Error-CPU Cloud 2 cpu1 c1 60")  
                else:
                    metrics_test=json.loads(get_data)
                    #print(metrics_test)
                    Data_Tests.insert_many(metrics_test, fields=[Data_Tests.date_data_tests, Data_Tests.granularity_data_tests, Data_Tests.value_data_tests, Data_Tests.fk_tests, Data_Tests.fk_data_tests_types, Data_Tests.fk_cloud]).execute()

                #print("vai comecar cpu cloud2")
                ###DADOS CPU
                CLOUD_GNOCCHI=cloud2_gnocchi
                CLOUD_RESOURCE=cloud2_resource_ids_nova[0]
                GRANULARITY=5.0
                METRIC=METRIC2_NAME
                AGGREGATION="mean"
                COD_DATA_TYPE=1 #CPU
                COD_CLOUD=2
                get_data=CLOUD_GNOCCHI.get_last_measure_Date(METRIC,CLOUD_RESOURCE,AGGREGATION,GRANULARITY,START_TEST,STOP_TEST,TEST_ID,COD_CLOUD,COD_DATA_TYPE)
                #print(get_data)
                if get_data == -1:
                    print ("Error-CPU Cloud 2 cpu2 c1 5") 
                else: 
                    metrics_test=json.loads(get_data)
                    #print(metrics_test)
                    Data_Tests.insert_many(metrics_test, fields=[Data_Tests.date_data_tests, Data_Tests.granularity_data_tests, Data_Tests.value_data_tests, Data_Tests.fk_tests, Data_Tests.fk_data_tests_types, Data_Tests.fk_cloud]).execute()

                print("vai comecar cpu cloud2 60")
                ###DADOS CPU
                CLOUD_GNOCCHI=cloud2_gnocchi
                CLOUD_RESOURCE=cloud2_resource_ids_nova[1]
                GRANULARITY=60.0
                METRIC=METRIC2_NAME
                AGGREGATION="mean"
                COD_DATA_TYPE=2 #CPU2
                COD_CLOUD=2
                get_data=CLOUD_GNOCCHI.get_last_measure_Date(METRIC,CLOUD_RESOURCE,AGGREGATION,GRANULARITY,START_TEST,STOP_TEST,TEST_ID,COD_CLOUD,COD_DATA_TYPE)
                #print(get_data)
                if get_data == -1:
                    print ("Error-CPU Cloud 2 cpu2 c2 60")  
                else:
                    metrics_test=json.loads(get_data)
                    #print(metrics_test)
                    Data_Tests.insert_many(metrics_test, fields=[Data_Tests.date_data_tests, Data_Tests.granularity_data_tests, Data_Tests.value_data_tests, Data_Tests.fk_tests, Data_Tests.fk_data_tests_types, Data_Tests.fk_cloud]).execute()

                print("vai comecar cpu cloud2 5")
                ###DADOS CPU
                CLOUD_GNOCCHI=cloud2_gnocchi
                CLOUD_RESOURCE=cloud2_resource_ids_nova[1]
                GRANULARITY=5.0
                METRIC=METRIC2_NAME
                AGGREGATION="mean"
                COD_DATA_TYPE=2 #CPU2
                COD_CLOUD=2
                get_data=CLOUD_GNOCCHI.get_last_measure_Date(METRIC,CLOUD_RESOURCE,AGGREGATION,GRANULARITY,START_TEST,STOP_TEST,TEST_ID,COD_CLOUD,COD_DATA_TYPE)
                #print(get_data)
                if get_data == -1:
                    print ("Error-CPU Cloud 1 c2 5")  
                else:
                    metrics_test=json.loads(get_data)
                    #print(metrics_test)
                    Data_Tests.insert_many(metrics_test, fields=[Data_Tests.date_data_tests, Data_Tests.granularity_data_tests, Data_Tests.value_data_tests, Data_Tests.fk_tests, Data_Tests.fk_data_tests_types, Data_Tests.fk_cloud]).execute()


                print("coletas")
                print("latencia to user Serra")
                print(DATA_METRIC1_CL1)
                print("cpu Serra")
                print(DATA_METRIC2_CL1)
                print("latencia to user Aracruz")
                print(DATA_METRIC1_CL2)
                print("cpu Aracruz")
                print(DATA_METRIC2_CL2)
                print("Lantencia entre Serra e Aracruz")
                print(Latencia_to_cloud2)
                print(OSMgetvnf3())
                
                return str(JOB_COD)
            else:
                print("Problem Instanciation")
                #UpdateFinishTestsMethods(METHOD_12_CL1)
                UpdateFinishDateTestsbyId(TEST_ID)
                return "-1"

    #servers = Servers()
    #IPServerLocal="10.159.205.10"
    IPServerLocal="127.0.0.1"
    #Alterar para IP do servidor do PLAO
    app.run(IPServerLocal, '3332',debug=True)

def CriaThreadColetaCPU_Memoria(tempo_coleta,id_test):
    thread_MonitorCPUPlaoServer = threading.Thread(target=Collector_CPU_PLAO_Server,args=(tempo_coleta,id_test))
    thread_MonitorCPUPlaoServer.start()
    thread_MonitorMemoriaPlaoServer = threading.Thread(target=Collector_Memory_PLAO_Server,args=(tempo_coleta,id_test))
    thread_MonitorMemoriaPlaoServer.start()

def DesativaThreadColetaCPU_Memoria():
    global COMMAND_MON_PLAO
    COMMAND_MON_PLAO=0

def getMetricsVnfApplyWeight(VNF_CL_M):
    #Calc VNF CL M
    print("- - - -")
    print (VNF_CL_M)
    VNF_CL_M_BD=GetMetricsVnf(VNF_CL_M)
    VNF_CL_M_BD=VNF_CL_M_BD.split(':')
    VNF_CL_M_BD_VALUE=VNF_CL_M_BD[0]
    VNF_CL_M_BD_WEIGHT=VNF_CL_M_BD[1]
    VNF_CL_M_CALC=(float(VNF_CL_M_BD_VALUE)*float(VNF_CL_M_BD_WEIGHT))
    print("Metric x Weigth")
    print (str(VNF_CL_M_BD_VALUE) + "x" +str(VNF_CL_M_BD_WEIGHT) + "=" +str(VNF_CL_M_CALC))
    
    return VNF_CL_M_CALC


def getLastMeasureClouds(METRIC2_NAME,cloud1_gnocchi,cloud1_resource_ids_nova,cloud1_resource_id,GRANULARITY,START,STOP):
    if (METRIC2_NAME.__contains__("Lat_To_")):
        if (METRIC2_NAME.__contains__("200.137.82.11")):
            print("if ip 200.137.82.11")
            DATA_METRIC2_CL2=cloud1_gnocchi.get_last_measure(METRIC2_NAME,cloud1_resource_id,None,5,None,None)
            print(DATA_METRIC2_CL2)
            return DATA_METRIC2_CL2
        else:
            DATA_METRIC2_CL2=cloud1_gnocchi.get_last_measure(METRIC2_NAME,cloud1_resource_id,None,GRANULARITY,START,STOP)
            print(DATA_METRIC2_CL2)
            return DATA_METRIC2_CL2
    else:
        print("if cpu")
        INDEX=0
        DATA_METRIC2_CL2=0
        DATA_METRIC2_CL2_TOT=0
        for i in cloud1_resource_ids_nova:
            DATA_METRIC2_CL2_PRE1=cloud1_gnocchi.get_last_measure(METRIC2_NAME,cloud1_resource_ids_nova[INDEX],None,GRANULARITY,START,STOP)
            DATA_METRIC2_CL2_TOT=DATA_METRIC2_CL2_TOT+DATA_METRIC2_CL2_PRE1
            INDEX=INDEX+1
        DATA_METRIC2_CL2=DATA_METRIC2_CL2_TOT/INDEX
        print(DATA_METRIC2_CL2_TOT)
        print(DATA_METRIC2_CL2)
        return DATA_METRIC2_CL2

if __name__ == "__main__":
    main()