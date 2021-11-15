import yaml
import threading
import subprocess
from datetime import date,timedelta
from PLAO_client2 import *
#from PLAO2_w_routes import app
from flask import Flask, request
import requests

#Teste para servidor requisicoes
#from PLAO2_w_routes import app

#FILE_VNF_PRICE="/opt/PLAO/osm/vnf_price_list.yaml"
#FILE_PIL_PRICE="/opt/PLAO/osm/pil_price_list.yaml"
FILE_VNF_PRICE="teste/vnf_price_list.yaml"
FILE_PIL_PRICE="teste/pil_price_list.yaml"
THRESHOLD=90 #THRESHOLD of CPU to apply rate in Cloud's price
PATH_LOG='log/'
#PATH_LOG='/opt/PLAO/log/'
PATH='/opt/PLAO/'
#Debug mode is 1
debug=0
debug_file = 0 #keep 0
#requisites for change all price of specif VIM (Cloud)
DOWN_UP_PRICE=10 #Number to add vnf Price

#classe arquivo vnfd

#Classe monitorar arquivo entrada_comandos_legado

#classe enviar ip para controladores clientes

class File_VNF_Price():
    def __init__(self):
        self.A=open(FILE_VNF_PRICE, )
        self.B=yaml.full_load(self.A)
        self.C = len(self.B)
        self.D = len(self.B[0]['prices'])

    #Search VNFD in configuration file vnf_price_list and return position in file
    #If no result, return -1 
    def SearchVNFD(self, NAME_VNFD):
        #C = len(self.B) #Elements
        for i in range(self.C):
            if self.B[i]['vnfd'] == NAME_VNFD: #Search and compare the VNFD name
                return i
        else:
            return -1

    #First, use the SearchVNFD function, after, this.
    #Change price of specific VIMNAME using the index (position) OF VNFD in vnf_price_list.
    #Change only in MEMORY. If no result, return -1  
    # In this, the target is to change the price cloud for specif Cloud (VIM)
    # If the CPU High - degraded (1), we add the extra THRESHOLD value in Price.
    def ChangeVNFPrice(self,COD_VNFD,VIMURL,PRICE,CLOUD_STATUS_CPU):
        C = len(self.B[COD_VNFD]['prices']) #Elements
        print(C)

        if COD_VNFD < 0:
            return -1   
        for i in range(C):
            if self.B[COD_VNFD]['prices'][i]['vim_url'] == VIMURL: #Compare VIMURL between YAML and the new
                if self.B[COD_VNFD]['prices'][i]['price'] != PRICE:  #Compare new PRICE with actual Price, if equal, no change
                    if (CLOUD_STATUS_CPU == 1):
                        print(self.B[COD_VNFD]['prices'][i]['price'])
                        self.B[COD_VNFD]['prices'][i]['price']=int(PRICE)+THRESHOLD #Change the VNF Price
                        print(self.B[COD_VNFD]['prices'][i]['price'])
                    else:
                        self.B[COD_VNFD]['prices'][i]['price']=int(PRICE) #Change the VNF Price
                    return i
                else:
                    return -1
        else:
            return -1

    #Change VNF File with new Price, change the file
    def SearchChangeVNFDPrice(self,NAME_VNFD,VIM_URL,PRICE_VNFD,CLOUD_STATUS_CPU):
        if debug == 1: print("In SearchChangeVNFDPrice")
        if (self.ChangeVNFPrice(self.SearchVNFD(NAME_VNFD),VIM_URL,PRICE_VNFD,CLOUD_STATUS_CPU)) != -1: #Change price of specific VIM in specific VNFD
            if debug == 1: print("In ChangeVNFPrice(SearchVNFD")
            with open(FILE_VNF_PRICE, 'w') as file:
                documents = yaml.dump(self.B, file, sort_keys=False) #Export changes to file without order, equal original file
            if debug == 1: print("going to copy to SearchChangeVNFDPrice ")
            print("lembrar descomentar linha para docker fazer copia vnf")
            #####ExecuteCommand('docker cp '+FILE_VNF_PRICE+' '+'$(docker ps -qf name=osm_pla):/placement/')  

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

    #Receive the CPU STATUS NOW and update in list cloud, the CLOUD_STATUS_CPU
    def SearchDownUpVimPrice(self,STATUS_CPU_NOW,Cloud):    #VIM_URL,CLOUD_COD,STATUS_CPU_NOW):
        VIM_URL=Cloud.getVimURL() # Get vim url for use in next operations
        CLOUD_STATUS_CPU=Cloud.getCpuStatus() #int(clouds.get(str(CLOUD_COD)).get('CPU')) #Values: 0-cpu normal, 1-cpu high and cost value changed
        PRICE=0 #Inicialize local variable
        CHANGED_PRICE_VIM_URL=0 #count auxiliar variable for count the total changes

        for i in range(self.C): #Search and change all the all vim url price for specific cloud
            for f in range(self.D):
                if self.B[i]['prices'][f]['vim_url'] == VIM_URL: #Compare VIMURL between YAML and the new
                        PRICE=self.B[i]['prices'][f]['price']  #Select the price of this vim_url
                        print(VIM_URL)
                        print(PRICE)
                        if PRICE >= 0:
                            #If the cloud CPU now is high (1), but in dict is normal (0), we need change dict to(1);
                            if STATUS_CPU_NOW == 1 and CLOUD_STATUS_CPU == 0: 
                                Cloud.setCpuStatus(1)
                                self.B[i]['prices'][f]['price']=PRICE+DOWN_UP_PRICE #Change the VNF Price with the rate price
                                CHANGED_PRICE_VIM_URL=CHANGED_PRICE_VIM_URL+1 #count auxiliar variable
                                print (self.B[i]['prices'][f]['price'])

                            #If the cloud CPU now is ok (0), but in dict is high (1), we need change dict to (0)
                            if STATUS_CPU_NOW == 0 and CLOUD_STATUS_CPU == 1 and PRICE >= DOWN_UP_PRICE: 
                                Cloud.setCpuStatus(0)
                                self.B[i]['prices'][f]['price']=int(PRICE-DOWN_UP_PRICE) #Change the VNF Price with the rate price
                                CHANGED_PRICE_VIM_URL=CHANGED_PRICE_VIM_URL+1 #count auxiliar variable
                                print(self.B[i]['prices'][f]['price'])

                            #If the cloud CPU now is ok (0), but in dict is high (1), we need change dict to (0)
                            if STATUS_CPU_NOW == 0 and CLOUD_STATUS_CPU == 1 and PRICE <= DOWN_UP_PRICE: 
                                Cloud.setCpuStatus(0)
                                self.B[i]['prices'][f]['price']=0 #Change the VNF Price with the rate price
                                CHANGED_PRICE_VIM_URL=CHANGED_PRICE_VIM_URL+1 #count auxiliar variable
                                print(self.B[i]['prices'][f]['price'])
                        else:
                            print("Trying update nvf_price file. There are price<=0. Check this.")

        if debug ==1: print ("DEBUG: Changed "+str(CHANGED_PRICE_VIM_URL)+" PRICES VIM_URL (CLOUDS).") #Print count auxiliar variable
        if CHANGED_PRICE_VIM_URL > 0:
            with open(FILE_VNF_PRICE, 'w') as file:
                documents = yaml.dump(self.B, file, sort_keys=False) #Export changes to file without order, equal original file
            print ("CPU CHANGE: File pil_price changed because High CPU.")

            nomearquivo5=PATH_LOG+'CPU_TRIGGER_'+ Cloud.getName() +'_history.txt' #write data in file
            with open(nomearquivo5, 'a') as arquivo:
                arquivo.write(DATEHOURS() + ','+ Cloud.getName() + ","+ Cloud.getIP() +","+ str(STATUS_CPU_NOW)+'\n')
            print("lembrar de descomentar")
            #ExecuteCommand('docker cp '+FILE_VNF_PRICE+' '+'$(docker ps -qf name=osm_pla):/placement/')
            try:
                nomearquivo6=PATH_LOG+'CONFIG_OSM_history.txt' #write data in file
                with open(nomearquivo6, 'a') as arquivo:
                    arquivo.write(DATEHOURS() + '#CHANGE_VNFD_ALL# Changed and copied file '+ FILE_VNF_PRICE + ' to container PLA. Add values in All prices to Cloud: '+VIM_URL+ '.' +'\n')
            except:
                return -1

