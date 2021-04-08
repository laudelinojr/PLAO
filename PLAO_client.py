import socket
import time
import sys
import datetime
import platform
import subprocess
import psutil

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

#Debug mode is 1
debug=0

# The values in config files of OSM need to be integer
QUANTITY_PCK="5" #Quantity packages to use in ping command 
DIR_IPERF="C:/Temp/artigo/utils/iperf/" #directory of iperf application

HOST = sys.argv[1] #Address Server OSM IP
if sys.argv[1] == '':
    print ("Invalido: We need the IP OSM Sever.")
    exit()

PORT = 6000 #Port Server
CLOUDNAME_LOCAL = sys.argv[2] #Cloud Name, this may equal in PLA configuration files (pil_price_list.yaml and vnf_price_list.yaml)
if sys.argv[2] == '':
    print ("Invalido: We need cloud name. Equal in PLA configuration files (pil_price_list.yaml and vnf_price_list.yaml) for OSM.")
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
    #print ("dentro antes do if parameter")
    if PARAMETER == "memory_use_percent":
        memory_mb_used=stats['memory_mb_used']
        memory_mb=stats['memory_mb']
        memory_use_percent=(memory_mb_used*100)/memory_mb
        return str(round(memory_use_percent))

    if PARAMETER == "vcpu_use_percent":
        vcpus=stats['vcpus']
        vcpus_used=stats['vcpus_used']        
        vcpu_use_percent=(vcpus_used*100)/vcpus
        return str(round(vcpu_use_percent))

    if PARAMETER == "local_gb_percent":
        local_gb=stats['local_gb']
        local_gb_used=stats['local_gb_used']       
        local_gb_percent=(local_gb_used*100)/local_gb
        return str(round(local_gb_percent))

    if PARAMETER == "running_vms":
        running_vms=stats['running_vms']
        return str(round(running_vms))

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
        resp2= resp.split("=")[0]
        resp3=resp2.split("ms")[0]
        return resp3

def GetCpuSO():
    cpuso = psutil.cpu_percent(interval=0.5)
    cpuso2 = round(cpuso)
    return str(cpuso2)

def MemorySO():
    mem = psutil.virtual_memory()
    memoryso = round(mem.percent)
    return str(memoryso)

def GetJitter(CLOUDTOIP,QUANTITY_PCK,STATUS):
    #if STATUS == "CLIENT":
    #iperf = subprocess.run(["iperf3", "-s", "-1", "-D"])
    try:
        iperf2 = subprocess.check_output(["iperf3", "-c", CLOUDTOIP,"-u", "-t", QUANTITY_PCK])
    except:
        return -1
    jitter = iperf2.split()[-7]
    resp = str(jitter, 'utf-8')
    print(resp)
    return resp
    #if STATUS == "SERVER":
    #    iperf = subprocess.check_output(["iperf3", "-c", CLOUDTOIP,"-u", "-t", QUANTITY_PCK])
    #    iperf2 = subprocess.run(["iperf3", "-s", "-1", "-D"])        
    #    #iperf = subprocess.check_output([DIR_IPERF+"iperf3", "-c", CLOUDTOIP,"-u", "-t", QUANTITY_PCK])
    #    jitter = iperf.split()[-11]
    #    print (jitter)
    #    resp = str(jitter, 'utf-8')
    #    return resp

ID_CONF="" #Local variable with uniq identifier cloud

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST,PORT)
tcp.connect(dest)

print ('Starting OSM collector ... '+ CLOUDNAME_LOCAL)
print ('To quit, use CTRL+C\n')

#First comunication with the server
mensagem = 'REGIS' + '#' + 'ID' + '#' +CLOUDNAME_LOCAL + '#' + CLOUDIP_LOCAL + '#' + 'DATAHORAC()' + '#' + 'CLOUDTONAME' + '#' + 'CLOUDTOIP' + '#' + 'STATUS' + '#' + 'PRICE' + '#' + 'LATENCY' + '#' + '0' + '#' + '0' + '#' + 'MEMORY'+ '#' + 'DISK'+ '#' + 'NVM' + '#' + '0' + '#' + 'MEMORYC' + '#' + 'DISKC' + '#'+ 'EXTRA' + '#'+ 'EXTRA2' + '#' + 'EXTRA3' + '#'
tcp.sendall(mensagem.encode('utf8')) #Sending to Server

