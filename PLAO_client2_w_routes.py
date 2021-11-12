#File in Clouds

from flask import Flask, request
from PLAO_client2 import Servers, OpenStack_Auth, Gnocchi,CreateThread

appc = Flask(__name__)

@appc.route("/plao/", methods=['POST', 'GET', 'DELETE'])
def latencia_user_plao():
    if request.method == "POST":
        print("entrei aqui")
        request_data = request.get_json()
        ip = request_data['ip']
        ip_user = request_data['ipuser']
        print (ip)
        print (ip_user)
        VarPlao="plao"
        servers = Servers()
        IPServerLocal=servers.getSearchIPLocalServer()
        print ("ipserver: "+IPServerLocal)
        NameServerLocal=servers.getServerName(IPServerLocal)
        print ("nameserver: "+NameServerLocal)
        auth_session = OpenStack_Auth(cloud_name=NameServerLocal)
        sess = auth_session.get_session()
        gnocchi = Gnocchi(session=sess)
        resource_id=gnocchi.get_resource_id(VarPlao)
        print ("idRrecurso: "+resource_id)
        print("Checking if metric Latency exists...")      
        Metric_Lat_test=""
        Name_Metric_Lat="Lat_To_"+str(ip_user)
        print(Name_Metric_Lat)
        Metric_Lat_test=gnocchi.get_metric_id(Name_Metric_Lat,resource_id)
        if (Metric_Lat_test == ""):
            print("depois if metric lat test")
            print("The "+ Name_Metric_Lat + " do not exist. Creating metric Latency.")
            if (gnocchi.set_create_metric(Name_Metric_Lat,VarPlao,resource_id,"ms") == "MetricaJaExiste" ):
                print ("Metric already exists.")            
            else:
                print("Created Metrics.")
        print("Iniciar Thread para aguardar pedidos de latencia para usuarios")
        Thread_Lat = CreateThread()
        print(Thread_Lat.ThreadPing(ip_user,"5","0",resource_id,gnocchi))
        return "ok"