class File_PIL_Price():
    def __init__(self):
        self.A=open(FILE_PIL_PRICE, )
        self.B=yaml.full_load(self.A)
        self.C = len(self.B['pil'])
        #self.D = len(self.B[0]['prices'])

    #Search in file the cloud math between from and to, in this order. If located, stop the search
    def SearchChangePILPrice(self, OPENSTACK_FROM,OPENSTACK_TO):
        for i in range(self.C):
            if self.B['pil'][i]['pil_endpoints'][0] == OPENSTACK_FROM:# or B['pil'][i]['pil_endpoints'][0] == OPENSTACK_TO:
                if self.B['pil'][i]['pil_endpoints'][1] == OPENSTACK_TO:# or B['pil'][i]['pil_endpoints'][1] == OPENSTACK_FROM:
                    return i
        return -1

    #Search cloud combination and change the price, latency and jitter
    def SearchChangePriceLatencyJitterPIL(self, PRICE,LATENCY,JITTER,OPENSTACK_FROM,OPENSTACK_TO):
        CLOUD_COD=self.SearchChangePILPrice(OPENSTACK_FROM,OPENSTACK_TO)
        #if debug == 1: print("CLOUD_COD: "+str(CLOUD_COD))
        if CLOUD_COD != -1:
            if (self.ChangePriceLatencyJitterPIL(CLOUD_COD,PRICE,LATENCY,JITTER)) != -1: #Change Price Latency and Jitter
                with open(FILE_PIL_PRICE, 'w') as file:
                    documents = yaml.dump(self.B, file, sort_keys=False) #Export changes to file without order, equal original file

                print("lembrar descomentar linha para docker fazer copia pil")
                ############ExecuteCommand('docker cp '+FILE_PIL_PRICE+' '+'$(docker ps -qf name=osm_pla):/placement/')

                try:
                    nomearquivo8=PATH_LOG+'CONFIG_OSM_history.txt' #write data in file
                    with open(nomearquivo8, 'a') as arquivo:
                        arquivo.write( DATEHOURS() + '#CHANGE_PIL# Changed and copied file '+FILE_PIL_PRICE + ' to container PLA. ' +' PRICE: '+PRICE+' LATENCY: '+LATENCY+' JITTER: '+JITTER+'\n')
                except:
                    return -1
                if debug == 1: print("File pil_price changed")
            else:
                if debug == 1: print ("File pil_price not changed")

    def ChangePriceLatencyJitterPIL(self, CLOUD_COD,PRICE,LATENCY,JITTER):
        #if debug == 1: print ("entrei dentro de ChangePriceLatencyJitterPIL")
        #if debug == 1: print(PRICE)
        #if debug == 1: print(LATENCY)
        #if debug == 1: print(JITTER)
        PRICE=round(float(PRICE))
        LATENCY=round(float(LATENCY))
        JITTER=round(float(JITTER))
        if ((self.B['pil'][CLOUD_COD]['pil_price'] != PRICE) or (self.B['pil'][CLOUD_COD]['pil_latency'] != LATENCY) or (self.B['pil'][CLOUD_COD]['pil_jitter'] != JITTER)): #Change just one this values is different of the entry
            self.B['pil'][CLOUD_COD]['pil_price']=PRICE #change the price
            self.B['pil'][CLOUD_COD]['pil_latency']=LATENCY #change the latency - same price
            self.B['pil'][CLOUD_COD]['pil_jitter']=JITTER #change the jitter
            if debug == 1: print ("PRICE, LATENCIA e JITTER alterados no arquivo pil_price_list.yaml.")
            return 0
        else:
            return -1

