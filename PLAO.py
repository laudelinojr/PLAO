import yaml
import socket
import threading
import time
import subprocess

#CPU - O LIMITE É CONFIGURAVEL E ESTA EM 90%, QUANDO O MESMO É ATINGIDO, OS PRICES DA 
# NUVEM_2 SÃO ALTERADOS PARA TODOS OS VNFDS DO ARQUIVO DE CONFIGURAÇÃO
# O PERCENTUAL SERÁ SEMPRE INTEIRO, DADO GUARDADO EM ARQUIVO TXT TAMBEM
# O valor a ser acrescido no PRICE é parametrizado, e atualmente é 10.
#Arquivo CPU_CLOUD_history.txt' - DATEHOURS,CLOUD,CLOUDIP,CPU

#JITTER E LATENCIA, AMBOS SÃO CONVERTIDOS PARA INTEIRO, POIS O ARQUIVO DE CONFIGURAÇÃO DO OSM SÓ ACEITA INTEIRO
# DADO GUARDADO EM ARQUIVO TEXTO TAMBÉM COM O NOME LINK
#Arquivo LINK_CLOUD_history.txt' - DATEHOUR, CLOUD,CLOUDIP,PRICE,LATENCY,JITTER
#O PREÇO ESTÁ O MESMO VALOR DA LATENCIA

#QUANTIDADE DE VNF POR CLOUD
#Arquivo CLOUD_CLOUDIP_history.txt - DATEHOUR,CLOUD,CLOUDIP,CPU,QT_VM

#Para simulacao
#OSM - ej /opt/PLAO: digitar python3 PLAO.py
#Openstack1- em /opt/PLAO/, digitar: python3 PLAO_client.py 10.159.205.10 openstack1 10.159.205.6
#Openstack2 - em /opt/PLAO/, digitar: python3 PLAO_client.py 10.159.205.10 openstack2 10.159.205.12



#Debug mode is 1
debug=0

#requisites for change all price of specif VIM (Cloud)
DOWN_UP_PRICE=10 #Number to add vnf Price
THRESHOLD=90 #THRESHOLD of CPU to apply rate in Cloud's price

#requisites1 SearchChangeVNFDPrice
FILE_VNF_PRICE="/opt/PLAO/osm/vnf_price_list.yaml"
NAME_VNFD="VNFB"
#VIM_URL='http://10.159.205.6:5000/v3'
PRICE_VNFD=14

#requisites SearchChangePriceLatencyJitterPIL
FILE_PIL_PRICE="/opt/PLAO/osm/pil_price_list.yaml"
PATH_LOG='/opt/PLAO/log/'


def SearchVNFD(NAME_VNFD,B):
#Search VNFD in configuration file vnf_price and return position
#If no result, return -1 
    C = len(B) #Elements
    for i in range(C):
        if B[i]['vnfd'] == NAME_VNFD: #Search and compare the VNFD name
            return i
    else:
        return -1

def ChangeVNFPrice(COD_VNFD,VIMURL,PRICE,B):
#First, use the SearchVNFD function, after, this
#Change price of specific VIMNAME OF VNFD
#If no result, return -1  
# In this, the target is to change the price cloud for specif Cloud (VIM)
    C = len(B[COD_VNFD]['prices']) #Elements

    if COD_VNFD < 0:
        return -1   
    for i in range(C):
        if B[COD_VNFD]['prices'][i]['vim_url'] == VIMURL: #Compare VIMURL between YAML and the new
            if B[COD_VNFD]['prices'][i]['price'] != PRICE:  #Compare new PRICE with actual Price, if equal, no change
                B[COD_VNFD]['prices'][i]['price']=PRICE #Change the VNF Price
                return i
            else:
                return -1
    else:
        return -1

