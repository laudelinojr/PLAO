import requests
from PLAO_client2 import *


IP_PLASERVER = sys.argv[1] #Address Server PLAO SERVER IP
if sys.argv[1] == '':
    print ("Invalido: We need the IP PLAO SERVER.")
    exit()

OPERATION = sys.argv[2] #Operation
if sys.argv[2] == '':
    print ("Invalido: We need the Operation.")
    exit()

IPUSER = sys.argv[3] #IPUser to latency
#Future: to valid the ip in third parameter
if (sys.argv[2] == 'plaoserver')and(sys.argv[3] == ''): 
    print ("Invalido: We need the user ip.")
    exit()

#Future: Send in payload the parametrs of operations. for example the number packets latency and others
# The payload is the user ip address.
payload = {"ipuser" : str(IPUSER)}

# Request to start the application agent betwen clouds (ping and jitter). The server will request for the all clouds in enviroment.
a = requests.request(
    method="POST", url='http://'+IP_PLASERVER+':3332/'+OPERATION+"/'", json=payload)
print(a.text)






# Request to cloud. Is necessary in http URL the cloud ip address
##a = requests.request(
##    method="POST", url='http://10.159.205.10:3332/plaoserver/', json=payload)

##print(a.text)