def DATEHOURS():
    DATEHOUR = datetime.now().strftime('%d.%m.%y-%H:%M:%S')  # converte hora para string do cliente
    return DATEHOUR

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

#Collect metric links from cloud1 to cloud2
def Collector_Metrics_Links(cloud1_gnocchi,cloud1_resource_id,cloud2,PILFile,CLOUD_FROM,CLOUD_TO):
    while True:
        now=datetime.now()
        intervalo=30
        delta = timedelta(seconds=intervalo)
        time_past=now-delta
        #START = "2021-08-01 13:30:33+00:00"
        #STOP = "2021-08-01 13:35:36+00:00"
        START=time_past
        STOP=now
        GRANULARITY=60.0
        print("horarioInicio: "+str(START))
        print("hoarioFinal: "+str(STOP))
        Latencia_to_cloud2=cloud1_gnocchi.get_last_measure("Lat_To_"+cloud2.getIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)
        print(Latencia_to_cloud2)
        Jitter_to_cloud2=cloud1_gnocchi.get_last_measure("Jit_To_"+cloud2.getIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)
        print(Jitter_to_cloud2)
        PILFile.SearchChangePriceLatencyJitterPIL(Latencia_to_cloud2,Latencia_to_cloud2,Jitter_to_cloud2,CLOUD_FROM,CLOUD_TO)
        time.sleep(5)