def SearchChangeVNFDPrice(NAME_VNFD,VIM_URL,PRICE_VNFD):
    A=open(FILE_VNF_PRICE, )
    B=yaml.full_load(A)

    if (ChangeVNFPrice(SearchVNFD(NAME_VNFD,B),VIM_URL,PRICE_VNFD,B)) != -1: #Change price of specific VIM in specific VNFD
        with open(FILE_VNF_PRICE, 'w') as file:
            documents = yaml.dump(B, file, sort_keys=False) #Export changes to file without order, equal original file
        try:
            #changefile = subprocess.check_output(['/bin/bash','/opt/PLAO/script.sh','vnf_price_list.yaml'])
            nomearquivo4=PATH_LOG+'COPY_CONFIG_OSM_history.txt' #write data in file
            with open(nomearquivo4, 'a') as arquivo:
                arquivo.write(DATEHOUR + '- Alterado e copiado arquivo '+FILE_VNF_PRICE + ' para o container PLA.' +'\n')
            arquivo.close()
            subprocess.call(['python3', '/opt/PLAO/docker_pla.py', 'vnf_price_list'])
            #subprocess.call("/opt/PLAO/test1.py", shell=True)
            #os.system('docker cp '+FILE_VNF_PRICE+' '+'$(docker ps -qf name=osm_pla):/placement/')
        except:
            return -1     
        if debug ==1: print("DEBUG: File changed")
        if debug ==1: print("DEBUG: Copy file to container pla...")
    else:
        if debug ==1: print ("DEBUG: File not changed")

def SearchDownUpVimPrice(VIM_URL,CLOUD_COD,STATUS_CPU_NOW,DATEHOUR):
    #Receive the CPU STATUS NOW and update in list cloud, the CLOUD_STATUS_CPU
    A=open(FILE_VNF_PRICE, )
    B=yaml.full_load(A)
    C = len(B)
    D = len(B[0]['prices'])
    CLOUD=clouds.get(str(CLOUD_COD)).get('CLOUD') #Get name cloud for use in next operations
    CLOUDIP=clouds.get(str(CLOUD_COD)).get('CLOUDIP') # Get cod cloud for use in next operations
    VIMURL=clouds.get(str(CLOUD_COD)).get('VIMURL') # Get vim url for use in next operations
    CLOUD_STATUS_CPU=int(clouds.get(str(CLOUD_COD)).get('CPU')) #Values: 0-cpu normal, 1-cpu high and cost value changed
    PRICE=0 #Inicialize local variable
    CHANGED_PRICE_VIM_URL=0 #count auxiliar variable for count the total changes

    for i in range(C): #Search and change all the all vim url price for specific cloud
        for f in range(D):
            if B[i]['prices'][f]['vim_url'] == VIM_URL: #Compare VIMURL between YAML and the new
                    PRICE=B[i]['prices'][f]['price']  #Select the price of this vim_url
                    if PRICE >= 0:
                        if STATUS_CPU_NOW == 1 and CLOUD_STATUS_CPU == 0: #If the cloud CPU now is high (1), but in dict is normal (0), we need change dict to(1);
                            clouds.update({str(CLOUD_COD):{'CLOUD': CLOUD,'CLOUDIP':CLOUDIP,'VIMURL': VIMURL,'CPU':'1'}})
                            B[i]['prices'][f]['price']=PRICE+DOWN_UP_PRICE #Change the VNF Price with the rate price
                            CHANGED_PRICE_VIM_URL=CHANGED_PRICE_VIM_URL+1 #count auxiliar variable
                        if STATUS_CPU_NOW == 0 and CLOUD_STATUS_CPU == 1 and PRICE >= DOWN_UP_PRICE: #If the cloud CPU now is ok (0), but in dict is high (1), we need change dict to (0)
                            clouds.update({str(CLOUD_COD):{'CLOUD': CLOUD,'CLOUDIP':CLOUDIP,'VIMURL': VIMURL,'CPU':'0'}})
                            B[i]['prices'][f]['price']=int(PRICE-DOWN_UP_PRICE) #Change the VNF Price with the rate price
                            CHANGED_PRICE_VIM_URL=CHANGED_PRICE_VIM_URL+1 #count auxiliar variable
                        if STATUS_CPU_NOW == 0 and CLOUD_STATUS_CPU == 1 and PRICE <= DOWN_UP_PRICE: #If the cloud CPU now is ok (0), but in dict is high (1), we need change dict to (0)
                            clouds.update({str(CLOUD_COD):{'CLOUD': CLOUD,'CLOUDIP':CLOUDIP,'VIMURL': VIMURL,'CPU':'0'}})
                            B[i]['prices'][f]['price']=0 #Change the VNF Price with the rate price
                            CHANGED_PRICE_VIM_URL=CHANGED_PRICE_VIM_URL+1 #count auxiliar variable
                    else:
                        print("Trying update nvf_price file. There are price<=0. Check this.")

    if debug ==1: print ("DEBUG: Changed "+str(CHANGED_PRICE_VIM_URL)+" PRICES VIM_URL (CLOUDS).") #Print count auxiliar variable
    if CHANGED_PRICE_VIM_URL > 0:
        with open(FILE_VNF_PRICE, 'w') as file:
            documents = yaml.dump(B, file, sort_keys=False) #Export changes to file without order, equal original file
        print ("CPU CHANGE: File pil_price changed because High CPU.")

        nomearquivo3=PATH_LOG+'CPU_TRIGGER_'+CLOUD+'_history.txt' #write data in file
        with open(nomearquivo3, 'a') as arquivo:
            arquivo.write(DATEHOUR + ','+ CLOUD + ","+ CLOUDIP +","+ str(STATUS_CPU_NOW)+'\n')
        arquivo.close()

        try:
            nomearquivo4=PATH_LOG+'COPY_CONFIG_OSM_history.txt' #write data in file
            with open(nomearquivo4, 'a') as arquivo:
                arquivo.write(DATEHOUR + '- Alterado e copiado arquivo '+FILE_VNF_PRICE + ' para o container PLA.' +'\n')
            arquivo.close()
            subprocess.call(['python3', '/opt/PLAO/docker_pla.py', 'vnf_price_list'])
            #subprocess.call("/opt/PLAO/test1.py")
            #os.system('docker cp '+FILE_VNF_PRICE+' '+'$(docker ps -qf name=osm_pla):/placement/')
        except:
            return -1


