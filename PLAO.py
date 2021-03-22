import yaml
import socket
import threading
import time

#Debug mode is 1
debug=0

#requisites for change all price of specif VIM (Cloud)
GROW_ADD_PRICE=10 #Number to add vnf Price
THRESHOLD=90 #THRESHOLD of CPU to apply rate in Cloud's price

#requisites1 SearchChangeVNFDPrice
FILE_VNF_PRICE="/opt/PLAO/osm/vnf_price_list.yaml"
NAME_VNFD="VNFB"
#VIM_URL='http://10.159.205.6:5000/v3'
PRICE_VNFD=14

#requisites SearchChangePriceLatencyJitterPILL
FILE_PILL_PRICE="/opt/PLAO/osm/pill_price_list.yaml"

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
        if debug ==1: print("DEBUG: File changed")
        if debug ==1: print("DEBUG: Copy file to container pla...")
    else:
        if debug ==1: print ("DEBUG: File not changed")

def SearchGrowUpVimPrice(VIM_URL,GROW_ADD_PRICE,CLOUD_COD,STATUS_CPU_NOW):
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
                    if PRICE > 0:
                        if STATUS_CPU_NOW == 1 and CLOUD_STATUS_CPU == 0: #If the cloud CPU now is high (1), but in dict is normal (0), we need change dict to(1);
                            clouds.update({str(CLOUD_COD):{'CLOUD': CLOUD,'CLOUDIP':CLOUDIP,'VIMURL': VIMURL,'CPU':'1'}})
                            B[i]['prices'][f]['price']=PRICE+GROW_ADD_PRICE #Change the VNF Price with the rate price
                            CHANGED_PRICE_VIM_URL=CHANGED_PRICE_VIM_URL+1 #count auxiliar variable
                        if STATUS_CPU_NOW == 0 and CLOUD_STATUS_CPU == 1: #If the cloud CPU now is ok (0), but in dict is high (1), we need change dict to (0)
                            clouds.update({str(CLOUD_COD):{'CLOUD': CLOUD,'CLOUDIP':CLOUDIP,'VIMURL': VIMURL,'CPU':'0'}})
                            B[i]['prices'][f]['price']=int(PRICE+GROW_ADD_PRICE) #Change the VNF Price with the rate price
                            CHANGED_PRICE_VIM_URL=CHANGED_PRICE_VIM_URL+1 #count auxiliar variable
                    else:
                        print("Trying update nvf_price file. There are price<=0. Check this.")

    if debug ==1: print ("DEBUG: Changed "+str(CHANGED_PRICE_VIM_URL)+" PRICES VIM_URL (CLOUDS).") #Print count auxiliar variable
    if CHANGED_PRICE_VIM_URL > 0:
        with open(FILE_VNF_PRICE, 'w') as file:
            documents = yaml.dump(B, file, sort_keys=False) #Export changes to file without order, equal original file
        print ("File pill_price changed because CPU.")


def SearchChangePILLPrice(OPENSTACK_FROM,OPENSTACK_TO,B):  #Search in file the cloud math between from and to, in this order. If located, stop the search
    C = len(B['pil']) #Elements
    for i in range(C):
        if B['pil'][i]['pil_endpoints'][0] == OPENSTACK_FROM:# or B['pil'][i]['pil_endpoints'][0] == OPENSTACK_TO:
            if B['pil'][i]['pil_endpoints'][1] == OPENSTACK_TO:# or B['pil'][i]['pil_endpoints'][1] == OPENSTACK_FROM:
                return i
    return -1

def ChangePriceLatencyJitterPILL(CLOUD_COD,PRICE,LATENCY,JITTER,B):
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