#Collect metric links from cloud1 to cloud2
def Monitor_Request_LatencyUser_Cloud1(cloud1_gnocchi,cloud1_resource_id,VNFFile,CLOUD_FROM):
    while True:
        now=datetime.now()
        intervalo=30
        delta = timedelta(seconds=intervalo)
        time_past=now-delta
        #START = "2021-08-01 13:30:33+00:00"
        #STOP = "2021-08-01 13:35:36+00:00"
        START=time_past
        STOP=now
        GRANULARITY=60.0
        print("horarioInicio: "+str(START))
        print("hoarioFinal: "+str(STOP))
        #Latencia_to_cloud2=cloud1_gnocchi.get_last_measure("Lat_To_"+cloud2.getIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)
        #print(Latencia_to_cloud2)
        #Jitter_to_cloud2=cloud1_gnocchi.get_last_measure("Jit_To_"+cloud2.getIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)
        #print(Jitter_to_cloud2)
        #PILFile.SearchChangePriceLatencyJitterPIL(Latencia_to_cloud2,Latencia_to_cloud2,Jitter_to_cloud2,CLOUD_FROM,CLOUD_TO)
        #time.sleep(5)

def Collector_Metrics_Disaggregated_cl1(cloud1_gnocchi,cloud1_resource_id_nova,Cloud,VNFFile):
    while True:
        now=datetime.now()
        intervalo=400
        delta = timedelta(seconds=intervalo)
        time_past=now-delta
        START=time_past
        STOP=now
        GRANULARITY=60.0
        print("horarioInicio: "+str(START))
        print("hoarioFinal: "+str(STOP))
        CPU_cloud1=cloud1_gnocchi.get_last_measure("compute.node.cpu.idle.percent",cloud1_resource_id_nova,None,GRANULARITY,START,STOP)
        print (CPU_cloud1)
        print("url da cloud na thread")
        print(Cloud.getVimURL())
        print("cpu atual da cloud")
        print(CPU_cloud1)
        print("status da cpu")
        print(Cloud.getCpuStatus())

        if (int(CPU_cloud1) > THRESHOLD) and (Cloud.getCpuStatus() == 0):
            CPU_STATUS_NOW=1   #Values: 0-cpu normal, 1-cpu high and cost value going to change
            VNFFile.SearchDownUpVimPrice(CPU_STATUS_NOW,Cloud) #The cost is add by CPU bigger
        if (int(CPU_cloud1) < THRESHOLD) and (Cloud.getCpuStatus() == 1):
            CPU_STATUS_NOW=0   #Values: 0-cpu normal, 1-cpu high and cost value going to change
            VNFFile.SearchDownUpVimPrice(CPU_STATUS_NOW,Cloud) #The cost is add by CPU bigger
        time.sleep(5)


def Collector_Metrics_VNF():
    pass


