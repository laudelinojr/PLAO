import yaml
import socket
import threading
import time
import subprocess
import os
import os.path
import datetime
from datetime import datetime

LOCK_USER=0 #bLOCK ACCESS THE DICT USERS
OKTOCLEAN=0
RC1=0  #READ DICT USERS FOR CLOUD 1
RC2=0  #READ DICT USERS FOR CLOUD 1
SENTCOMMAND=0 #SENT COMMAND TO OSM

#Para simulacao
#OSM - ej /opt/PLAO: digitar python3 PLAO.py
#Openstack1- em /opt/PLAO/, digitar: python3 PLAO_client.py 10.159.205.10 openstack1 10.159.205.6
#Openstack2 - em /opt/PLAO/, digitar: python3 PLAO_client.py 10.159.205.10 openstack2 10.159.205.12

#Debug mode is 1
debug=0
debug_file = 0 #keep 0

#requisites for change all price of specif VIM (Cloud)
DOWN_UP_PRICE=10 #Number to add vnf Price
THRESHOLD=90 #THRESHOLD of CPU to apply rate in Cloud's price

#requisites1 SearchChangeVNFDPrice
FILE_VNF_PRICE="/opt/PLAO/osm/vnf_price_list.yaml"
#NAME_VNFD="VNFB"
#VIM_URL='http://10.159.205.6:5000/v3'
#PRICE_VNFD=14

#requisites SearchChangePriceLatencyJitterPIL
FILE_PIL_PRICE="/opt/PLAO/osm/pil_price_list.yaml"
PATH_LOG='/opt/PLAO/log/'
PATH='/opt/PLAO/'


def SearchVNFD(NAME_VNFD,B):
#Search VNFD in configuration file vnf_price and return position
#If no result, return -1 
    C = len(B) #Elements
    for i in range(C):
        if B[i]['vnfd'] == NAME_VNFD: #Search and compare the VNFD name
            return i
    else:
        return -1

def ChangeVNFPrice(COD_VNFD,VIMURL,PRICE,B,CLOUD_STATUS_CPU):
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
                if (CLOUD_STATUS_CPU == 1):
                    B[COD_VNFD]['prices'][i]['price']=int(PRICE)+THRESHOLD #Change the VNF Price
                else:
                    B[COD_VNFD]['prices'][i]['price']=int(PRICE) #Change the VNF Price
                return i
            else:
                return -1
    else:
        return -1

def SearchChangeVNFDPrice(NAME_VNFD,VIM_URL,PRICE_VNFD,CLOUD_STATUS_CPU):
    A=open(FILE_VNF_PRICE, )
    B=yaml.full_load(A)
    if debug == 1: print("In SearchChangeVNFDPrice")
    if (ChangeVNFPrice(SearchVNFD(NAME_VNFD,B),VIM_URL,PRICE_VNFD,B,CLOUD_STATUS_CPU)) != -1: #Change price of specific VIM in specific VNFD
        if debug == 1: print("In ChangeVNFPrice(SearchVNFD")
        with open(FILE_VNF_PRICE, 'w') as file:
            documents = yaml.dump(B, file, sort_keys=False) #Export changes to file without order, equal original file
        if debug == 1: print("going to copy to SearchChangeVNFDPrice ")
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

        nomearquivo5=PATH_LOG+'CPU_TRIGGER_'+CLOUD+'_history.txt' #write data in file
        with open(nomearquivo5, 'a') as arquivo:
            arquivo.write(DATEHOURS() + ','+ CLOUD + ","+ CLOUDIP +","+ str(STATUS_CPU_NOW)+'\n')
        ExecuteCommand('docker cp '+FILE_VNF_PRICE+' '+'$(docker ps -qf name=osm_pla):/placement/')
        try:
            nomearquivo6=PATH_LOG+'CONFIG_OSM_history.txt' #write data in file
            with open(nomearquivo6, 'a') as arquivo:
                arquivo.write(DATEHOURS() + '#CHANGE_VNFD_ALL# Changed and copied file '+ FILE_VNF_PRICE + ' to container PLA. Add values in All prices to Cloud: '+VIM_URL+ '.' +'\n')
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
    #if debug == 1: print ("entrei dentro de ChangePriceLatencyJitterPIL")
    #if debug == 1: print(PRICE)
    #if debug == 1: print(LATENCY)
    #if debug == 1: print(JITTER)
    PRICE=round(float(PRICE))
    LATENCY=round(float(LATENCY))
    JITTER=round(float(JITTER))
    if ((B['pil'][CLOUD_COD]['pil_price'] != PRICE) or (B['pil'][CLOUD_COD]['pil_latency'] != LATENCY) or (B['pil'][CLOUD_COD]['pil_jitter'] != JITTER)): #Change just one this values is different of the entry
        B['pil'][CLOUD_COD]['pil_price']=PRICE #change the price
        B['pil'][CLOUD_COD]['pil_latency']=LATENCY #change the latency - same price
        B['pil'][CLOUD_COD]['pil_jitter']=JITTER #change the jitter
        if debug == 1: print ("PRICE, LATENCIA e JITTER alterados no arquivo vnf_price_list.yaml.")
        return 0
    else:
        return -1

