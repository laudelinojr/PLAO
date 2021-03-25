import socket
import time
import sys
import datetime
import platform
import subprocess
import psutil
import os
import datetime
import uuid
import os


HOST = sys.argv[1] #Address Server OSM IP
if sys.argv[1] == '':
    print ("Invalido: We need the IP OSM Sever.")
    exit()

PORT = 6001 #Port Server

#Debug mode is 1
debug=1

# The values in config files of OSM need to be integer
QUANTITY_PCK="5" #Quantity packages to use in ping command 
DIR_IPERF="C:/Temp/artigo/utils/iperf/" #directory of iperf application

def DATAHORAC():
    DATAHORAC = datetime.datetime.now().strftime('%d.%m.%y-%H:%M:%S')  # convert hour to string
    return DATAHORAC

def GetLatency(TARGET,QUANTITY_PCK):
    #Test with ping to get latency.
    if platform.system().lower() == "linux":
        try:
            ping = subprocess.check_output(["/usr/sbin/ping", "-c", QUANTITY_PCK, TARGET])
        except:
            return "" #if return with error, return empty
        latency = ping.split()[-2]
        resp = str(latency, 'utf-8')
        resp2= resp.split("/")[2]
        return resp2
    else: # platform.system().lower() == "windows":
        try:
            ping = subprocess.check_output(["/usr/sbin/ping", "-n", QUANTITY_PCK, TARGET])
        except:
            return "" #if return with error, return empty
        latency = ping.split()[-1]
        resp = str(latency, 'utf-8')
        resp2= resp.split("=")[0]
        resp3=resp2.split("ms")[0]
        return resp3

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST,PORT)
tcp.connect(dest)

print ('Starting PING Collector ... ')
print ('To quit, use CTRL+C\n')

mensagem = 'PINGSENDS#' + '1' + '#' + 'CLOUDNAME_LOCAL' + '#' + 'CLOUDIP_LOCAL' + '#' + 'DATAHORAC()' + '#' + '#' + 'CLOUDTOIP' + '#' + 'STATUS' + '#' + 'PRICE' + '#' + 'LATENCY' + '#' + '0' + '#' + '0' + '#' + 'MEMORY'+ '#' + 'DISK'+ '#' + 'NVM' + '#' + '0' + '#' + 'MEMORYC' + '#' + 'DISKC' + '#'
tcp.sendall(mensagem.encode('utf8')) #send to server colletion data

try:
    while True:
        msg = tcp.recv(1024).decode("utf8")  #receive the message socket in byte and to convert in utf-8
        msg = msg.split('#')  #split message separeted in # symbol
        if len(msg) > 5:
            TIPO = msg[0] 
            ID = msg[1]
            CLOUD = msg[2] #NAME CLOUD
            CLOUDIP = msg[3] #IP CLOUD
            DATEHOUR = msg[4] #DATA AND HOUR
            USERIP = msg[5] #
            VNFD = msg[6] #IP OF CLOUD TO
            COMMAND = msg[7] 
            LATENCY = msg[9] #LATENCY

            if TIPO == 'PINGSENDC':
                time.sleep(2)
                LATENCY=str(round(float(GetLatency(CLOUDTOIP,QUANTITY_PCK))))
                #LATENCY=str(GetLatency(USERIP,QUANTITY_PCK)) #Get latency with ping, is necessary set quantity packages
                PRICE=LATENCY              
                mensagem = 'PINGSENDS#'+ ID + '#' + CLOUD + '#' + CLOUDIP + '#' + DATEHOUR + '#'+ USERIP + '#' + VNFD + '#' + COMMAND + '#' + LATENCY + '#'
                print (mensagem)
                tcp.sendall(mensagem.encode('utf8')) #send to server colletion data

        if not msg: break
except KeyboardInterrupt:
    print('Tecla de interrupção acionada, saindo... e solicitando exclusao do dispositivo no servidor.')
except Exception as e:
    print("Erro no cliente. " + str(e))
finally:
    mensagem = 'EXCL#' + ID + '#' + CLOUD + '#' + CLOUDIP + '#' + 'DATAHORAC()' + '#' + 'CLOUDTOIP' + '#' + 'STATUS' + '#' + 'PRICE' + '#' +'LATENCY' + '#' + 'JITTER' + '#' + 'CPU' + '#' + 'MEMORY'+ '#' + 'DISK'+ '#' + 'NVM' + '#' + 'CPUC' + '#'
    tcp.sendall(mensagem.encode('utf8'))
    tcp.close()