def main():
    print ("Iniciando Server PLAO")
    VNFFile = File_VNF_Price()
    PILFile = File_PIL_Price()

    NAME_VNFD="VNFA"

    #print receber a posicao do VNF no arquivo confi VNF OSM
    #print("testando SearchVNFD")
    #teste1 = VNFFile.SearchVNFD(NAME_VNFD)
    #print(teste1)
    #print("     ")

    #print("testando ChangeVNFPrice")
#    VIM_URL="http://10.159.205.6:5000/v3"
#    PRICE_VNFD=78
#    CLOUD_STATUS_CPU=1 #1 se a cpu estiver degradada
    #teste2 = VNFFile.ChangeVNFPrice(2,VIM_URL,PRICE_VNFD,CLOUD_STATUS_CPU)
    #print(teste2)

#    print("testando SearchChangeVNFDPrice") #Este devera se executaod por thrad que ira coletar das nuvens a latencia e cpu para formar o custo da VNF
#    VNFFile.SearchChangeVNFDPrice(NAME_VNFD,VIM_URL,PRICE_VNFD,CLOUD_STATUS_CPU)

    servers = Servers()

    cloud1 = Cloud(servers.getbyIndexIP(0))
    cloud1.setName(servers.getServerName(cloud1.getIp()))
    cloud1.setVimURL("http://10.159.205.6:5000/v3")
    cloud1.getVimURL()
    print(cloud1.getIp())
    print(cloud1.getCpu())
    print(cloud1.getName())

    cloud2 = Cloud(servers.getbyIndexIP(1))
    cloud2.setName=servers.getServerName(cloud2.getIp)
    cloud2.setVimURL("http://10.159.205.11:5000/v3")
    print(cloud2.getIp())
    print(cloud2.getVimURL())
    print(cloud2.getCpu())

    print("Creating session in Openstack1...")
    #Creating session OpenStack
    #auth_session = OpenStack_Auth(cloud_name=VarCloudName)
    cloud1_auth_session = OpenStack_Auth(cloud_name=cloud1.getName())
    cloud1_sess = cloud1_auth_session.get_session()
    print("Creating object and using session in Gnocchi...")
    #Insert Session in Gnocchi object   
    cloud1_gnocchi = Gnocchi(session=cloud1_sess)
    cloud1_resource_id=cloud1_gnocchi.get_resource_id("plao")
    print ("resource_id: "+cloud1_resource_id) 
    cloud1_resource_id_nova=cloud1_gnocchi.get_resource_id("nova_compute")
    print ("resource_id: "+cloud1_resource_id_nova) 

    print("Creating session in Openstack2...")
    #Creating session OpenStack
    #auth_session = OpenStack_Auth(cloud_name=VarCloudName)
#    cloud2_auth_session = OpenStack_Auth(cloud_name=cloud2.getName())
#    cloud2_sess = cloud2_auth_session.get_session()
#    print("Creating object and using session in Gnocchi...")
    #Insert Session in Gnocchi object   
#   cloud2_gnocchi = Gnocchi(session=cloud2_sess)
#    cloud2_resource_id=cloud1_gnocchi.get_resource_id("plao")   
#    print ("resource_id: "+cloud1_resource_id)




#    teste(Gnocchi,cloud1_resource_id,cloud2.getIp(),GRANULARITY,START,STOP)
    #Latencia_to_cloud2=cloud1_gnocchi.get_last_measure("Lat_To_"+cloud2.getIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)
    #print (Latencia_to_cloud2)
    #Latencia_to_cloud2=cloud1_gnocchi.get_last_measure("Lat_To_"+cloud2.getIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)

    #Latencia_to_cloud2 = Latencia_to_cloud2.drop(["granularity","timestamp"],axis=1)
    #teste_Latencia_to_cloud2=Latencia_to_cloud2.head(1)
    #teste_Latencia_to_cloud2=Latencia_to_cloud2.head(1).values
    ##print("valorLatenciatoCloud2: "+str(Latencia_to_cloud2))
    ##print (Latencia_to_cloud2)
    ##Jitter_to_cloud2=cloud1_gnocchi.get_last_measure("Jit_To_"+cloud2.getIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)
    #print (Latencia_to_cloud2)
    #Latencia_to_cloud2 = Latencia_to_cloud2.drop(["granularity","timestamp"],axis=1)
    #teste_Latencia_to_cloud2=Latencia_to_cloud2.head(1)
    #teste_Latencia_to_cloud2=Latencia_to_cloud2.head(1).values
   ##print("valorJittertoCloud2: "+str(Jitter_to_cloud2))

    #Thread para atualizar Price, Latency and jitter between cloud1 and 2
    thread_MonitorLinks = threading.Thread(target=Collector_Metrics_Links,args=(cloud1_gnocchi,cloud1_resource_id,cloud2,PILFile,"openstack1","openstack2"))
    thread_MonitorLinks.start()

    ###thread_MonitorDisaggregated1 = threading.Thread(target=Collector_Metrics_Disaggregated_cl1,args=(cloud1_gnocchi,cloud1_resource_id_nova,cloud1,VNFFile))
    ####thread_MonitorDisaggregated1.start()

