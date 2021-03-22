import socket
import time
import sys
import datetime
import platform
import subprocess

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

#/opt/plao   root of application withc .py
#/opt/plao/utils/ local iperf
#/opt/plao/logs  aquivos de log
#/opt/plao/osm arquivos configuracaoOSM
#/opt/plao/openstack

# The values in config files of OSM need to be integer
QUANTITY_PCK="5" #Quantity packages to use in ping command 
DIR_IPERF="C:/Temp/artigo/utils/iperf/" #directory of iperf application

HOST = sys.argv[1] #Address Server OSM IP
if sys.argv[1] == '':
    print ("Invalido: We need the IP OSM Sever.")
    exit()

PORT = 6000 #Port Server
CLOUDNAME_LOCAL = sys.argv[2] #Cloud Name, this may equal in PLA configuration files (pill_price_list.yaml and vnf_price_list.yaml)
if sys.argv[2] == '':
    print ("Invalido: We need cloud name. Equal in PLA configuration files (pill_price_list.yaml and vnf_price_list.yaml) for OSM.")
    exit()

CLOUDIP_LOCAL = sys.argv[3] #Address Server Cloud IP
if sys.argv[3] == '':
    print ("Invalido: We need cloud IP Address.")
    exit()

def DATAHORAC():
    DATAHORAC = datetime.datetime.now().strftime('%d.%m.%y-%H:%M:%S')  # convert hour to string
    return DATAHORAC

def GetHypervisorStats(OPENSTACK_FROM, PARAMETER):
    # Disable SSL Warnings when using self-signed certificates
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    # API
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
    print ("dentro antes do if parameter")
    if PARAMETER == "memory_use_percent":
        memory_mb_used=stats['memory_mb_used']
        memory_mb=stats['memory_mb']
        memory_use_percent=(memory_mb_used*100)/memory_mb
        return str(round(memory_use_percent))

    if PARAMETER == "vcpu_use_percent":
        vcpus=stats['vcpus']
        vcpus_used=stats['vcpus_used']        
        vcpu_use_percent=(vcpus_used*100)/vcpus
        print("PASSOU PERCENT CPU")
        return str(round(vcpu_use_percent))

    if PARAMETER == "local_gb_percent":
        local_gb=stats['local_gb']
        local_gb_used=stats['local_gb_used']       
        local_gb_percent=(local_gb_used*100)/local_gb
        return str(round(local_gb_percent))

    if PARAMETER == "running_vms":
        running_vms=stats['running_vms']
        return str(round(running_vms))

    #print(GetHypervisorStats("memory_use_percent"))
    #print(GetHypervisorStats("vcpu_use_percent"))
    #print(GetHypervisorStats("running_vms"))
    #print(GetHypervisorStats("local_gb_percent"))


def GetLatency(TARGET,QUANTITY_PCK):
    #Test with ping to get latency.
    if platform.system().lower() == "linux":
        try:
            ping = subprocess.check_output(["ping", "-c", QUANTITY_PCK, TARGET])
        except:
            return "" #if return with error, return empty
        latency = ping.split()[-2]
        resp = str(latency, 'utf-8')
        resp2= resp.split("/")[2]
        return resp2
    else: # platform.system().lower() == "windows":
        try:
            ping = subprocess.check_output(["ping", "-n", QUANTITY_PCK, TARGET])
        except:
            return "" #if return with error, return empty
        latency = ping.split()[-1]
        resp = str(latency, 'utf-8')
        print (resp)
        resp2= resp.split("=")[0]
        resp3=resp2.split("ms")[0]
        return resp3

def OpenStackHypervisorStats(): #criar file hypervisor_stats.txt in openstack directory
    adminrc = subprocess.run(["source", "admin.rc"]) 
    hypervisorStats = subprocess.check_output(["openstack", "hypervisor", "stats", "show"])      
    print (hypervisorStats)
    return hypervisorStats

def GetJitter(CLOUDTOIP,QUANTITY_PCK,STATUS):
    if STATUS == "CLIENT":
        iperf = subprocess.run(["iperf3", "-s", "-1", "-D"])
        iperf2 = subprocess.check_output(["iperf3", "-c", CLOUDTOIP,"-u", "-t", QUANTITY_PCK])
        jitter = iperf2.split()[-11]
        print (jitter)
        resp = str(jitter, 'utf-8')
        return resp
    if STATUS == "SERVER":
        iperf = subprocess.check_output(["iperf3", "-c", CLOUDTOIP,"-u", "-t", QUANTITY_PCK])
        iperf = subprocess.run(["iperf3", "-s", "-1", "-D"])        
        #iperf = subprocess.check_output([DIR_IPERF+"iperf3", "-c", CLOUDTOIP,"-u", "-t", QUANTITY_PCK])
        jitter = iperf.split()[-11]
        print (jitter)
        resp = str(jitter, 'utf-8')
        return resp

ID_CONF="" #Local variable with uniq identifier cloud

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST,PORT)
tcp.connect(dest)

print ('Starting OSM collector ... '+ CLOUDNAME_LOCAL)
print ('To quit, use CTRL+C\n')

#First comunication with the server
mensagem = 'REGIS' + '#' + 'ID' + '#' +CLOUDNAME_LOCAL + '#' + CLOUDIP_LOCAL + '#' + 'DATAHORAC()' + '#' + 'CLOUDTONAME' + '#' + 'CLOUDTOIP' + '#' + 'STATUS' + '#' + 'PRICE' + '#' + 'LATENCY' + '#' + 'JITTER' + '#' + '0' + '#' + 'MEMORY' + '#'
tcp.sendall(mensagem.encode('utf8')) #Sending to Server
print ('DEGUG: Sent first REGIS')

