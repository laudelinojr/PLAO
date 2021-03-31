import subprocess
import time
import requests
import json
import yaml
import requests
import os
import datetime
requests.packages.urllib3.disable_warnings() 

INTERVALO_EXPERIMENTO=180
INTERVALO_DESCANSO_EXPERIMENTO=30
debug_file=1
OSM_IP='10.159.205.10'
PATH_LOG='/opt/PLAO/log/'

def DATEHOURS():
    DATEHOUR = datetime.datetime.now().strftime('%d.%m.%y-%H:%M:%S')  # converte hora para string do cliente
    return DATEHOUR
    
def RegisterLOGLaunch(OPERACAO):
    nomearquivo1=PATH_LOG+'LAUCH_OSM_history.txt' #write data in file
    with open(nomearquivo1, 'a') as arquivo:
        arquivo.write(DATEHOURS() +","+ OPERACAO +'\n')

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
    for i in range(len(b)):
        identifier=(b[i]['nsr-id-ref'])
        #print(identifier)#
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

print("### Cenario 1###")
print("Incluindo simulacao Latencia 5")
ExecuteCommand("for pid in $(ps -ef | grep 'PLAO.py' | awk '{print $2}'); do kill -9 $pid; done")
ExecuteCommand("ssh root@10.159.205.6 'for pid in $(ps -ef | grep 'PLAO_client.py' | awk '\\''{print $2}'\\''); do kill -9 $pid; done'") 
ExecuteCommand("ssh root@10.159.205.12 'for pid in $(ps -ef | grep 'PLAO_client.py' | awk '\\''{print $2}'\\''); do kill -9 $pid; done'") 
ExecuteCommand("ssh root@10.159.205.6 'tc qdisc add dev eth0 root netem delay 5ms'")
ExecuteCommand("cd /opt/PLAO; git pull; rm -rf /opt/PLAO/log/* ; python3 /opt/PLAO/PLAO.py > /dev/null 2>&1 &")
time.sleep(10)
ExecuteCommand("ssh root@10.159.205.6 'cd /opt/PLAO; git pull; python3 /opt/PLAO/PLAO_client.py 10.159.205.10 openstack1 10.159.205.6 > /dev/null 2>&1 &'")
ExecuteCommand("ssh root@10.159.205.12 'cd /opt/PLAO; git pull; python3 /opt/PLAO/PLAO_client.py 10.159.205.10 openstack2 10.159.205.12 > /dev/null 2>&1 &'")
time.sleep(30) #Delay link irá para 15, aguardando nova coleta.
ExecuteCommand("python3 USER_TEST.py 1a") #Create NS with 2 VNFD using PLA module OSM sem latencia do usuario
print('vamos aguardar '+str(INTERVALO_EXPERIMENTO)+' segundos.')
time.sleep(INTERVALO_EXPERIMENTO)
print('Finalizando cenário1, excluir NSs')
print('Collecting token access in OSM.')
print('Collecting NS itens')
print('Token Gerado: '+getoken())
print('Lista de NS: ')
print (getlistaNS(getoken()))
print('Removendo todas as NSs: ')
deleteAllNS(getlistaNS(getoken()))
ExecuteCommand("ssh root@10.159.205.6 'for pid in $(ps -ef | grep 'PLAO_client.py' | awk '\\''{print $2}'\\''); do kill -9 $pid; done'") 
ExecuteCommand("ssh root@10.159.205.12 'for pid in $(ps -ef | grep 'PLAO_client.py' | awk '\\''{print $2}'\\''); do kill -9 $pid; done'") 
ExecuteCommand("for pid in $(ps -ef | grep 'PLAO.py' | awk '{print $2}'); do kill -9 $pid; done")
RegisterLOGLaunch('REMOVING')
#print("Coletando logs.")
#ExecuteCommand("mkdir -p /opt/PLAO/exp/1; mv /opt/PLAO/log/* /opt/PLAO/exp/1  ")
print("Intervalo descanso Experimento")
time.sleep(INTERVALO_DESCANSO_EXPERIMENTO)