def SearchChangePILPrice(OPENSTACK_FROM,OPENSTACK_TO,B):  #Search in file the cloud math between from and to, in this order. If located, stop the search
    C = len(B['pil']) #Elements
    for i in range(C):
        if B['pil'][i]['pil_endpoints'][0] == OPENSTACK_FROM:# or B['pil'][i]['pil_endpoints'][0] == OPENSTACK_TO:
            if B['pil'][i]['pil_endpoints'][1] == OPENSTACK_TO:# or B['pil'][i]['pil_endpoints'][1] == OPENSTACK_FROM:
                return i
    return -1

def ChangePriceLatencyJitterPIL(CLOUD_COD,PRICE,LATENCY,JITTER,B):
    PRICE=round(float(PRICE))
    LATENCY=round(float(LATENCY))
    JITTER=round(float(JITTER))
    if ((B['pil'][CLOUD_COD]['pil_price'] != PRICE) or (B['pil'][CLOUD_COD]['pil_latency'] != LATENCY) or (B['pil'][CLOUD_COD]['pil_jitter'] != JITTER)): #Change just one this values is different of the entry
        B['pil'][CLOUD_COD]['pil_price']=PRICE #change the price
        B['pil'][CLOUD_COD]['pil_latency']=LATENCY #change the latency - same price
        B['pil'][CLOUD_COD]['pil_jitter']=JITTER #change the jitter
        return 0
    else:
        return -1