def UsersAdd():
    global LOCK_USER #bLOCK ACCESS THE DICT USERS
    global RC1
    global RC2
    global SENTCOMMAND
    USERIP=""
    LATENCY=""
    VNF=""
    COMMAND=""
    while True:
        nomearquivo7='user_vnfd_latencia.txt' #write data in file
        if(os.path.isfile(nomearquivo7)):
            #if debug == 1: print("O arquivo existe")           
            with open(nomearquivo7, 'r') as arquivo:
                #print("coletando arquivo latencia")
                linha = arquivo.readline()
            #if debug == 1: print("linha trabalhando agora: "+ linha)
                valores=linha.split('#')
                USERIP = valores[0]
                COMMAND = valores[1]        
                VNF = valores[2]           
            #print("vai excluir arquivo")
            os.remove(nomearquivo7)
            #print("excluiu o arquivo")
        
        if LOCK_USER == 0:
            LOCK_USER = 1
            #if debug == 1: print("lock user lockado")
            users.update({'0':{'USERIP': USERIP,'VNF': VNF,'COMMAND': COMMAND,'SENTCOMMAND': SENTCOMMAND,'RC1': RC1, 'RC2': RC2}}) 
            LOCK_USER = 0
            #if debug == 1: print("lock user deslockado")
        if debug == 1: print(users)
        time.sleep(1)
        if LOCK_USER == 0:
            LOCK_USER = 1
            if ( users.get('0').get('RC1') == 1) and ( users.get('0').get('RC2') == 1) and  (users.get('0').get('SENTCOMMAND') == 1):
                users.clear()
                RC1=0
                RC2=0
                SENTCOMMAND=0
                USERIP=""
                LATENCY=""
                VNF=""
                COMMAND=""
            LOCK_USER = 0

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

def SearchChangePriceLatencyJitterPIL(PRICE,LATENCY,JITTER,OPENSTACK_FROM,OPENSTACK_TO):
    A=open(FILE_PIL_PRICE, )
    B=yaml.full_load(A)
    #Search cloud combination and change the price, latency and jitter
    CLOUD_COD=SearchChangePILPrice(OPENSTACK_FROM,OPENSTACK_TO,B)
    #if debug == 1: print("CLOUD_COD: "+str(CLOUD_COD))
    if CLOUD_COD != -1:
        if (ChangePriceLatencyJitterPIL(CLOUD_COD,PRICE,LATENCY,JITTER,B)) != -1: #Change Price Latency and Jitter
            with open(FILE_PIL_PRICE, 'w') as file:
                documents = yaml.dump(B, file, sort_keys=False) #Export changes to file without order, equal original file

            ExecuteCommand('docker cp '+FILE_PIL_PRICE+' '+'$(docker ps -qf name=osm_pla):/placement/')

            try:
                nomearquivo8=PATH_LOG+'CONFIG_OSM_history.txt' #write data in file
                with open(nomearquivo8, 'a') as arquivo:
                    arquivo.write( DATEHOURS() + '#CHANGE_PIL# Changed and copied file '+FILE_PIL_PRICE + ' to container PLA. ' +' PRICE: '+PRICE+' LATENCY: '+LATENCY+' JITTER: '+JITTER+'\n')
            except:
                return -1
            if debug == 1: print("File pil_price changed")
        else:
            if debug == 1: print ("File pil_price not changed")