try:
    while True:
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
            DATEHOUR = msg[4] #DATA AND HOUR COLLETC IN CLIENT
            CLOUDTONAME = msg[5] #NAME OF CLOUD TO
            CLOUDTOIP = msg[6] #IP OF CLOUD TO
            STATUS = msg[7] #SERVER OR CLIENT
            PRICE = msg[8] #PRICE
            LATENCY = msg[9] #LATENCY
            JITTER = msg[10] #JITTER
            CPU = msg[11] #CPU PERCENT USAGE
            MEMORY = msg[12] #MEMORY PERCENT USAGE
            DISK = msg[13] #DISK PERCENT USAGE
            NVM = msg[14] #QUANTITY MACHINES
            CPUC = msg[15] #PERCENT CPU IN TOTAL OF CLOUD
            MEMORYC = msg[16] #PERCENT CPU IN TOTAL OF CLOUD
            DISKC = msg[17] #PERCENT CPU IN TOTAL OF CLOUD
            EXTRA = msg[18] #ADDRESS IP FOR TEST LATENCY
            EXTRA2 = msg[19] #VNFDS
            EXTRA3 = msg[20] #LATENCY IN CLIENT

            #print ('TIPO: '+TIPO+' CLOUD: '+CLOUD+' CLOUDIP: '+CLOUDIP+' DATEHOUR: '+DATEHOUR+' CLOUDTONAME: '+CLOUDTONAME+' CLOUDTOIP: '+CLOUDTOIP+' STATUS: '+STATUS+' PRICE: '+PRICE+' LATENCY: '+LATENCY+' JITTER: '+JITTER+' CPU: '+CPU+' MEMORY: '+MEMORY+' DISK: '+DISK+' NVM: '+NVM+' CPUC: '+CPUC+' MEMORYC: '+MEMORYC+' DISKC: '+DISKC)
            print (TIPO+'#'+CLOUD+'#'+CLOUDIP+'#'+DATEHOUR+'#'+CLOUDTONAME+'#'+CLOUDTOIP+'#'+STATUS+'#'+PRICE+'#'+LATENCY+'#'+JITTER+'#'+CPU+'#'+MEMORY+'#'+DISK+'#'+NVM+'#'+CPUC+'#'+MEMORYC+'#'+'#'+DISKC+'#' +EXTRA+'#'+EXTRA2+'#'+EXTRA3+'#' )
            if TIPO == 'REGIS':  #check if the protocol is type registry
                #print ("DEBUG: recebido comando do servidor com registro")
                #print(TIPO+ID+CLOUD+CLOUDIP+DATEHOUR+CLOUDTONAME,CLOUDTONAME,STATUS)
                if ID != 'ID':
                    ID_CONF = ID  #Store ID in global variable
                    #print("DEBUG: ID stored")
            if ID_CONF == ID:
                if TIPO == 'REGIS':
                    mensagem = 'SENDS#' + ID + '#' + CLOUD + '#' + CLOUDIP + '#' + DATAHORAC() + '#' + CLOUDTONAME + '#' + CLOUDTOIP + '#' + STATUS + '#' + PRICE + '#' + LATENCY + '#' + JITTER + '#' + CPU + '#' + MEMORY + '#' + DISK + '#' + NVM + '#' + CPUC + '#' + MEMORYC + '#' + DISKC + '#'  + EXTRA + '#'+ EXTRA2 + '#'+ EXTRA3 + '#'
                    tcp.sendall(mensagem.encode('utf8'))
                if TIPO == 'SENDC':
                    if CLOUDIP_LOCAL == CLOUDIP:
                        #time.sleep(1)
                        if( (EXTRA != "EXTRA") and (len(EXTRA)!=0) ):
                            print("COLLECT LATENCY TO VNF CLIENT: "+ EXTRA)
                            EXTRA3=str(round(float(GetLatency(EXTRA,QUANTITY_PCK)))) #Get latency with ping, is necessary set quantity packages
                        if (CLOUDTOIP != "CLOUDTOIP" ):
                            LATENCY=str(round(float(GetLatency(CLOUDTOIP,QUANTITY_PCK)))) #Get latency with ping, is necessary set quantity packages
                            PRICE=LATENCY
                            if (CLOUDTOIP ==  "10.159.205.7"):
                                JITTER=str(round(float(GetJitter(CLOUDTOIP,QUANTITY_PCK,STATUS)))) #Get Jitter with iperf, is necessary set quantity packages
                        CPU=GetCpuSO()
                        NVM=GetHypervisorStats(CLOUDIP,"running_vms")                       
                        CPUC=GetHypervisorStats(CLOUDIP,"vcpu_use_percent")
                        MEMORY=MemorySO()
                        MEMORYC=GetHypervisorStats(CLOUDIP,"memory_use_percent")
                        DISKC=GetHypervisorStats(CLOUDIP,"local_gb_percent")
                        mensagem = 'SENDS#' + ID + '#' + CLOUD + '#' + CLOUDIP + '#' + DATAHORAC() + '#' + CLOUDTONAME + '#' + CLOUDTOIP + '#' + STATUS + '#' + PRICE + '#' + LATENCY + '#' + JITTER + '#' + CPU + '#' + MEMORY + '#' + DISK + '#' + NVM + '#' + CPUC + '#' + MEMORYC + '#' + DISKC + '#' + EXTRA + '#'+ EXTRA2 + '#'+ EXTRA3 + '#'
                        print(mensagem)
                        tcp.sendall(mensagem.encode('utf8')) #send to server colletion data
        if not msg: break
except KeyboardInterrupt:
    print('Tecla de interrupção acionada, saindo... e solicitando exclusao do dispositivo no servidor.')
except Exception as e:
    print("Erro no cliente. " + str(e))
finally:
    mensagem = 'EXCL#' + ID + '#' + CLOUD + '#' + CLOUDIP + '#' + 'DATAHORAC()' + '#' + 'CLOUDTONAME' + '#' + 'CLOUDTOIP' + '#' + 'STATUS' + '#' + 'PRICE' + '#' +'LATENCY' + '#' + 'JITTER' + '#' + 'CPU' + '#' + 'MEMORY'+ '#' + 'DISK'+ '#' + 'NVM' + '#' + 'CPUC' + '#' + 'MEMORYC' + '#' + 'DISKC' + '#' + 'EXTRA' + '#'+ 'EXTRA2' + '#'+ 'EXTRA3' + '#'
    tcp.sendall(mensagem.encode('utf8'))
    tcp.close()