print("### Cenario 2###")
print("Excluindo simulacao de latencia")
ExecuteCommand("ssh root@10.159.205.6 'tc qdisc del dev eth0 root'")
ExecuteCommand("ssh root@10.159.205.6 'tc qdisc add dev eth0 root netem delay 15ms'")
ExecuteCommand("cd /opt/PLAO; python3 /opt/PLAO/PLAO.py > /dev/null 2>&1 &")
time.sleep(10)
ExecuteCommand("ssh root@10.159.205.6 'cd /opt/PLAO; git pull; python3 /opt/PLAO/PLAO_client.py 10.159.205.10 openstack1 10.159.205.6 > /dev/null 2>&1 &'")
ExecuteCommand("ssh root@10.159.205.12 'cd /opt/PLAO; git pull; python3 /opt/PLAO/PLAO_client.py 10.159.205.10 openstack2 10.159.205.12 > /dev/null 2>&1 &'")
print("Delay link irá para 15, aguardando nova coleta.")
time.sleep(30) #Aguardando nova coleta para alterar dinamicamente a pontuacao do link
ExecuteCommand("python3 USER_TEST.py 1a") #Create NS with 2 VNFD using PLA module OSM sem latencia do usuario
print("Instanciado NS com nova pontuação")
print('vamos aguardar '+str(INTERVALO_EXPERIMENTO)+' segundos.')
time.sleep(INTERVALO_EXPERIMENTO)
print('Finalizando cenário1, excluir NSs')
print('Collecting token access in OSM.')
print('Collecting NS itens')
print('Token Gerado: '+getoken())
print('Lista de NS: ')
print (getlistaNS(getoken()))
print('Removendo todas as NSs: ')
deleteAllNS(getlistaNS(getoken()))
RegisterLOGLaunch('REMOVING')
ExecuteCommand("ssh root@10.159.205.6 'for pid in $(ps -ef | grep 'PLAO_client.py' | awk '\\''{print $2}'\\''); do kill -9 $pid; done'") 
ExecuteCommand("ssh root@10.159.205.12 'for pid in $(ps -ef | grep 'PLAO_client.py' | awk '\\''{print $2}'\\''); do kill -9 $pid; done'") 
ExecuteCommand("for pid in $(ps -ef | grep 'PLAO.py' | awk '{print $2}'); do kill -9 $pid; done")
print("Intervalo descanso Experimento")
time.sleep(INTERVALO_DESCANSO_EXPERIMENTO)


print("### Cenario 3 - igual ao Cenario 1 ###")
print("Excluindo simulacao de latencia")
ExecuteCommand("ssh root@10.159.205.6 'tc qdisc del dev eth0 root'")
print("Incluindo simulacao Latencia 5")
ExecuteCommand("ssh root@10.159.205.6 'tc qdisc add dev eth0 root netem delay 5ms'")
ExecuteCommand("cd /opt/PLAO; python3 /opt/PLAO/PLAO.py > /dev/null 2>&1 &")
time.sleep(10)
ExecuteCommand("ssh root@10.159.205.6 'cd /opt/PLAO; git pull; python3 /opt/PLAO/PLAO_client.py 10.159.205.10 openstack1 10.159.205.6 > /dev/null 2>&1 &'")
ExecuteCommand("ssh root@10.159.205.12 'cd /opt/PLAO; git pull; python3 /opt/PLAO/PLAO_client.py 10.159.205.10 openstack2 10.159.205.12 > /dev/null 2>&1 &'")
print("Delay link irá para 5, aguardando nova coleta.")
time.sleep(30) #Aguardando nova coleta para alterar dinamicamente a pontuacao do link
ExecuteCommand("python3 USER_TEST.py 1a") #Create NS with 2 VNFD using PLA module OSM sem latencia do usuario
print('vamos aguardar '+str(INTERVALO_EXPERIMENTO)+' segundos.')
time.sleep(INTERVALO_EXPERIMENTO)
print('Finalizando cenário1, excluir NSs')
print('Collecting token access in OSM.')
print('Collecting NS itens')
print('Token Gerado: '+getoken())
print('Lista de NS: ')
print (getlistaNS(getoken()))
print('Removendo todas as NSs: ')
deleteAllNS(getlistaNS(getoken()))
RegisterLOGLaunch('REMOVING')
ExecuteCommand("ssh root@10.159.205.6 'for pid in $(ps -ef | grep 'PLAO_client.py' | awk '\\''{print $2}'\\''); do kill -9 $pid; done'") 
ExecuteCommand("ssh root@10.159.205.12 'for pid in $(ps -ef | grep 'PLAO_client.py' | awk '\\''{print $2}'\\''); do kill -9 $pid; done'") 
ExecuteCommand("for pid in $(ps -ef | grep 'PLAO.py' | awk '{print $2}'); do kill -9 $pid; done")
#print("Coletando logs.")
#ExecuteCommand("mkdir -p /opt/PLAO/exp/3; mv /opt/PLAO/log/* /opt/PLAO/exp/3  ")