try:
    #desligar = False
    while True; #desligar == False:
        msg = tcp.recv(1024).decode("utf8")  #receive the message socket in byte and to convert in utf-8
        msg = msg.split('#')  #split message separeted in # symbol
        if len(msg) > 5:
            #       REGIS - First comunication between server and client for register the cloud
            #       SENDS - Send information to Server
            #       SENDC - Send command to client
            TIPO = msg[0] 
            ID = msg[1]
            CLOUD = msg[2] #NAME CLOUD
            CLOUDIP = msg[3] #IP CLOUD
            DATEHOUR = msg[4] #DATA AND HOUR
            CLOUDTONAME = msg[5] #NAME OF CLOUD TO
            CLOUDTOIP = msg[6] #IP OF CLOUD TO
            STATUS = msg[7] #SERVER OR CLIENT
            PRICE = msg[8] #PRICE
            LATENCY = msg[9] #LATENCY
            JITTER = msg[10] #JITTER
            CPU = msg[11] #CPU
            MEMORY = msg[12] #MEMORY

            if TIPO == 'REGIS':  #check if the protocol is type registry
                print ("DEBUG: recebido comando do servidor com registro")
                print(TIPO+ID+CLOUD+CLOUDIP+DATEHOUR+CLOUDTONAME,CLOUDTONAME,STATUS)
                if ID != 'ID':
                    ID_CONF = ID  #Store ID in global variable
                    print("DEBUG: ID stored")
            if ID_CONF == ID:
                if TIPO == 'REGIS':
                    mensagem = 'SENDS#' + ID + '#' + CLOUD + '#' + CLOUDIP + '#' + DATAHORAC() + '#' + CLOUDTONAME + '#' + CLOUDTOIP + '#' + STATUS + '#' + PRICE + '#' + LATENCY + '#' + JITTER + '#' + CPU + '#' + MEMORY + '#'
                    tcp.sendall(mensagem.encode('utf8'))
                if TIPO == 'SENDC':
                    if CLOUDIP_LOCAL == CLOUDIP:
                        print(CLOUDTOIP)
                        #if STATUS == 'SERVER':
                        print('DEBUG: Command received, exec iperf SERVER')
                        time.sleep(5)
                        if (CLOUDTOIP != "CLOUDTOIP"):
                            LATENCY=str(round(float(GetLatency(CLOUDTOIP,QUANTITY_PCK)))) #Get latency with ping, is necessary set quantity packages
                            PRICE=LATENCY
                            JITTER=str(round(float(GetJitter(CLOUDTOIP,QUANTITY_PCK,STATUS)))) #Get Jitter with iperf, is necessary set quantity packages
                        CPU=GetHypervisorStats(CLOUDIP,"vcpu_use_percent")
                        MEMORY=''
                        mensagem = 'SENDS#' + ID + '#' + CLOUD + '#' + CLOUDIP + '#' + DATAHORAC() + '#' + CLOUDTONAME + '#' + CLOUDTOIP + '#' + STATUS + '#' + PRICE + '#' + LATENCY + '#' + JITTER + '#' + CPU + '#' + MEMORY + '#'
                        print (mensagem)
                        tcp.sendall(mensagem.encode('utf8')) #send to server colletion data
                         '''   
                        if STATUS == 'CLIENT':
                            print('DEBUG: Command received, exec iperf CLIENT')
                            time.sleep(5)
                            PRICE='' #In first time, in example case, the server is openstack1 and client openstack2. Is not necessary this colletc.
                            LATENCY='' #In first time, in example case, the server is openstack1 and client openstack2. Is not necessary this colletc.
                            GetJitter(CLOUDTOIP,QUANTITY_PCK,STATUS) #Start Jitter as daemon for receive 1 conection, is necessary set quantity packages
                            JITTER="" #The client going to collect this
                            CPU=GetHypervisorStats(CLOUDIP,"vcpu_use_percent")
                            print("CPU: "+CPU)
                            MEMORY=''
                            mensagem = 'SENDS#' + ID + '#' + CLOUD + '#' + CLOUDIP + '#' + DATAHORAC() + '#' + CLOUDTONAME + '#' + CLOUDTOIP + '#' + STATUS + '#' + PRICE + '#' + LATENCY + '#' + JITTER + '#' + CPU + '#' + MEMORY + '#'
                            print (mensagem)
                            tcp.sendall(mensagem.encode('utf8'))  #send to server colletion data
                        else:
                            mensagem = 'SENDS#' + ID + '#' + CLOUD + '#' + CLOUDIP + '#' + DATAHORAC() + '#' + CLOUDTONAME + '#' + CLOUDTOIP + '#' + STATUS + '#' + PRICE + '#' + LATENCY + '#' + JITTER + '#' + CPU + '#' + MEMORY + '#'
                            print (mensagem)
                            tcp.sendall(mensagem.encode('utf8'))  #send to server colletion data
                            '''
        if not msg: break
except KeyboardInterrupt:
    print('Tecla de interrupção acionada, saindo... e solicitando exclusao do dispositivo no servidor.')
except Exception as e:
    print("Erro no cliente. " + str(e))
finally:
    mensagem = 'EXCL#' + ID + '#' + CLOUD + '#' + CLOUDIP + '#' + 'DATAHORAC()' + '#' + 'CLOUDTONAME' + '#' + 'CLOUDTOIP' + '#' + 'STATUS' + '#' + 'PRICE' + '#' +'LATENCY' + '#' + 'JITTER' + '#' + 'CPU' + '#' + 'MEMORY' + '#'
    tcp.sendall(mensagem.encode('utf8'))
    tcp.close()