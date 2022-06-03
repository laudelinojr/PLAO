import requests
from PLAO_client2 import *

#IPUser to latency test between cloud and this
IPUSER=''

IP_PLASERVER = sys.argv[1] #Address Server PLAO SERVER IP
if sys.argv[1] == '':
    print ("Invalido: We need the IP PLAO SERVER.")
    exit()

OPERATION = sys.argv[2] #Operation
if sys.argv[2] == '':
    print ("Invalido: We need the Operation.")
    exit()

if sys.argv[2] == "userlatency":
    print ("Invalido: We need the Operation.")
    IPUSER = sys.argv[3] #IPUser to latency
    #Future: to valid the ip in third parameter
    if sys.argv[3] == '': 
        print ("Invalido: We need the user ip.")
        exit()

if sys.argv[2] == "sendjob":
    print ("Invalido: We need the Operation.")
    IPUSER = sys.argv[3] #IPUser to sendJob
    #Future: to valid the ip in third parameter
    if sys.argv[3] == '': 
        print ("Invalido: We need the user ip.")
        exit()

if sys.argv[2] == "selectMetricTime":
    START_DATE = sys.argv[3] #DATE for data
    STOP_DATE = sys.argv[4] #DATE for data
    if sys.argv[3] == '': 
        print ("Invalido: We need start date.")
        exit()
    if sys.argv[4] == '': 
        print ("Invalido: We need stop date.")
        exit()    
        
print("Conectando em "+IP_PLASERVER)
URL='http://'+IP_PLASERVER+':3332/'+OPERATION+"/"
print(URL)

#Future: Send in payload the parametrs of operations. for example the number packets latency and others
# The payload is the user ip address.
payload = {"ipuser" : str(IPUSER)} #, "startdate" : str(START_DATE), "stopdate" : str(STOP_DATE)}
#vnf1, vnf2, pesovnf1, pesovnf2, metrlimite, valmetrlimite, metrrestricao, valmetrrestricao, nsnome
# Request to start the application agent betwen clouds (ping and jitter). The server will request for the all clouds in enviroment.
a = requests.request(
    method="POST", url=str(URL), json=payload)
print(a.text)
