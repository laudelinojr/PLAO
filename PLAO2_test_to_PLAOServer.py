import requests
from PLAO_client2 import *

#IPUser to latency test between cloud and this
IPUSER=''
START_DATE=''
STOP_DATE='' 
METRIC_NAME=''
CLOUD_COD=''
TYPE=''

IP_PLASERVER = sys.argv[1] #Address Server PLAO SERVER IP
if sys.argv[1] == '':
    print ("Invalido: We need the IP PLAO SERVER.")
    exit()

METHOD_HTTP = sys.argv[2] #Type
if sys.argv[2] == '':
    print ("Invalido: We need the TYPE GET OR POST.")
    exit()

OPERATION = sys.argv[3] #Operation
if sys.argv[3] == '':
    print ("Invalido: We need the Operation.")
    exit()

if sys.argv[3] == "userlatency":
    print ("Invalido: We need the Operation.")
    IPUSER = sys.argv[4] #IPUser to latency
    #Future: to valid the ip in third parameter
    if sys.argv[4] == '': 
        print ("Invalido: We need the user ip.")
        exit()

if sys.argv[3] == "sendjob":
    print ("Invalido: We need the Operation.")
    IPUSER = sys.argv[4] #IPUser to sendJob
    CONSTRAINT_OPERATION = sys.argv[5] #Send operational
    #Future: to valid the ip in third parameter
    if sys.argv[4] == '': 
        print ("Invalido: We need the user ip.")
        exit()
    if sys.argv[5] == '': 
        print ("Invalido: We need the operation.")
        exit()

if sys.argv[3] == "selectMetricTime":
    START_DATE = sys.argv[4] #DATE for data
    STOP_DATE = sys.argv[5] #DATE for data
    METRIC_NAME = sys.argv[6] #DATE for data
    CLOUD_COD = sys.argv[7] #DATE for data
    if sys.argv[4] == '': 
        print ("Invalido: We need start date.")
        exit()
    if sys.argv[5] == '': 
        print ("Invalido: We need stop date.")
        exit()    
    if sys.argv[6] == '': 
        print ("Invalido: We need stop date.")
        exit()  
    if sys.argv[7] == '': 
        print ("Invalido: We need stop date.")
        exit()  
        
print("Conectando em "+IP_PLASERVER)
URL='http://'+IP_PLASERVER+':3332/'+OPERATION+"/"
print(URL)

#Future: Send in payload the parametrs of operations. for example the number packets latency and others
# The payload is the user ip address.
payload = {"ipuser" : str(IPUSER) , "constraint_operation" : str(CONSTRAINT_OPERATION),"startdate" : str(START_DATE), "stopdate" : str(STOP_DATE), "metricname" : str(METRIC_NAME), "cloudcod" : CLOUD_COD}
#vnf1, vnf2, pesovnf1, pesovnf2, metrlimite, valmetrlimite, metrrestricao, valmetrrestricao, nsnome
# Request to start the application agent betwen clouds (ping and jitter). The server will request for the all clouds in enviroment.
a = requests.request(
    method=METHOD_HTTP, url=str(URL), json=payload)
print(a.text)

#python.exe .\PLAO2_test_to_PLAOServer.py 127.0.0.1 GET selectMetricTime '2022-06-05 09:05:00' '2022-06-05 13:36:00'
#python.exe .\PLAO2_test_to_PLAOServer.py 127.0.0.1 GET selectMetricTime '2022-06-05 09:05:00' '2022-06-05 13:36:00' Lat_To_200.137.75.160  1
#python.exe .\PLAO2_test_to_PLAOServer.py 127.0.0.1 GET selectMetricTime '2022-06-05 09:05:00' '2022-06-05 13:36:00' Lat_To_200.137.82.21 2  
#python.exe .\PLAO2_test_to_PLAOServer.py 127.0.0.1 GET selectMetricTime