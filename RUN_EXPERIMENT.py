import subprocess
import time
import requests
import json
import yaml
import requests
import os
requests.packages.urllib3.disable_warnings() 

INTERVALO_EXPERIMENTO=120
debug_file=1
OSM_IP='10.159.205.10'
COMANDO = []

def getoken():
    url = 'https://'+OSM_IP+':9999/osm/admin/v1/tokens'

    headers = {
    'Content-Type': 'application/json'
    }
    payload = {
        "username": 'admin',
        "password": 'admin',
        "project_id": 'admin'
    }

    response = requests.request("POST", url, headers=headers, json=payload,verify=False)
    #print(response.text)

    a=response.text
    B=yaml.full_load(a)
    return B['_id']

def getlistaNS(tokencoletado):
    url = 'https://'+OSM_IP+':9999/osm/nslcm/v1/vnf_instances'
    payload={}

    token=tokencoletado

    headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    "Authorization": 'Bearer ' + token
                }

    response = requests.request("GET", url, headers=headers, verify=False)
    #print(response.text)

    a=response.text
    b=json.loads(a)  #B eh um grande dicionario
    c=(len(b))
    lista_ns = []
    lista_ns_norepeated = []
    #print(b[0]['nsr-id-ref'])
    #print(b[0]['ip-address'])
    #nsr-id-ref

    #for i in range(len(b)):
    #    print(b[i]['ip-address'])

    #Get NS list
    for i in range(len(b)):
        identifier=(b[i]['nsr-id-ref'])
        #print(identifier)
        lista_ns.insert(i,identifier) 

    lista_ns_norepeated = lista_ns
    i = 0
    while i < len(lista_ns_norepeated): #To delete repeted itens
        j = i + 1
        while j < len(lista_ns_norepeated):
            if lista_ns_norepeated[j] == lista_ns_norepeated[i]:
                del(lista_ns_norepeated[j])
            else:
                j = j + 1
        i = i + 1
    return(lista_ns_norepeated)
  
def deleteAllNS(lista):
    for i in range(len(lista)):
        ExecuteCommand('osm ns-delete '+ lista[i])
        print("Removendo NS: "+lista[i])

def ExecuteCommand(exec_command):
#    try:
    print (exec_command)
    ret = subprocess.run(exec_command, universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
    #    if debug_file == 1:
    #        print("DEBUG ON")
    #        print("CMD - " + exec_command)
    #        print("RETURN - \n" + ret.stdout)
    #    return ret.returncode
    #except:
    #    print('FAIL IN COMMAND EXECUTE')
    #    print("CMD - " + exec_command)
    #    print("ERROR - " + ret)
    return ret.returncode

#'for pid in $(ps -ef | grep "PLAO_client.py" | awk '+"'"+'{print $2}'+"'"+'); do kill -9 $pid; done ; cd /opt/PLAO ; git pull; rm -rf log/*; python3 PLAO.py > /dev/null 2>&1 &'
os.system('python3 /opt/PLAO/PLAO.py > /dev/null 2>&1 &')
os.system('ssh root@10.159.205.6 python3 /opt/PLAO/PLAO_client.py 10.159.205.10 openstack1 10.159.205.6 > /dev/null 2>&1 &')
os.system('ssh root@10.159.205.12 python3 /opt/PLAO/PLAO_client.py 10.159.205.10 openstack1 10.159.205.12 > /dev/null 2>&1 &')
os.system('python3 USER_TEST.py 1a')
#COMANDO.insert(0, 'python3 /opt/PLAO/PLAO.py > /dev/null 2>&1 &')
#COMANDO.insert(1,'ssh root@10.159.205.6 '+"'"+ 'python3 /opt/PLAO/PLAO_client.py 10.159.205.10 openstack1 10.159.205.6 > /dev/null 2>&1 &'+"'")
#COMANDO.insert(2,'ssh root@10.159.205.12'+"'"+' python3 /opt/PLAO/PLAO_client.py 10.159.205.10 openstack1 10.159.205.12 > /dev/null 2>&1 &'+"'")
#COMANDO.insert(3,'python3 USER_TEST.py 1a') #Create NS with 2 VNFD using PLA module OSM sem latencia do usuario

#for i in range(len(COMANDO)):
#    print ("Executando comando: "+str(i))
#    ExecuteCommand(COMANDO[i])
#    time.sleep(2)
print('vamos aguardar'+str(INTERVALO_EXPERIMENTO)+' segundos.')
time.sleep(INTERVALO_EXPERIMENTO)
print('Finalizando cenário1, excluir NSs')
print('Collecting token access in OSM.')
print('Collecting NS itens')
print('Token Gerado: '+getoken())
print('Lista de NS: ')
print (getlistaNS(getoken()))
print('Removendo todas as NSs: ')
deleteAllNS(getlistaNS(getoken()))