print("Intervalo descanso Experimento")
time.sleep(INTERVALO_DESCANSO_EXPERIMENTO)

print("### Cenario 4 ###")
ExecuteCommand("cd /opt/PLAO; python3 /opt/PLAO/PLAO.py > /dev/null 2>&1 &")
time.sleep(10)
ExecuteCommand("ssh root@10.159.205.6 'cd /opt/PLAO; git pull; python3 /opt/PLAO/PLAO_client.py 10.159.205.10 openstack1 10.159.205.6 > /dev/null 2>&1 &'")
ExecuteCommand("ssh root@10.159.205.12 'cd /opt/PLAO; git pull; python3 /opt/PLAO/PLAO_client.py 10.159.205.10 openstack2 10.159.205.12 > /dev/null 2>&1 &'")
time.sleep(30) #Aguardando para ficar com mesmo tempo dos outros cenários
ExecuteCommand("python3 USER_TEST.py 3a") #Create NS with 2 VNFD using PLA module OSM sem latencia do usuario
print('vamos aguardar '+str(INTERVALO_EXPERIMENTO)+' segundos.')
time.sleep(INTERVALO_EXPERIMENTO)
print('Finalizando cenário1, excluir NSs')
print('Collecting token access in OSM.')
print('Collecting NS itens')
print('Token Gerado: '+getoken())
print('Lista de NS: ')
print (getlistaNS(getoken()))
print('Removendo todas as NSs: ')
deleteAllNS(getlistaNS(getoken()))
RegisterLOGLaunch('REMOVING')
ExecuteCommand("ssh root@10.159.205.6 'for pid in $(ps -ef | grep 'PLAO_client.py' | awk '\\''{print $2}'\\''); do kill -9 $pid; done'") 
ExecuteCommand("ssh root@10.159.205.12 'for pid in $(ps -ef | grep 'PLAO_client.py' | awk '\\''{print $2}'\\''); do kill -9 $pid; done'") 
ExecuteCommand("for pid in $(ps -ef | grep 'PLAO.py' | awk '{print $2}'); do kill -9 $pid; done")
#print("Coletando logs.")
#ExecuteCommand("mkdir -p /opt/PLAO/exp/4; mv /opt/PLAO/log/* /opt/PLAO/exp/4  ")
print("Intervalo descanso Experimento")
time.sleep(INTERVALO_DESCANSO_EXPERIMENTO)


print("### Cenario 5 ###")   #Aumentar quantidade de Maquinas virtuais na nuvem
ExecuteCommand("cd /opt/PLAO; python3 /opt/PLAO/PLAO.py > /dev/null 2>&1 &")
time.sleep(10)
ExecuteCommand("ssh root@10.159.205.6 'cd /opt/PLAO; git pull; python3 /opt/PLAO/PLAO_client.py 10.159.205.10 openstack1 10.159.205.6 > /dev/null 2>&1 &'")
ExecuteCommand("ssh root@10.159.205.12 'cd /opt/PLAO; git pull; python3 /opt/PLAO/PLAO_client.py 10.159.205.10 openstack2 10.159.205.12 > /dev/null 2>&1 &'")
print("Incluindo simulacao Latencia 5")
time.sleep(30) #Aguardando nova coleta para alterar dinamicamente a pontuacao do link
ExecuteCommand("python3 USER_TEST.py 3a") #Create NS with 2 VNFD using PLA module OSM sem latencia do usuario
ExecuteCommand("python3 USER_TEST.py 3a") #Create NS with 2 VNFD using PLA module OSM sem latencia do usuario
ExecuteCommand("python3 USER_TEST.py 3a") #Create NS with 2 VNFD using PLA module OSM sem latencia do usuario
ExecuteCommand("python3 USER_TEST.py 3a") #Create NS with 2 VNFD using PLA module OSM sem latencia do usuario
print('vamos aguardar '+str(INTERVALO_EXPERIMENTO)+' segundos.')
time.sleep(INTERVALO_EXPERIMENTO)
print('Finalizando cenário1, excluir NSs')
print('Collecting token access in OSM.')
print('Collecting NS itens')
print('Token Gerado: '+getoken())
print('Lista de NS: ')
print (getlistaNS(getoken()))
print('Removendo todas as NSs: ')
deleteAllNS(getlistaNS(getoken()))
RegisterLOGLaunch('REMOVING')
ExecuteCommand("ssh root@10.159.205.6 'for pid in $(ps -ef | grep 'PLAO_client.py' | awk '\\''{print $2}'\\''); do kill -9 $pid; done'") 
ExecuteCommand("ssh root@10.159.205.12 'for pid in $(ps -ef | grep 'PLAO_client.py' | awk '\\''{print $2}'\\''); do kill -9 $pid; done'") 
ExecuteCommand("for pid in $(ps -ef | grep 'PLAO.py' | awk '{print $2}'); do kill -9 $pid; done")
#print("Coletando logs.")
#ExecuteCommand("mkdir -p /opt/PLAO/exp/5; mv /opt/PLAO/log/* /opt/PLAO/exp/5  ")
print("Intervalo descanso Experimento")
time.sleep(INTERVALO_DESCANSO_EXPERIMENTO)


