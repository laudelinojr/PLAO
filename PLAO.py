import yaml
import socket
import threading
import time

#requisites1 SearchChangeVNFDPrice
FILE_VNF_PRICE="C:/Temp/artigo/vnf_price_list.yaml"
NAME_VNFD="VNFB"
VIM_URL='http://10.159.205.6:5000/v3'
PRICE_VNFD=14

#requisites SearchChangePriceLatencyJitterPILL
FILE_PILL_PRICE="C:/Temp/artigo/pill_price_list.yaml"
OPENSTACK_FROM="openstack1"
OPENSTACK_TO="openstack2"
PRICE=14
LATENCY=34
JITTER=44

#requisites for change all price of specif VIM (Cloud)
GROW_RATE_PRICE=2
THRESHOLD=90

####################################### First Phase Program

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
        print("File changed")
        print("Copy file to container pla...")
    else:
        print ("File not changed")

def SearchGrowUpVimPrice(VIM_URL,GROW_RATE_PRICE):

    A=open(FILE_VNF_PRICE, )
    B=yaml.full_load(A)
    C = len(B)
    D = len(B[0]['prices'])
    PRICE=0
    CHANGED_PRICE_VIM_URL=0

    for i in range(C): #Search and change all the all vim url price for specific cloud
        for f in range(D):
            if B[i]['prices'][f]['vim_url'] == VIM_URL: #Compare VIMURL between YAML and the new
                    PRICE=B[i]['prices'][f]['price']
                    B[i]['prices'][f]['price']=PRICE*GROW_RATE_PRICE #Change the VNF Price with the rate price
                    PRICE=0
                    CHANGED_PRICE_VIM_URL=CHANGED_PRICE_VIM_URL+1


    with open(FILE_VNF_PRICE, 'w') as file:
        documents = yaml.dump(B, file, sort_keys=False) #Export changes to file without order, equal original file
    print("File changed")
    print ("Changed "+str(CHANGED_PRICE_VIM_URL)+" PRICES VIM_URL (CLOUDS).")



def SearchChangePILLPrice(OPENSTACK_FROM,OPENSTACK_TO,B):  #Search in file the cloud math between from and to, in this order. If located, stop the search
    C = len(B['pil']) #Elements
    for i in range(C):
        if B['pil'][i]['pil_endpoints'][0] == OPENSTACK_FROM:
            if B['pil'][i]['pil_endpoints'][1] == OPENSTACK_TO:
                return i
    return -1

def ChangePriceLatencyJitterPILL(CLOUD_COD,PRICE,LATENCY,JITTER,B):
    if ((B['pil'][CLOUD_COD]['pil_price'] != PRICE) or (B['pil'][CLOUD_COD]['pil_latency'] != LATENCY) or (B['pil'][CLOUD_COD]['pil_jitter'] != JITTER)): #Change just one this values is different of the entry
        B['pil'][CLOUD_COD]['pil_price']=PRICE #change the price
        B['pil'][CLOUD_COD]['pil_latency']=LATENCY #change the latency - same price
        B['pil'][CLOUD_COD]['pil_jitter']=JITTER #change the jitter
        return 0
    else:
        return -1

def SearchChangePriceLatencyJitterPILL(PRICE,LATENCY,JITTER,OPENSTACK_FROM,OPENSTACK_TO):

    A=open(FILE_PILL_PRICE, )
    B=yaml.full_load(A)

    CLOUD_COD=SearchChangePILLPrice(OPENSTACK_FROM,OPENSTACK_TO,B)

    if CLOUD_COD != -1:
        if (ChangePriceLatencyJitterPILL(CLOUD_COD,PRICE,LATENCY,JITTER,B)) != -1: #Change Price Latency and Jitter
            with open(FILE_PILL_PRICE, 'w') as file:
                documents = yaml.dump(B, file, sort_keys=False) #Export changes to file without order, equal original file
            print("File changed")
        else:
            print ("File not changed")
    else:
        print('The cloud math did not locate.')


#SearchChangeVNFDPrice(NAME_VNFD,VIM_URL,PRICE_VNFD)
#SearchChangePriceLatencyJitterPILL(PRICE,LATENCY,JITTER,OPENSTACK_FROM,OPENSTACK_TO)
SearchGrowUpVimPrice(VIM_URL,GROW_RATE_PRICE)