def printCloudsDict():
    while True:
        time.sleep(15)
        if debug == 1: print('Printing Cloud Dict:')
        if len(clouds) > 0:
            for i in clouds:
                print (i+str(clouds.get(i)))
        else:
            if debug == 1: print('Cloud Dict Empty')

def DATEHOURS():
    DATEHOUR = datetime.now().strftime('%d.%m.%y-%H:%M:%S')  # converte hora para string do cliente
    return DATEHOUR

def UnixTimeStamp():
    return datetime.timestamp(datetime.now())

def conectado(connection, enderecoCliente):
        print('Conected with', enderecoCliente)
        global RC1
        global RC2
        global LOCK_USER
        global SENTCOMMAND
        while True:
            msg = connection.recv(1024).decode('utf8')
            msg = msg.split('#')  # quebra o texto unico com o separador #

            if len(msg) > 5:  # se true indica que existe protocolo trafegando
                #if debug == 1: print ("DEBUG: dentro primeiro while true conectado2")
                # TIPOS:REGIS - First comunication between server and client for register the cloud
                #       SENDS - Send command to Server
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
                EXTRA = msg[18]  #ADDRESS IP FOR TEST LATENCY
                EXTRA2 = msg[19] #VNFDS
                EXTRA3 = msg[20] #LATENCY IN CLIENT
                
                if debug == 1: print ('TIPO: '+TIPO+' CLOUD: '+CLOUD+' CLOUDIP: '+CLOUDIP+' DATEHOUR: '+DATEHOUR+' CLOUDTONAME: '+CLOUDTONAME+' CLOUDTOIP: '+CLOUDTOIP+' STATUS: '+STATUS+' PRICE: '+PRICE+' LATENCY: '+LATENCY+' JITTER: '+JITTER+' CPU: '+CPU+' MEMORY: '+MEMORY+' DISK: '+DISK+' NVM: '+NVM+' CPUC: '+ CPUC+' MEMORYC: '+ MEMORYC +' DISKC: '+DISKC +' EXTRA: '+EXTRA+' EXTRA2: '+EXTRA2+' EXTRA3: '+EXTRA3 )
                print (TIPO+'#'+CLOUD+'#'+CLOUDIP+'#'+DATEHOUR+'#'+CLOUDTONAME+'#'+CLOUDTOIP+'#'+STATUS+'#'+PRICE+'#'+LATENCY+'#'+JITTER+'#'+CPU+'#'+MEMORY+'#'+DISK+'#'+NVM+'#'+CPUC+'#'+MEMORYC+'#'+'#'+DISKC+'#' +EXTRA+'#'+EXTRA2+'#'+EXTRA3+'#' )
                if TIPO == 'REGIS': #check for the first time the type protocol and send the id number
                    VIMURL='http://'+CLOUDIP+':5000/v3'
                    clouds.update({(str(len(clouds)+1)):{'CLOUD': CLOUD,'CLOUDIP':CLOUDIP,'VIMURL': VIMURL,'CPU':CPU}})
                    mensagem = 'REGIS#' + str(len(clouds)) + '#' + CLOUD + '#' + CLOUDIP + '#' + DATEHOUR + '#'+ CLOUDTONAME + '#' + CLOUDTOIP + '#' + STATUS + '#' + PRICE + '#' + LATENCY + '#' + JITTER + '#' + CPU + '#' + MEMORY + '#' + DISK+ '#' + NVM + '#' + CPUC + '#' + MEMORYC + '#'+ DISKC + '#' + EXTRA + '#'+ EXTRA2 + '#'+ EXTRA3 + '#'  #preparing message
                    connection.sendall(mensagem.encode('utf8'))  #sending in first time the command to client
                    commands.update({(ID): {'CLOUD': CLOUD,'CLOUDIP': CLOUDIP, 'DATEHOUR': DATEHOUR,'CLOUDTONAME': CLOUDTONAME, 'CLOUDTOIP': CLOUDTOIP, 'STATUS': STATUS, 'PRICE': PRICE, 'LATTENCY': LATENCY, 'JITTER': JITTER , 'CPU': CPU , 'MEMORY': MEMORY ,'DISK': DISK ,'NVM': NVM ,'CPUC': CPUC,'MEMORYC': MEMORYC,'DISKC': DISKC, 'EXTRA': EXTRA, 'EXTRA2': EXTRA2, 'EXTRA3': 0 ,'CONEXAO': connection}})
                if TIPO == 'SENDS':  #check the type protocol
                    CLOUD_STATUS_CPU=int(clouds.get(str(ID)).get('CPU'))
                    #print ("entrou sends")
                    #print(len(EXTRA3))
                    #print(EXTRA3)
                    #Process to change price between cloud and vnfd

                    #News

                    #Iniciando variaveis
                    PESOL_VNFA=0
                    PESOCPU_VNFA=0
                    LATENCYP_VNFA=0
                    CPUP_VNFA=0
                    PRICE_NOVO_VNFA=0
                    PESOL_VNFB=0
                    PESOCPU_VNFB=0
                    LATENCYP_VNFB=0
                    CPUP_VNFB=0
                    PRICE_NOVO_VNFB=0
                    LATENCY_USER=''

                    if ((EXTRA3 != 'EXTRA3') and (len(EXTRA3)!=0)):
                        EXTRA2=EXTRA2.split(',')
                        EXTRA2SPL0=EXTRA2[0]
                        EXTRA2SPL1=EXTRA2[1]

                        PESOL_VNFA=7 #Peso para Latencia VNFA
                        PESOCPU_VNFA=3 #Peso CPU para Latencia VNFA
                        LATENCY_USER=EXTRA3

                        print("pesol")
                        print(PESOL_VNFA)
                        print('print pesocpu')
                        print(PESOCPU_VNFA)
                        print("latencia_user")
                        print(LATENCY_USER)
                        print("cpu")
                        print(CPU)

                        #if (CLOUD == "openstack1"):
                        #    CPU='10'
                        #if (CLOUD == "openstack2"):
                        #    CPU='20'

                        LATENCYP_VNFA=int(LATENCY_USER)*PESOL_VNFA
                        CPUP_VNFA=int(CPU)*PESOCPU_VNFA
                        PRICE_NOVO_VNFA=round((LATENCYP_VNFA+CPUP_VNFA)/10)

                        print("price novo nvfwa")
                        print("latencyp")
                        print(LATENCYP_VNFA)
                        print("cpup")
                        print (CPUP_VNFA)
                        print("price_novo")
                        print(PRICE_NOVO_VNFA)                 
                        #print(type(EXTRA3))
                        NAME_VNFD=EXTRA2SPL0
                        VIM_URL='http://'+CLOUDIP+':5000/v3'
                        #PRICE_VNFD=EXTRA3
                        PRICE_VNFD=PRICE_NOVO_VNFA
                        SearchChangeVNFDPrice(NAME_VNFD,VIM_URL,PRICE_VNFD,CLOUD_STATUS_CPU)

                        PESOL_VNFB=1
                        PESOCPU_VNFB=9
                        print("proximo")
                        print("pesol")
                        print(PESOL_VNFB)
                        print('print pesocpu')
                        print(PESOCPU_VNFB)
                        print("latencia_user")
                        print(LATENCY_USER)
                        print("cpu")
                        print(CPU)
                        LATENCYP_VNFB=int(LATENCY_USER)*PESOL_VNFB
                        CPUP_VNFB=int(CPU)*PESOCPU_VNFB

                        #if (CLOUD == "openstack1"):
                        #    CPU='10'
                        #if (CLOUD == "openstack2"):
                        #    CPU='20'

                        PRICE_NOVO_VNFB=round((LATENCYP_VNFB+CPUP_VNFB)/10)
                        print("price novo nvfwb")
                        print("latencyp")
                        print(LATENCYP_VNFB)
                        print("vcpup")
                        print (CPUP_VNFB)
                        print("pricenovo")
                        print(PRICE_NOVO_VNFB)                 
                        #print(type(EXTRA3))

                        NAME_VNFD=EXTRA2SPL1
                        VIM_URL='http://'+CLOUDIP+':5000/v3'
                        #PRICE_VNFD=EXTRA3
                        PRICE_VNFD=PRICE_NOVO_VNFB
                        SearchChangeVNFDPrice(NAME_VNFD,VIM_URL,PRICE_VNFD,CLOUD_STATUS_CPU) 


                        nomearquivo10=PATH_LOG+'CONFIG_OSM_history.txt' #write data in file
                        with open(nomearquivo10, 'a') as arquivo:
                            arquivo.write(DATEHOURS()+'#DEBUG#' + 'CLOUDIP: '+ CLOUDIP+' LATENCY: '+LATENCY+' PESOL_VNFA: '+str(PESOL_VNFA) + ' LATENCY_USER: '+str(LATENCY_USER)+' PESOCPU_VNFA : '+str(PESOCPU_VNFA)+' CPU: '+CPU+' LATENCYP_VNFA: '+str(LATENCYP_VNFA)+' CPUP_VNFA: '+str(CPUP_VNFA)+' PRICE_NOVO_VNFA: '+str(PRICE_NOVO_VNFA)+' PESOL_VNFB: '+str(PESOL_VNFB)+' PESOCPU_VNFB: '+str(PESOCPU_VNFB)+' LATENCYP_VNFb: '+str(LATENCYP_VNFB)+' CPUP_VNFB: '+str(CPUP_VNFB)+' PRICE_NOVO_VNFB: '+str(PRICE_NOVO_VNFB)+ '\n')



                        if (ID == "1"):   #If receive and processing data about user, this is marked in dictionary
                            #print("vou colocar rc1 igual a 1")
                            RC1=1
                        if (ID == "2"):
                            #print("vou colocar rc2 igual a 1")
                            RC2=1
                        EXTRA='EXTRA'
                        EXTRA2='EXTRA2'
                    #if debug == 1: print ("imprimindo RCs")
                    #if debug == 1: print(users.get('0').get('RC1'))
                    #if debug == 1: print(users.get('0').get('RC2'))
                    #if LOCK_USER == 0:
                        #print ("entrei lock igual a 0 n main para command")
                    #    LOCK_USER = 1      
                    if ((users.get('0').get('RC1') == 1) and (users.get('0').get('RC2') == 1) and (users.get('0').get('SENTCOMMAND') == 0)):
                        #print ("vamos rodar o comando ExecuteCommand")
                        #ExecuteCommand('$(docker ps -qf name=osm_pla)')
                        USERSCOMMAND=users.get('0').get('COMMAND')
                        SENTCOMMAND=1
                        #LOCK_USER = 0
                        ExecuteCommand(USERSCOMMAND) #Run command to instanciate machine
                        nomearquivo1=PATH_LOG+'CONFIG_OSM_history.txt' #write data in file
                        with open(nomearquivo1, 'a') as arquivo:
                            arquivo.write(DATEHOURS() + '#INSTANTIATE#  Executado comando para instanciar NS. Segue:' + USERSCOMMAND + '\n')

                        ExecuteCommand('cp '+FILE_VNF_PRICE+' '+PATH_LOG+'vnf_price_list.yaml_'+str(UnixTimeStamp()))
                        ExecuteCommand('cp '+FILE_PIL_PRICE+' '+PATH_LOG+'pil_price_list.yaml_'+str(UnixTimeStamp()))
                        
                    #    LOCK_USER = 0
                    #Check Dict that have information about user entry
                    if (len(users)>=1):
                        #print("LOCKUSER: "+str(LOCK_USER))
                        #print("ID: "+str(ID))
                        #print(users.get('0').get('RC1'))
                        #print("entrou aqui if users")
                        if LOCK_USER == 0:
                            LOCK_USER = 1
                            if (users.get('0').get('RC1')==0 and ID == "1"):
                                #print("entrou primeiro if")
                                EXTRA=users.get('0').get('USERIP')
                                EXTRA2=users.get('0').get('VNF')
                                #print(EXTRA)
                                #print(EXTRA2)
                            if (users.get('0').get('RC2')==0 and ID == "2" ):
                                #print("entrou segundo if")
                                EXTRA=users.get('0').get('USERIP')
                                EXTRA2=users.get('0').get('VNF')
                                #print(EXTRA)
                                #print(EXTRA2)
                            LOCK_USER = 0
                    else:
                        EXTRA='EXTRA'
                        EXTRA2='EXTRA2'
                        