def UsersAdd():

    nomearquivo1='user_vnfd_latencia.txt'
    arquivo = open(nomearquivo1,'r')
    linha = arquivo.readline()
    for linha in arquivo:
        valores=linha.split('#')

        USERIP = valores[0]
        VNFD = valores[1]
        LATENCY = valores[2]
        VIMURL = valores[3]
        COMMAND = valores[4]        
        #users.update({((str(len(users)+1)): {'USERIP': USERIP,'VNFD': VNFD, 'LATENCY': LATENCY,'VIMURL': VIMURL, 'COMMAND': COMMAND }})
        users.update({(str(len(users)+1)):{'USERIP': USERIP,'LATENCY': LATENCY,'COMMAND': COMMAND }})
        #clouds.update({(str(len(clouds)+1)):{'CLOUD': CLOUD,'CLOUDIP':CLOUDIP,'VIMURL': VIMURL,'CPU':CPU}})
        CLOUD=(clouds.get('1').get('CLOUD'))
    arquivo.close()

def UsersManager():
    while True:
        sleep.time(5)

        for i in len(users):
            print (users.get(i))
       


def SearchChangePriceLatencyJitterPIL(PRICE,LATENCY,JITTER,OPENSTACK_FROM,OPENSTACK_TO):
    #Search cloud combination and change the price, latency and jitter
    A=open(FILE_PIL_PRICE, )
    B=yaml.full_load(A)

    CLOUD_COD=SearchChangePILPrice(OPENSTACK_FROM,OPENSTACK_TO,B)
    if CLOUD_COD != -1:
        if (ChangePriceLatencyJitterPIL(CLOUD_COD,PRICE,LATENCY,JITTER,B)) != -1: #Change Price Latency and Jitter
            with open(FILE_PIL_PRICE, 'w') as file:
                documents = yaml.dump(B, file, sort_keys=False) #Export changes to file without order, equal original file
            try:
                nomearquivo4=PATH_LOG+'COPY_CONFIG_OSM_history.txt' #write data in file
                with open(nomearquivo4, 'a') as arquivo:
                    arquivo.write(DATEHOUR + '- Alterado e copiado arquivo '+FILE_PIL_PRICE + ' para o container PLA.' +'\n')
                arquivo.close()
                subprocess.call(['python3', '/opt/PLAO/docker_pla.py', 'pil_price_list'])
                #os.system('docker cp '+FILE_PIL_PRICE+' '+'$(docker ps -qf name=osm_pla):/placement/')
            except:
                return -1
            print("File pil_price changed")
        else:
            print ("File pil_price not changed")

def printCloudsDict():
    while True:
        time.sleep(15)
        print('Printing Cloud Dict:')
        if len(clouds) > 0:
            for i in clouds:
                print (i+str(clouds.get(i)))
        else:
            print('Cloud Dict Empty')

def DATEHOURS():
    DATEHOUR = datetime.datetime.now().strftime('%d.%m.%y-%H:%M:%S')  # converte hora para string do cliente
    return DATEHOURS