####################################### Second Phase Program
""" 
def printCloudsDict():
    while True:
        time.sleep(15)
        print('Printing Cloud Dict:')
        if len(clouds) > 0:
            for i in clouds:
                print (i+str(clouds.get(i)))
        else:
            print('Cloud Dict Empty')

def requestDataCloud():
    while True:
        time.sleep(5)
        if len(clouds) == 2:
            print('Sending commands to Clouds:')
            CLOUD=(clouds.get('1').get('CLOUD'))
            CLOUDIP=(clouds.get('1').get('CLOUDIP'))
            CLOUDTONAME=(clouds.get('2').get('CLOUD'))
            CLOUDTOIP=(clouds.get('2').get('CLOUDIP'))
            #for i in clouds:
            #    print ('ID: '+i+' CLOUD: '+str(clouds.get(i).get('CLOUD'))+' CLOUDIP: '+str(clouds.get(i).get('CLOUDIP')))          
            for i in commands:
                print(i)
                print(commands.get(i).get('CONEXAO'))

            connection = commands.get('ID').get('CONEXAO')
            print (connection)
            #if connection != 'null':
             #   mensagem = 'SENDC#' + '#' + CLOUD + '#' + CLOUDIP + '#' + DATEHOUR + '#'+ CLOUDTONAME + '#' + CLOUDTOIP + '#' + STATUS + '#'  # preparando mensagem
              #  connection.sendall(mensagem.encode('utf8'))
               # commands.update({(ID): {'CLOUD': CLOUD,'CLOUDIP': CLOUDIP, 'DATEHOUR': DATEHOURS(),'CLOUDTONAME': CLOUDTONAME, 'CLOUDTOIP': CLOUDTOIP, 'STATUS': STATUS,'CONEXAO': connection}})


def DATEHOURS():
    DATEHOUR = datetime.datetime.now().strftime('%d.%m.%y-%H:%M:%S')  # converte hora para string do cliente
    return DATEHOURS

def conectado(connection, enderecoCliente):
        print('Conected with', enderecoCliente)
        while True:
            #time.sleep(5)
            #print ("DEBUG: dentro primeiro while true conectado")
            msg = connection.recv(1024).decode('utf8')
            msg = msg.split('#')  # quebra o texto unico com o separador #

            if len(msg) > 5:  # se true indica que existe protocolo trafegando
                #print ("DEBUG: dentro primeiro while true conectado2")
                # TIPOS: REGD - Send new ID request
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
                    clouds.update({(str(len(clouds)+1)):{'CLOUD': CLOUD,'CLOUDIP':CLOUDIP}})
                    mensagem = 'REGIS#' + str(len(clouds)) + '#' + CLOUD + '#' + CLOUDIP + '#' + DATEHOUR + '#'+ CLOUDTONAME + '#' + CLOUDTOIP + '#' + STATUS + '#' + PRICE + '#' + LATENCY + '#' + JITTER + '#' + CPU + '#' + MEMORY + '#'  #preparing message
                    connection.sendall(mensagem.encode('utf8'))  #sending in first time the command to client
                    commands.update({(ID): {'CLOUD': CLOUD,'CLOUDIP': CLOUDIP, 'DATEHOUR': DATEHOUR,'CLOUDTONAME': CLOUDTONAME, 'CLOUDTOIP': CLOUDTOIP, 'STATUS': STATUS, 'PRICE': PRICE, 'LATTENCY': LATENCY, 'JITTER': JITTER , 'CPU': CPU , 'MEMORY': MEMORY ,'CONEXAO': connection}})
                if TIPO == 'SENDS':  #check the type protocol
                    mensagem = 'SENDC#' + ID + '#' + CLOUD + '#' + CLOUDIP + '#' + DATEHOUR + '#'+ CLOUDTONAME + '#' + CLOUDTOIP + '#' + STATUS + '#' + PRICE + '#' + LATENCY + '#' + JITTER + '#' + CPU + '#' + MEMORY + '#'
                    connection.sendall(mensagem.encode('utf8'))
                    commands.update({(ID): {'CLOUD': CLOUD,'CLOUDIP': CLOUDIP, 'DATEHOUR': DATEHOUR,'CLOUDTONAME': CLOUDTONAME, 'CLOUDTOIP': CLOUDTOIP, 'STATUS': STATUS, 'PRICE': PRICE, 'LATTENCY': LATENCY, 'JITTER': JITTER , 'CPU': CPU , 'MEMORY': MEMORY, 'CONEXAO': connection}})                   
                    nomearquivo=CLOUD+'_'+CLOUDIP+'_history.txt' #write data in file
                    with open(nomearquivo, 'a') as arquivo:
                        arquivo.write(DATEHOUR + ','+ CLOUD + ","+ CLOUDIP +","+ PRICE + ","+LATENCY+","+JITTER + "," + CPU + "," + MEMORY +'\r\n')
                    SearchChangePriceLatencyJitterPILL(PRICE,LATENCY,CLOUD,CLOUDTONAME) #execute function that search and change price pill

                    if CPU > THRESHOLD:
                        SearchGrowUpVimPrice(VIM_URL,GROW_RATE_PRICE) #The cost is multiplied by the GROW_RATE_PRICE if CPU is bigger than 

                if TIPO == 'EXCL': #Delete registry cloud in Dict
                    if ID.isdigit():
                        clouds.pop(ID)
        print('Closing connection with client', enderecoCliente)
        connection.close()
        
socketServer = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
HOST = "0.0.0.0"#endereco ip do servidor
PORT = 5000 #porta do servidor

socketServer.bind((HOST,PORT))
socketServer.listen(10)

print('Starting Server')
commands = {}
clouds = {}

try:
    thread_requestDataCloud = threading.Thread(target=requestDataCloud)
    thread_requestDataCloud.start()
    thread_printCloudsDict = threading.Thread(target=printCloudsDict)
    thread_printCloudsDict.start()
    while True:
        print("DEBUG: while criando thread")
        con, enderecoCliente = socketServer.accept()
        IPORIGEM, PORTAORIGEM= enderecoCliente
        thread_cliente = threading.Thread(target=conectado,args=(con,enderecoCliente,))
        thread_cliente.start()
        print("DEBUG: iniciado thread")
    print("Finalizando conexao do cliente", IP)
except KeyboardInterrupt:
    print('Tecla de interrupção acionada, saindo... Digite "Ctrl + C" mais uma vez.\n')
except Exception as e:
    print("Erro no cliente. " + str(e))
finally:
    print ("DEBUG: finalinzando thread")
    socketServer.close()



#proximos passos
#Executar o iperf como client e como server
# viabilizar estes comandos a cada 10 segundos( ver com oficará a fila se demorar) de preferencia via thread
#corrigir envio custo sem dados, so nome variavel
# latencia para o usuario e aterar pesos vnf baseado nisto
# ver se existe metrica de quantidade de vnf alocada
# ver se existe metrica para quantidade de cpu de um total da nuvem
# alterar aquivo no container a cada mudança
# fazer simulações com tc
 """