print("### Cenario 6 ###")   #Aumentar quantidade de CPU usada no SO com nstress
print("Incluindo simulacao Latencia 6")
ExecuteCommand("ssh root@10.159.205.6 'tc qdisc add dev eth0 root netem delay 5ms'")
print('Simulando aumento de CPU Cloud 1')
ExecuteCommand("cd /opt/PLAO; python3 /opt/PLAO/PLAO.py > /dev/null 2>&1 &")
time.sleep(10)
ExecuteCommand("ssh root@10.159.205.6 'cd /opt/PLAO; git pull; python3 /opt/PLAO/PLAO_client.py 10.159.205.10 openstack1 10.159.205.6 > /dev/null 2>&1 &'")
ExecuteCommand("ssh root@10.159.205.12 'cd /opt/PLAO; git pull; python3 /opt/PLAO/PLAO_client.py 10.159.205.10 openstack2 10.159.205.12 > /dev/null 2>&1 &'")
ExecuteCommand("ssh root@10.159.205.6 'stress-ng --cpu 1 > /dev/null 2>&1 &'")
time.sleep(30) #Aguardando nova coleta para alterar dinamicamente a pontuacao do link e cpu
ExecuteCommand("python3 USER_TEST.py 3a") #Create NS with 2 VNFD using PLA module OSM sem latencia do usuario
print('vamos aguardar '+str(INTERVALO_EXPERIMENTO)+' segundos.')
time.sleep(INTERVALO_EXPERIMENTO)
print('Finalizando cenário1, excluir NSs')
print('Collecting token access in OSM.')
print('Collecting NS itens')
print('Token Gerado: '+getoken())
print('Lista de NS: ')
print (getlistaNS(getoken()))
print('Removendo todas as NSs: ')
deleteAllNS(getlistaNS(getoken()))
RegisterLOGLaunch('REMOVING')
print("Excluindo simulacao de latencia")
ExecuteCommand("ssh root@10.159.205.6 'for pid in $(ps -ef | grep 'PLAO_client.py' | awk '\\''{print $2}'\\''); do kill -9 $pid; done'") 
ExecuteCommand("ssh root@10.159.205.12 'for pid in $(ps -ef | grep 'PLAO_client.py' | awk '\\''{print $2}'\\''); do kill -9 $pid; done'") 
ExecuteCommand("for pid in $(ps -ef | grep 'PLAO.py' | awk '{print $2}'); do kill -9 $pid; done")
ExecuteCommand("ssh root@10.159.205.6 'tc qdisc del dev eth0 root'")
print("Excluindo simulacao de aumento CPU Cloud 1")
ExecuteCommand("ssh root@10.159.205.6 'for pid in $(ps -ef | grep 'stress-ng' | awk '\\''{print $2}'\\''); do kill -9 $pid; done'") 
print("Coletando logs.")
ExecuteCommand("mkdir -p /opt/PLAO/exp/; mv /opt/PLAO/log/* /opt/PLAO/exp/  ")