def conectado(connection, enderecoCliente):
        print('Conected with', enderecoCliente)
        while True:
            msg = connection.recv(1024).decode('utf8')
            msg = msg.split('#')  # quebra o texto unico com o separador #

            if len(msg) > 5:  # se true indica que existe protocolo trafegando
                if debug == 1: print ("DEBUG: dentro primeiro while true conectado2")
                # TIPOS:REGIS - First comunication between server and client for register the cloud
                #       SENDS - Send command to Server
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
                CPU = msg[11] #CPU PERCENT USAGE
                MEMORY = msg[12] #MEMORY PERCENT USAGE
                DISK = msg[13] #DISK PERCENT USAGE
                NVM = msg[14] #QUANTITY MACHINES
                CPUC = msg[15] #PERCENT CPU IN TOTAL OF CLOUD
                MEMORYC = msg[16] #PERCENT CPU IN TOTAL OF CLOUD
                DISKC = msg[17] #PERCENT CPU IN TOTAL OF CLOUD
                EXTRA = msg[18] 
                
                if debug == 1: print ('TIPO: '+TIPO+' CLOUD: '+CLOUD+' CLOUDIP: '+CLOUDIP+' DATEHOUR: '+DATEHOUR+' CLOUDTONAME: '+CLOUDTONAME+' CLOUDTOIP: '+CLOUDTOIP+' STATUS: '+STATUS+' PRICE: '+PRICE+' LATENCY: '+LATENCY+' JITTER: '+JITTER+' CPU: '+CPU+' MEMORY: '+MEMORY+' DISK: '+DISK+' NVM: '+NVM+' CPUC: '+ CPUC+' MEMORYC: '+ MEMORYC +' DISKC: '+DISKC )
               
                if TIPO == 'REGIS': #check for the first time the type protocol and send the id number
                    VIMURL='http://'+CLOUDIP+':5000/v3'
                    clouds.update({(str(len(clouds)+1)):{'CLOUD': CLOUD,'CLOUDIP':CLOUDIP,'VIMURL': VIMURL,'CPU':CPU}})
                    mensagem = 'REGIS#' + str(len(clouds)) + '#' + CLOUD + '#' + CLOUDIP + '#' + DATEHOUR + '#'+ CLOUDTONAME + '#' + CLOUDTOIP + '#' + STATUS + '#' + PRICE + '#' + LATENCY + '#' + JITTER + '#' + CPU + '#' + MEMORY + '#' + DISK+ '#' + NVM + '#' + CPUC + '#' + MEMORYC + '#'+ DISKC + '#'  #preparing message
                    connection.sendall(mensagem.encode('utf8'))  #sending in first time the command to client
                    commands.update({(ID): {'CLOUD': CLOUD,'CLOUDIP': CLOUDIP, 'DATEHOUR': DATEHOUR,'CLOUDTONAME': CLOUDTONAME, 'CLOUDTOIP': CLOUDTOIP, 'STATUS': STATUS, 'PRICE': PRICE, 'LATTENCY': LATENCY, 'JITTER': JITTER , 'CPU': CPU , 'MEMORY': MEMORY ,'DISK': DISK ,'NVM': NVM ,'CPUC': CPUC,'MEMORYC': MEMORYC,'DISKC': DISKC ,'CONEXAO': connection}})
                if TIPO == 'SENDS':  #check the type protocol
                    CLOUD_STATUS_CPU=int(clouds.get(str(ID)).get('CPU'))
                    if (int(CPUC) > THRESHOLD) and (CLOUD_STATUS_CPU == 0):
                        CPU_STATUS_NOW=1   #Values: 0-cpu normal, 1-cpu high and cost value going to change
                        VIMURL=clouds.get(str(ID)).get('VIMURL')
                        SearchDownUpVimPrice(VIMURL,ID,CPU_STATUS_NOW,DATEHOUR) #The cost is add by CPU bigger
                    if (int(CPUC) < THRESHOLD) and (CLOUD_STATUS_CPU == 1):
                        CPU_STATUS_NOW=0   #Values: 0-cpu normal, 1-cpu high and cost value going to change
                        VIMURL=clouds.get(str(ID)).get('VIMURL')
                        SearchDownUpVimPrice(VIMURL,ID,CPU_STATUS_NOW,DATEHOUR) #The cost is add by CPU bigger

                    nomearquivo1=PATH_LOG+CLOUD+'_'+CLOUDIP+'_history.txt' #write data in file
                    nomearquivo2=PATH_LOG+'LINK_'+CLOUD+'_history.txt' #write data in file

                    with open(nomearquivo1, 'a') as arquivo:
                        arquivo.write(DATEHOUR + ','+ CLOUD + ","+ CLOUDIP +","+ CPU + "," + MEMORY + "," + NVM + "," + CPUC + "," + MEMORYC + ","+ DISKC +'\n')
                    arquivo.close()

                    if PRICE != "PRICE": #If is sending real data, this going to a file
                        with open(nomearquivo2, 'a') as arquivo:
                            arquivo.write(DATEHOUR + ','+ CLOUD + ","+ CLOUDIP +","+ PRICE + ","+LATENCY+","+JITTER+'\n')
                        arquivo.close()
                        SearchChangePriceLatencyJitterPIL(PRICE,LATENCY,JITTER,CLOUD,CLOUDTONAME) #execute function that search and change price pil                

                    print ("tamanhoclouds: "+str(len(clouds)))
                    if len(clouds) == 2:
                        if ID == "1":
                            CLOUD=(clouds.get('1').get('CLOUD'))
                            CLOUDIP=(clouds.get('1').get('CLOUDIP'))
                            CLOUDTONAME=(clouds.get('2').get('CLOUD'))
                            CLOUDTOIP=(clouds.get('2').get('CLOUDIP'))
                        if ID == "2":
                            CLOUD=(clouds.get('2').get('CLOUD'))
                            CLOUDIP=(clouds.get('2').get('CLOUDIP'))
                            CLOUDTONAME=(clouds.get('1').get('CLOUD'))
                            CLOUDTOIP=(clouds.get('1').get('CLOUDIP'))

                    commands.update({('ID'): {'CLOUD': CLOUD,'CLOUDIP': CLOUDIP, 'DATEHOUR': DATEHOUR,'CLOUDTONAME': CLOUDTONAME, 'CLOUDTOIP': CLOUDTOIP, 'STATUS': STATUS, 'PRICE': PRICE, 'LATTENCY': LATENCY, 'JITTER': JITTER , 'CPU': CPU , 'MEMORY': MEMORY, 'CPUC': CPUC ,'MEMORYC': MEMORYC ,'DISKC': DISKC , 'CONEXAO': connection}})
                    mensagem = 'SENDC#' + ID + '#' + CLOUD + '#' + CLOUDIP + '#' + DATEHOUR + '#'+ CLOUDTONAME + '#' + CLOUDTOIP + '#' + STATUS + '#' + 'PRICE' + '#' + 'LATENCY' + '#' + '0' + '#' + 'CPU' + '#' + 'MEMORY' + '#' + 'DISK' + '#' + 'NVM' + '#' + 'CPUC' + '#'+ 'MEMORYC' + '#'+ 'DISKC' + '#'
                    print("saindo sendc")
                    print (mensagem)
                    connection.sendall(mensagem.encode('utf8'))

                if TIPO == 'EXCL': #Delete registry cloud in Dict
                    if ID.isdigit():
                        clouds.pop(ID)
        print('Closing connection with client', enderecoCliente)
        connection.close()

#Configurations for socket enviroment
socketServer = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
HOST = "0.0.0.0"#address ip to server
PORT = 6000 #port to server
socketServer.bind((HOST,PORT))
socketServer.listen(10)
print('Starting Controller PLAO Server for OSM')

#Dictionaries for application use.
commands = {}
clouds = {}
users = {}

try:
    #subprocess.call(['python3', '/opt/PLAO/PLAOsub_server.py'])
    UsersAdd()
    thread_usersManager = threading.Thread(target=UsersManager)
    thread_usersManager.start()
    thread_printCloudsDict = threading.Thread(target=printCloudsDict)
    thread_printCloudsDict.start()
    while True:
        con, enderecoCliente = socketServer.accept()
        IPORIGEM, PORTAORIGEM= enderecoCliente
        thread_cliente = threading.Thread(target=conectado,args=(con,enderecoCliente,))
        thread_cliente.start()
        if debug == 1: print("DEBUG: iniciado thread")
    print("Finalizando conexao do cliente", IP)
except KeyboardInterrupt:
    print('Tecla de interrupção acionada, saindo... Digite "Ctrl + C" mais uma vez.\n')
except Exception as e:
    print("Erro no cliente. " + str(e))
finally:
    socketServer.close()
