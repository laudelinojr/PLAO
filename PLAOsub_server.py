import yaml
import socket
import threading
import time
import subprocess

#Debug mode is 1
debug=0

#requisites1 SearchChangeVNFDPrice
FILE_VNF_PRICE="/opt/PLAO/osm/vnf_price_list.yaml"
NAME_VNFD="VNFB"
#VIM_URL='http://10.159.205.6:5000/v3'
PRICE_VNFD=14

#requisites SearchChangePriceLatencyJitterPIL
FILE_PIL_PRICE="/opt/PLAO/osm/pil_price_list.yaml"
PATH_LOG='/opt/PLAO/log/'

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

                TIPO = msg[0] 
                ID = msg[1]
                CLOUD = msg[2] #NAME CLOUD
                CLOUDIP = msg[3] #IP CLOUD
                DATEHOUR = msg[4] #DATA AND HOUR
                USERIP = msg[5] #
                VNFD = msg[6] #IP OF CLOUD TO
                COMANDO = msg[7] 
                LATENCY = msg[9] #LATENCY
             
                #fico lendo arquivo TXT USERIP,VNFD,COMANDO
                #se aparecer algo, os clientes irao verificar, fazer o ping e retornar  o valor, que será posto em outro arquivo txt
                #PING_FILA

                nomearquivo1='user_vnfd.txt'
                arquivo = open('seu-arquivo.text', 'w')
                    linha = arquivo.readline()
                arquivo.close()

                print(linha)


                #arquivo.write(DATEHOUR + ','+ USERIP + ","+ CLOUDIP +","+ CPU + "," + MEMORY + "," + NVM + "," + CPUC + "," + MEMORYC + ","+ DISKC +'\n')

                if TIPO == 'PINGSENDS':
                    sleep.time(5)
                    #USERIP':USERIP,'VNFD': VNFD, 'COMANDO': STATUS
                    #commands.update({('ID'): {'CLOUD': CLOUD,'CLOUDIP': CLOUDIP, 'DATEHOUR': DATEHOUR,'CLOUDTONAME': CLOUDTONAME, 'CLOUDTOIP': CLOUDTOIP, 'STATUS': STATUS, 'PRICE': PRICE, 'LATTENCY': LATENCY, 'JITTER': JITTER , 'CPU': CPU , 'MEMORY': MEMORY, 'CPUC': CPUC ,'MEMORYC': MEMORYC ,'DISKC': DISKC , 'CONEXAO': connection}})
                    mensagem = 'PINGSENDC#' + '1' + '#' + CLOUD + '#' + CLOUDIP + '#' + DATEHOUR + '#'+ CLOUDTONAME + '#' + CLOUDTOIP + '#' + STATUS + '#' + PRICE + '#' + LATENCY + '#' + JITTER + '#' + CPU + '#' + MEMORY + '#' + DISK+ '#' + NVM + '#' + CPUC + '#' + MEMORYC + '#'+ DISKC + '#'  #preparing message
                    connection.sendall(mensagem.encode('utf8'))  #sending in first time the command to client

                if TIPO == 'PINGSENDC':
                 #   commands.update({('ID'): {'CLOUD': CLOUD,'CLOUDIP': CLOUDIP, 'DATEHOUR': DATEHOUR,'CLOUDTONAME': CLOUDTONAME, 'CLOUDTOIP': CLOUDTOIP, 'STATUS': STATUS, 'PRICE': PRICE, 'LATTENCY': LATENCY, 'JITTER': JITTER , 'CPU': CPU , 'MEMORY': MEMORY, 'CPUC': CPUC ,'MEMORYC': MEMORYC ,'DISKC': DISKC , 'CONEXAO': connection}})
                  #  mensagem = 'SENDC#' + ID + '#' + CLOUD + '#' + CLOUDIP + '#' + DATEHOUR + '#'+ CLOUDTONAME + '#' + CLOUDTOIP + '#' + STATUS + '#' + 'PRICE' + '#' + 'LATENCY' + '#' + '0' + '#' + 'CPU' + '#' + 'MEMORY' + '#' + 'DISK' + '#' + 'NVM' + '#' + 'CPUC' + '#'+ 'MEMORYC' + '#'+ 'DISKC' + '#'
                    mensagem = "testepingsendc"
                    connection.sendall(mensagem.encode('utf8'))

                if TIPO == 'EXCL': #Delete registry cloud in Dict
                    if ID.isdigit():
                        ping.pop(ID)
        print('Closing connection with client', enderecoCliente)
        connection.close()



#Configurations for socket enviroment
socketServer = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
HOST = "0.0.0.0"#address ip to server
PORT = 6001 #port to server
socketServer.bind((HOST,PORT))
socketServer.listen(10)
print('Starting Controller PLAO Server for OSM')

#Dictionaries for application use.
commands = {}
ping = {}

try:
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