def SearchChangePriceLatencyJitterPILL(PRICE,LATENCY,JITTER,OPENSTACK_FROM,OPENSTACK_TO):
    #Search cloud combination and change the price, latency and jitter
    A=open(FILE_PILL_PRICE, )
    B=yaml.full_load(A)

    CLOUD_COD=SearchChangePILLPrice(OPENSTACK_FROM,OPENSTACK_TO,B)
    if CLOUD_COD != -1:
        if (ChangePriceLatencyJitterPILL(CLOUD_COD,PRICE,LATENCY,JITTER,B)) != -1: #Change Price Latency and Jitter
            with open(FILE_PILL_PRICE, 'w') as file:
                documents = yaml.dump(B, file, sort_keys=False) #Export changes to file without order, equal original file
            print("File pill_price changed")
        else:
            print ("File pill_price not changed")

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
                CPU = msg[11] #CPU
                MEMORY = msg[12] #MEMORY
                if TIPO == 'REGIS': #check for the first time the type protocol and send the id number
                    VIMURL='http://'+CLOUDIP+':5000/v3'
                    clouds.update({(str(len(clouds)+1)):{'CLOUD': CLOUD,'CLOUDIP':CLOUDIP,'VIMURL': VIMURL,'CPU':CPU}})
                    mensagem = 'REGIS#' + str(len(clouds)) + '#' + CLOUD + '#' + CLOUDIP + '#' + DATEHOUR + '#'+ CLOUDTONAME + '#' + CLOUDTOIP + '#' + STATUS + '#' + PRICE + '#' + LATENCY + '#' + JITTER + '#' + CPU + '#' + MEMORY + '#'  #preparing message
                    connection.sendall(mensagem.encode('utf8'))  #sending in first time the command to client
                    commands.update({(ID): {'CLOUD': CLOUD,'CLOUDIP': CLOUDIP, 'DATEHOUR': DATEHOUR,'CLOUDTONAME': CLOUDTONAME, 'CLOUDTOIP': CLOUDTOIP, 'STATUS': STATUS, 'PRICE': PRICE, 'LATTENCY': LATENCY, 'JITTER': JITTER , 'CPU': CPU , 'MEMORY': MEMORY ,'CONEXAO': connection}})
                if TIPO == 'SENDS':  #check the type protocol

                    if int(CPU) > THRESHOLD:
                        CPU_STATUS_NOW=1   #Values: 0-cpu normal, 1-cpu high and cost value going to change
                        VIMURL=clouds.get(str(ID)).get('VIMURL')
                        SearchGrowUpVimPrice(VIMURL,GROW_ADD_PRICE,ID,CPU_STATUS_NOW) #The cost is add by CPU bigger

                    nomearquivo1=CLOUD+'_'+CLOUDIP+'_history.txt' #write data in file
                    nomearquivo2='LINK_'+CLOUD+'_'+CLOUDTONAME+'_history.txt' #write data in file

                    if PRICE != "PRICE": #If is sending real data, this going to a file
                        print(DATEHOUR + ','+ CLOUD + ","+ CLOUDIP +","+ PRICE + ","+LATENCY+","+JITTER + "," + CPU + "," + MEMORY)
                        with open(nomearquivo1, 'a') as arquivo:
                            arquivo.write(DATEHOUR + ','+ CLOUD + ","+ CLOUDIP +","+ CPU + "," + MEMORY +'\n')
                        with open(nomearquivo2, 'a') as arquivo:
                            arquivo.write(DATEHOUR + ','+ CLOUD + ","+ CLOUDIP +","+ PRICE + ","+LATENCY+","+JITTER+'\n')
                        SearchChangePriceLatencyJitterPILL(PRICE,LATENCY,JITTER,CLOUD,CLOUDTONAME) #execute function that search and change price pill                

                    print ("tamanhoclouds: "+str(len(clouds)))
                    if len(clouds) = 2:
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
                    commands.update({('ID'): {'CLOUD': CLOUD,'CLOUDIP': CLOUDIP, 'DATEHOUR': DATEHOUR,'CLOUDTONAME': CLOUDTONAME, 'CLOUDTOIP': CLOUDTOIP, 'STATUS': STATUS, 'PRICE': PRICE, 'LATTENCY': LATENCY, 'JITTER': JITTER , 'CPU': CPU , 'MEMORY': MEMORY, 'CONEXAO': connection}})
                    mensagem = 'SENDC#' + ID + '#' + CLOUD + '#' + CLOUDIP + '#' + DATEHOUR + '#'+ CLOUDTONAME + '#' + CLOUDTOIP + '#' + STATUS + '#' + 'PRICE' + '#' + 'LATENCY' + '#' + 'JITTER' + '#' + 'CPU' + '#' + 'MEMORY' + '#'
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

try:
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

#corrigir envio custo sem dados, so nome variavel
# latencia para o usuario e aterar pesos vnf baseado nisto
# ver se existe metrica de quantidade de vnf alocada
# alterar aquivo no container a cada mudança
# fazer simulações com tc