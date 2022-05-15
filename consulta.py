from http.client import HTTPConnection
from multiprocessing.connection import Connection
import yaml
import threading
import subprocess
from datetime import date,timedelta
from PLAO_client2 import *
#from PLAO2_w_routes import app
from flask import Flask, request
import requests
import pytz

tz_SP = pytz.timezone("America/Sao_Paulo")
print(tz_SP)
SP = datetime.now(tz_SP)
print (SP)

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



def main():
    print ("Iniciando Server PLAO")
    #VNFFile = File_VNF_Price()
    PILFile = File_PIL_Price()

    NAME_VNFD="VNFA"

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

    print("Latencia entre nuvens")
    last_Lat=Collector_Metrics_Links_Demand(cloud1_gnocchi,cloud1_resource_id,cloud2,PILFile,"200.137.82.21","200.137.75.159",1,"Lat_To_")
    print(last_Lat)
    print ("Jitter entre nuvens")
    last_Jit=Collector_Metrics_Links_Demand(cloud1_gnocchi,cloud1_resource_id,cloud2,PILFile,"200.137.82.21","200.137.75.159",1,"Jit_To_")
    print(last_Jit)

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
                        arquivo.write( DATEHOURS() + '#CHANGE_PIL# Changed and copied file '+FILE_PIL_PRICE + ' to container PLA. ' +' PRICE: '+PRICE+' LATENCY: '+LATENCY+' JITTER: '+JITTER+'\n')
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


def Collector_Metrics_Links(cloud1_gnocchi,cloud1_resource_id,cloud2,PILFile,CLOUD_FROM,CLOUD_TO,interval,metric_name):
    #while True:
    now=datetime.now()
    #now=datetime.now(tz_SP)

    #intervalo=300
    delta = timedelta(seconds=interval)
    time_past=now-delta
    #START = "2021-08-01 13:30:33+00:00"
    #STOP = "2021-08-01 13:35:36+00:00"
    START=time_past
    STOP=now
    print (" start: " +str(START)+" stop: "+str(STOP))
    GRANULARITY=60.0
    print("horarioInicio: "+str(START))
    print("hoarioFinal: "+str(STOP))
    Latencia_to_cloud2=cloud1_gnocchi.get_last_measure(metric_name+cloud2.getExternalIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)
    print("LatenciatoCloud2: "+str(Latencia_to_cloud2))
    Jitter_to_cloud2=cloud1_gnocchi.get_last_measure("Jit_To_"+cloud2.getExternalIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)
    print("JittertoCloud2: "+str(Jitter_to_cloud2))
    PILFile.SearchChangePriceLatencyJitterPIL(Latencia_to_cloud2,Latencia_to_cloud2,Jitter_to_cloud2,CLOUD_FROM,CLOUD_TO)
    #    time.sleep(5)


def Collector_Metrics_Links_Demand(cloud1_gnocchi,cloud1_resource_id,cloud2,PILFile,CLOUD_FROM,CLOUD_TO,interval,metric_name):
    now=datetime.now()
    delta = timedelta(seconds=interval)
    time_past=now-delta
    #START = "2021-08-01 13:30:33+00:00"
    #STOP = "2021-08-01 13:35:36+00:00"
    START=time_past
    STOP=now
    GRANULARITY=60.0
    return cloud1_gnocchi.get_last_measure(metric_name+cloud2.getExternalIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)

#Collect metric links from cloud1 to cloud2
def Monitor_Request_LatencyUser_Cloud1(cloud1_gnocchi,cloud1_resource_id,VNFFile,CLOUD_FROM):
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
        #Latencia_to_cloud2=cloud1_gnocchi.get_last_measure("Lat_To_"+cloud2.getIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)
        #print(Latencia_to_cloud2)
        #Jitter_to_cloud2=cloud1_gnocchi.get_last_measure("Jit_To_"+cloud2.getIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)
        #print(Jitter_to_cloud2)
        #PILFile.SearchChangePriceLatencyJitterPIL(Latencia_to_cloud2,Latencia_to_cloud2,Jitter_to_cloud2,CLOUD_FROM,CLOUD_TO)
        #time.sleep(5)

def Collector_Metrics_Disaggregated_cl1(cloud1_gnocchi,cloud1_resource_id_nova,Cloud,VNFFile):
    while True:
        now=datetime.now()
        intervalo=400
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

        if (int(CPU_cloud1) > THRESHOLD) and (Cloud.getCpuStatus() == 0):
            CPU_STATUS_NOW=1   #Values: 0-cpu normal, 1-cpu high and cost value going to change
            VNFFile.SearchDownUpVimPrice(CPU_STATUS_NOW,Cloud) #The cost is add by CPU bigger
        if (int(CPU_cloud1) < THRESHOLD) and (Cloud.getCpuStatus() == 1):
            CPU_STATUS_NOW=0   #Values: 0-cpu normal, 1-cpu high and cost value going to change
            VNFFile.SearchDownUpVimPrice(CPU_STATUS_NOW,Cloud) #The cost is add by CPU bigger
        time.sleep(5)

if __name__ == "__main__":
    main()