#                    CLOUD_STATUS_CPU=int(clouds.get(str(ID)).get('CPU'))
                    if (int(CPUC) > THRESHOLD) and (CLOUD_STATUS_CPU == 0):
                        CPU_STATUS_NOW=1   #Values: 0-cpu normal, 1-cpu high and cost value going to change
                        VIMURL=clouds.get(str(ID)).get('VIMURL')
                        SearchDownUpVimPrice(VIMURL,ID,CPU_STATUS_NOW,DATEHOUR) #The cost is add by CPU bigger
                    if (int(CPUC) < THRESHOLD) and (CLOUD_STATUS_CPU == 1):
                        CPU_STATUS_NOW=0   #Values: 0-cpu normal, 1-cpu high and cost value going to change
                        VIMURL=clouds.get(str(ID)).get('VIMURL')
                        SearchDownUpVimPrice(VIMURL,ID,CPU_STATUS_NOW,DATEHOUR) #The cost is add by CPU bigger

                    nomearquivo2=PATH_LOG+CLOUD+'_'+CLOUDIP+'_history.txt' #write data in file
                    nomearquivo3=PATH_LOG+'LINK_'+CLOUD+'_history.txt' #write data in file
                    
                    with open(nomearquivo2, 'a') as arquivo:
                        if (os.path.getsize(nomearquivo2) == 0):
                            arquivo.write('data,CLOUD,IP,CPU,MEMORY,NVM,VCPU,MEMORYC,DISCKC' +'\n')
                        if (MEMORY != 'MEMORY'):
                            arquivo.write(DATEHOUR + ','+ CLOUD + ","+ CLOUDIP +","+ CPU + "," + MEMORY + "," + NVM + "," + CPUC + "," + MEMORYC + ","+ DISKC +'\n')
                        if (MEMORY == 'MEMORY'):
                            arquivo.write(DATEHOUR + ','+ CLOUD + ","+ CLOUDIP +","+ '0' + "," + '0' + "," + '0' + "," + '0' + "," + '0' + ","+ '0' +'\n')
           
                    if PRICE != "PRICE": #If is sending real data, this going to a file
                        #print("price changed, we will to try change PILL PRICE")
                        with open(nomearquivo3, 'a') as arquivo:
                            
                            if (os.path.getsize(nomearquivo3) == 0):
                                arquivo.write('data,CLOUD,IP,PRICE,LATENCY,JITTER' +'\n')
                            if (MEMORY != 'MEMORY'):                            
                                arquivo.write(DATEHOUR + ','+ CLOUD + ","+ CLOUDIP +","+ PRICE + ","+LATENCY+","+JITTER+'\n')
                            if (MEMORY == 'MEMORY'):                            
                                arquivo.write(DATEHOUR + ','+ CLOUD + ","+ CLOUDIP +","+ '0' + ","+'0'+","+'0'+'\n')

                        SearchChangePriceLatencyJitterPIL(PRICE,LATENCY,JITTER,CLOUD,CLOUDTONAME) #execute function that search and change price pil                

                    #print ("tamanhoclouds: "+str(len(clouds)))
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

                    commands.update({('ID'): {'CLOUD': CLOUD,'CLOUDIP': CLOUDIP, 'DATEHOUR': DATEHOUR,'CLOUDTONAME': CLOUDTONAME, 'CLOUDTOIP': CLOUDTOIP, 'STATUS': STATUS, 'PRICE': PRICE, 'LATTENCY': LATENCY, 'JITTER': JITTER , 'CPU': CPU , 'MEMORY': MEMORY, 'CPUC': CPUC ,'MEMORYC': MEMORYC ,'DISKC': DISKC ,'EXTRA': EXTRA,'EXTRA2': EXTRA2,'EXTRA3': EXTRA3, 'CONEXAO': connection}})
                    mensagem = 'SENDC#' + ID + '#' + CLOUD + '#' + CLOUDIP + '#' + DATEHOUR + '#'+ CLOUDTONAME + '#' + CLOUDTOIP + '#' + STATUS + '#' + 'PRICE' + '#' + 'LATENCY' + '#' + '0' + '#' + 'CPU' + '#' + 'MEMORY' + '#' + 'DISK' + '#' + 'NVM' + '#' + 'CPUC' + '#'+ 'MEMORYC' + '#'+ 'DISKC'+ '#'+ EXTRA + '#'+ EXTRA2 + '#'+ 'EXTRA3' + '#'
                    #print("saindo sendc")
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
    thread_usersADD = threading.Thread(target=UsersAdd)
    thread_usersADD.start()
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