#    thread_MonitorDisaggregated2 = threading.Thread(target=Collector_Metrics_Disaggregated_cl1,args=(cloud2_gnocchi,cloud2_resource_id,cloud2,VNFFile))
#    thread_MonitorDisaggregated2.start()


    try:
        print("teste")


        #File in Clouds
        app = Flask(__name__)

        # The payload is the user ip address.
        nuvem1="10.159.205.8"
        nuvem2="10.159.205.11"

        @app.route('/start/',methods=['POST'])
        def start():
            if request.method == "POST":
                request_data = request.get_json()
                payload = request_data['ipuser']
                a = requests.request(
                    method="POST", url='http://'+nuvem1+':3333/start/', json=payload)
                print(a.text)
                a = requests.request(
                    method="POST", url='http://'+nuvem2+':3333/start/', json=payload)
                print(a.text)
                return "okstart"
        @app.route("/plaoserver/", methods=['POST', 'GET', 'DELETE'])
        def latencia_user_plao():
            if request.method == "POST":
                request_data = request.get_json()
                controle=0
                print("Inicio Teste na nuvem 1")
                # Request to cloud. Is necessary in http URL the cloud ip address
                a = requests.request(
                    method="POST", url='http://'+nuvem1+':3333/plao/', json=request_data)
                print(a.text)
                print("Fim Teste na nuvem 1")
                print("Inicio Teste na nuvem 2")
                a = requests.request(
                    method="POST", url='http://'+nuvem2+':3333/plao/', json=request_data)
                print(a.text)
                print("Fim Teste na nuvem 2")
                return "okplaoserver"


        #servers = Servers()
        IPServerLocal="10.159.205.10"
        #Alterar para IP do servidor do PLAO
        app.run(IPServerLocal, '3332',debug=True)

    except ConnectionRefusedError as e:
        print ("Problema conexao com "+e)

    #Thread para enviar request 
    ###thread_MonitorLatencyUser = threading.Thread(target=Request_LatencyUser_Cloud1,args=(cloud1_gnocchi,cloud1_resource_id,cloud2,VNFFile,"openstack1","openstack2"))
    ###thread_MonitorLatencyUser.start()


    #Jitter_to_cloud2=cloud1_gnocchi.get_measure("Jit_To_"+cloud2.getIp(),cloud1_resource_id,None,GRANULARITY,START,STOP)
    #Jitter_to_cloud2 = Jitter_to_cloud2.drop("granularity",axis=1)
    #dataset = Latencia_to_cloud2.merge(Jitter_to_cloud2, how='left',on='timestamp',suffixes=["Lat_To_"+cloud2.getIp(),"Jit_To_"+cloud2.getIp()])
    #print(dataset)

    #DataSet(cloud1_gnocchi)

    #Creating vector with objects Cloud 
    #To add clouds in vector
    #clouds = []
    #for i in range(servers.getServerQtd()):
    #    clouds.append(Cloud(servers.getbyIndexIP(i))) 
    #for i in range(len(clouds)):
    #    print(clouds[i].getIp())
    #clouds[0].setCpu(20)
    #print (clouds[0].getCpu())
    #https://www.geeksforgeeks.org/how-to-create-a-list-of-object-in-python-class/
    
if __name__ == "__main__":
    main()