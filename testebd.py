from ast import Try
from cgi import test
import csv
from distutils.util import execute
from http.client import HTTPConnection
from multiprocessing.connection import Connection
from operator import contains, eq
from random import randint
from sqlite3 import Date
from uuid import NAMESPACE_X500, uuid4
import uuid
from webbrowser import get
from wsgiref.validate import validator
from attr import has
#import bson
from certifi import where
from psutil import users
import yaml
import threading
import subprocess
from datetime import date,timedelta
from PLAO_client2 import *
#from PLAO2_w_routes import app
from flask import Flask, request
import requests
from database.models import *
import time
import openpyxl

#Block to active log
import logging
logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

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

def DATEHOURS():
    DATEHOUR = datetime.now().utcnow().strftime('%d.%m.%y-%H:%M:%S')  # converte hora para string do cliente
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

def DATEHOURS():
    DATEHOUR = datetime.now().utcnow().strftime('%d.%m.%y-%H:%M:%S')  # converte hora para string do cliente
    return DATEHOUR

def InsertUser(name0, username0, password0):
    TestUsers=Users.get_or_none(Users.username_user==username0)
    if TestUsers is None:
        return Users.insert(
            name_user = name0,
            username_user = username0,
            password_user = password0,
            creation_date_user = datetime.now().utcnow()
        ).execute()
    else:
        -1

def InsertMethods(name):
    return Methods.insert(
        name_methods = name
    ).execute()

def InsertDataTestsTypes(name):
    return Data_Tests_Types.insert(
        name_data_tests = name
    ).execute()

def InsertDataTests(date, id_test, id_data_test_type, id_cloud ):
    return Data_Tests.insert(
        date_data_tests = date,
        fk_tests = id_test,
        fk_data_tests_types = id_data_test_type,
        fk_cloud = id_cloud
    ).execute()

def InsertTests(desc):
    return Tests.insert(
        description = desc,
        start_date_test = datetime.timestamp(datetime.now().utcnow())
    ).execute()

def InsertActionsTestsTypes(name_test_type):
    return Actions_Tests_Types.insert(
        name_action_test_type = name_test_type
    ).execute()

def InsertActionsTests(id_fk_test,cod_test_type,date_actions_tests):
    return Actions_Tests.insert(
        date_actions_tests = date_actions_tests,
        fk_tests = id_fk_test,
        fk_actions_tests_types = cod_test_type
    ).execute()

def InsertTestsMethods(cod_test,cod_method):
    return Tests_Methods.insert(
        start_date_test_methods = datetime.timestamp(datetime.now().utcnow()),
        fk_tests = cod_test,
        fk_methods=cod_method
    ).execute()

def InsertDegradationVnfType(nametype):
    return Degradations_Vnfs_Clouds_Types.insert(
        creation_date_degradations_vnfs_clouds_types=datetime.now().utcnow(),
        name_degradations_vnfs_clouds_types = nametype
    ).execute()


def UpdateFinishTestsMethods(cod_method_test):
    return Tests_Methods.update(finish_date_test_methods=datetime.timestamp(datetime.now().utcnow())).where(Tests_Methods.id_tests_methods==cod_method_test).execute()
    #print(datetime.timestamp(datetime.now().utcnow()))
    #time.sleep(2)
    #return timetestmethod

def UpdateFinishDateTestsbyId(id):
    return Tests.update(finish_date_test=datetime.timestamp(datetime.now().utcnow())).where(Tests.id_tests==id).execute()
    #print(datetime.timestamp(datetime.now().utcnow()))
    #time.sleep(2)
    #return timetest

#def UpdateFinishTestsMethods(cod_method_test):
#    return Tests_Methods.update(finish_date_test_methods=datetime.now().utcnow()).where(Tests_Methods.id_tests_methods==cod_method_test).execute()

#def UpdateFinishDateTestsbyId(id):
#    return Tests.update(finish_date_test=datetime.now().utcnow()).where(Tests.id_tests==id).execute()

def InsertJob(userip0, nsd_name0,cod_fkuser,cod_status, cod_test):
    return Jobs.insert(
        userip_job = userip0,
        start_date_job = datetime.now().utcnow(),
        nsd_name_job=nsd_name0,
        fk_user = cod_fkuser,
        fk_status = cod_status,
        fk_tests = cod_test
    ).execute()

def UpdateJob(job_id, job_status):
    Jobs.update(fk_status = job_status,finish_date_job = datetime.now().utcnow()).where(Jobs.id_job==job_id).execute()
    return "ExecutedUpdate"

def insertJobVnfCloud(cost_vnf,id_fk_job,id_fk_vnf,id_fk_cloud,vnf_threshold,vnf_threshold_type,degradation_monitoring_value):
    return Jobs_Vnfs_Clouds.insert(
        cost = cost_vnf,
        fk_job = id_fk_job,
        fk_vnf = id_fk_vnf,
        fk_cloud = id_fk_cloud,
        degradation_threshold_jobs_vnfs_clouds = vnf_threshold,
        fk_degradation_vnfs_clouds_types = vnf_threshold_type,
        degradation_monitoring_value_now_jobs_vnfs_clouds = degradation_monitoring_value,
        creation_date = datetime.now().utcnow()
    ).execute()

def InsertStatusNsInstanced(name):
    return Status_NS_Instanciateds.insert(
        name_osm_status_ns_instanciated = name,
        creation_date_status_ns_instanciated = datetime.now().utcnow()
    ).execute()  

def InsertNsInstanciated(name0,id_osm0,id_status0,id_job0):
    return NS_Instanciateds.insert(
        name_ns_instanciated = name0,
        id_osm_ns_instanciated = id_osm0,
        fk_status = id_status0,
        fk_job = id_job0,
        creation_date_ns_instanciated = datetime.now().utcnow()
    ).execute()

def UpdateNsInstanciated(id_osm0,id_status0,id_job0):
    NS_Instanciateds.update(fk_status = id_status0,finish_date_ns_instanciated=datetime.now().utcnow()).where((NS_Instanciateds.id_osm_ns_instanciated == id_osm0)&(NS_Instanciateds.fk_job==id_job0)).execute()
    return "ExecutedUpdate"

def InsertStatusVnfInstanced(name):
    return Status_Vnf_Instanciateds.insert(
        name_osm_status_vnf_instanciated = name,
        creation_date_status_vnf_instanciated = datetime.now().utcnow()
    ).execute()  

def InsertVnfInstanciated(id_osm0,name_osm,id_fk_cloud,id_status,id_ns_instanciated):
    return Vnf_Instanciateds.insert(
        id_osm_vnf_instanciated = id_osm0,
        name_osm_vnf_instanciated = name_osm,
        fk_cloud = id_fk_cloud,
        fk_status = id_status,
        fk_ns_instanciated = id_ns_instanciated,
        creation_date_vnf_instanciated = datetime.now().utcnow()
    ).execute()

def SelectVnfInstanciated(cod):
    return (Vnf_Instanciateds.select()
    .join(Status_Vnf_Instanciateds)
    .where((Vnf_Instanciateds.id_osm_vnf_instanciated==cod)&(NS_Instanciateds.fk_status==Status_NS_Instanciateds.id_status_vnf_instanciated)).dicts().get())

def SelectNsInstanciated(cod):
    return (NS_Instanciateds.select()
    .join(Status_NS_Instanciateds)
    .where((NS_Instanciateds.id_osm_ns_instanciated==cod)&(Vnf_Instanciateds.fk_status==Status_Vnf_Instanciateds.id_status)).dicts().get())

def SelectTests():
    result = (Tests.select(
        Tests.id_tests,
        Tests.start_date_test,
        Tests.finish_date_test,
        Tests.description,
        Tests_Methods.id_tests_methods,
        Tests_Methods.start_date_test_methods,
        Tests_Methods.finish_date_test_methods,
        Tests_Methods.fk_tests,
        Tests_Methods.fk_methods,
        Methods.id_methods,
        Methods.name_methods,
        #fn.AVG(Tests.finish_date_test-Tests.start_date_test).alias('diftimeTest'),
        #fn.AVG(Tests_Methods.finish_date_test_methods-Tests_Methods.start_date_test_methods).alias('diftimeMethod')
    )
    .join(Tests_Methods)
    .join(Methods)
    #.group_by(Tests.id_tests,Methods.id_methods)
    .dicts())
    print(result)
    df = pd.DataFrame(result)
    #df['start_date_test']=df['start_date_test'].astype(float)
    #df['finish_date_test']=df['finish_date_test'].astype(float)
    #df['diftimeTest']=df['finish_date_test']-df['start_date_test']

    #df['start_date_test_methods']=df['start_date_test_methods'].astype(float)
    #df['finish_date_test_methods']=df['finish_date_test_methods'].astype(float)
    #df['diftimeMethod']=df['finish_date_test_methods']-df['start_date_test_methods']

    #print(df.groupby(['id_methods','name_methods']).mean())
    #df2=df.groupby(['id_methods']).mean()

    #print(df['start_date_test'].sum())
    #print(df)
    #print(df2)
    df.to_csv("coleta2/teste.csv", index=False)
    #df2.to_excel("coleta2teste2.xlsx", index=False)
    return 1

def SelectNsjoinVNFInstanciated(cod):
    return (Jobs.select(
                                    Jobs.id_job,
                                    Jobs.fk_user,
                                    NS_Instanciateds.name_ns_instanciated,
                                    NS_Instanciateds.id_osm_ns_instanciated,
                                    NS_Instanciateds.creation_date_ns_instanciated,
                                    NS_Instanciateds.fk_status,
                                    #Status_NS_Instanciateds.name_osm_status_ns_instanciated,
                                    Vnf_Instanciateds.id_osm_vnf_instanciated,
                                    Vnf_Instanciateds.name_osm_vnf_instanciated,
                                    Vnf_Instanciateds.creation_date_vnf_instanciated,
                                    Vnf_Instanciateds.fk_status,
                                    Vnf_Instanciateds.fk_cloud,
                                    Clouds.name,
                                    Clouds.id_cloud,
                                    Clouds.external_ip
                                    #Status_NS_Instanciateds.name_osm_status_ns_instanciated
                                    )
    .join(NS_Instanciateds)
    .join(Vnf_Instanciateds)  
    #.join(Status_Vnf_Instanciateds) 
    #.join(Status_NS_Instanciateds)
    .join(Clouds)                            
    .dicts())

def updateCostJobVnfCloud(id_jobs_vnf_cloud0, cost_vnf):
    Jobs_Vnfs_Clouds.update(cost = cost_vnf).where(Jobs_Vnfs_Clouds.id_jobs_vnf_cloud==id_jobs_vnf_cloud0).execute()
    return "ExecutedUpdate"

def SelectIdVnf_JobVnfCloud(cod):
    Jobs_Vnfs=Jobs_Vnfs_Clouds.select(Jobs_Vnfs_Clouds.id_vnf).where(Jobs_Vnfs_Clouds.id_jobs_vnf_cloud==cod)
    for row in Jobs_Vnfs:
        return str(row.id_vnf)
    return "-1"

def SelectIdCloud_JobVnfCloud(cod):
    Jobs_Vnfs=Jobs_Vnfs_Clouds.select(Jobs_Vnfs_Clouds.id_cloud).where(Jobs_Vnfs_Clouds.id_jobs_vnf_cloud==cod)
    for row in Jobs_Vnfs:
        return str(row.id_cloud)
    return "-1"

def getVnfStatusDegradation(id_job_vnf):
    THRESHOLD=Jobs_Vnfs_Clouds.select(Jobs_Vnfs_Clouds.degradation_threshold_jobs_vnfs_clouds).where(Jobs_Vnfs_Clouds.id_jobs_vnf_cloud==id_job_vnf)
    THRESHOLD2=0
    VALUE2=0
    
    for row in THRESHOLD:
        THRESHOLD2=row.degradation_threshold_jobs_vnfs_clouds
    
    VALUE=Jobs_Vnfs_Clouds.select(Jobs_Vnfs_Clouds.degradation_monitoring_value_now_jobs_vnfs_clouds).where(Jobs_Vnfs_Clouds.id_jobs_vnf_cloud==id_job_vnf) 
    for row2 in VALUE:
        VALUE2=row2.degradation_monitoring_value_now_jobs_vnfs_clouds

    print(" value")
    print (VALUE2)
    print (" mais detalhes")
    print(THRESHOLD2)
    if VALUE2 > THRESHOLD2:
        print (" esta degradado ")
        return 1
    else:
        print (" nao esta degradado ")
        return 0

def InsertCloud(name0, ip0, external_ip0,cod_degradation_cloud_type,threshold_value,vim_id_osm0):
    TestCloud=Clouds.get_or_none(Clouds.name==name0)
    if TestCloud is None:
        return Clouds.insert(
            name=name0,
            ip=ip0,
            external_ip=external_ip0,
            fk_degradation_cloud_type = cod_degradation_cloud_type,
            threshold_degradation = threshold_value,
            vim_id_osm = vim_id_osm0,
            creation_date=datetime.now().utcnow()
        ).execute()
    else:
        return -1

def GetIdCloud(name_cloud):
    cloud=Clouds.select(Clouds.id_cloud).where(Clouds.name==name_cloud)
    for row in cloud:
        return str(row.id_cloud)
    return "-1"

def GetIdCloudbyvimidosm(vim_id_osm0):
    cloud=Clouds.select(Clouds.id_cloud).where(Clouds.vim_id_osm==vim_id_osm0)
    for row in cloud:
        return str(row.id_cloud)
    return "-1"

def insertMetric(name_metric):
    TestMetric=Metrics.get_or_none(Metrics.name==name_metric)
    if TestMetric is None:
        return Metrics.insert(
            name = name_metric,
            creation_date = datetime.now().utcnow()
        ).execute()
    else:
        return GetIdMetric(name_metric)

def insertMetricCloud(fk_cloud0, fk_metric0):
    Metrics_Clouds.insert(
        fk_cloud = fk_cloud0,
        fk_metric = fk_metric0,
        creation_date = datetime.now().utcnow()
    ).execute()

def GetIdMetric(NAME_METRIC):
    #teste = Metrics.select(Metrics.id_metric).where((Metrics.name==NAME_METRIC)&(Metrics.fk_cloud==COD_CLOUD))
    metrics = Metrics.select(Metrics.id_metric).where(Metrics.name==NAME_METRIC)
    for row in metrics:
            return str(row.id_metric)
    return "-1"

def InsertVnf(name_vnf):
    TestVnf=Vnfs.get_or_none(Vnfs.name==name_vnf)
    if TestVnf is None:
        Vnfs.insert(
            name=name_vnf,
            creation_date=datetime.now().utcnow()
        ).execute()
    else:
        -1

def GetIdVNF(NAME_VNF):
    #teste = Metrics.select(Metrics.id_metric).where((Metrics.name==NAME_METRIC)&(Metrics.fk_cloud==COD_CLOUD))
    vnfs = Vnfs.select(Vnfs.id_vnf).where(Vnfs.name==NAME_VNF)
    for row in vnfs:
            return str(row.id_vnf)
    return "-1"

def GetNameVNF(COD):
    VNFGet=Vnfs.select(Vnfs.name).where(Vnfs.id_vnf==COD)
    for row in VNFGet:
        return str(row.name)
    return "-1"

def insertMetricsVnf(metric_data, weight0,  cod_metric,cod_job_vnf_cloud):
    return Metrics_Vnfs.insert(
        metric_value = metric_data,
        weight = weight0,
        #fk_vnf = cod_vnf,
        fk_metric = cod_metric,
        fk_job_vnf_cloud = cod_job_vnf_cloud,
        creation_date = datetime.now().utcnow()
    ).execute()

def GetMetricsVnf(metric_vnf_id):
    print("metric vnf id:")
    print(metric_vnf_id)
    TestMetricsVnf=Metrics_Vnfs.get_or_none(Metrics_Vnfs.id_metric_vnf==metric_vnf_id)
    if TestMetricsVnf is None:
        return -1
    else:
        metricsvnfs = Metrics_Vnfs.select(Metrics_Vnfs.metric_value,Metrics_Vnfs.weight).where(Metrics_Vnfs.id_metric_vnf==metric_vnf_id)
        for row in metricsvnfs:
            if row.metric_value > str(0):
                return str(row.metric_value+":"+row.weight)
            else:
                return str("0:"+row.weight)

def InsertStatusJobs(nameStatus):
    Status_Jobs.insert(
        name_status_jobs = nameStatus,
        creation_date_status_jobs = datetime.now().utcnow()
    ).execute()

def InsertDegradationsCloudsTypes(name_type):
    Degradations_Clouds_Types.insert(
        name = name_type,
        creation_date = datetime.now().utcnow()
    ).execute()

def InsertDegradations_Clouds(id_fk_cloud, status_degradation_cloud, current_value_degradation0):
    Degradations_Clouds.insert(
        status_degradation_cloud = status_degradation_cloud, #1 if degration start, and 0 if stoped
        current_value_degradation = current_value_degradation0,
        fk_cloud = id_fk_cloud,
        creation_date = datetime.now().utcnow()
    ).execute()

def SelectStatusDegradationCloud(CLOUD_ID):
    CloudDegra=Degradations_Clouds.select(Degradations_Clouds.status_degradation_cloud).where((Degradations_Clouds.id_cloud==CLOUD_ID)&(Degradations_Clouds.status_degradation_cloud==1))
    for row in CloudDegra:
        return str(row.status_degradation_cloud)
    return "0"    

def FirstLoadBD():
    print("Iniciando carga BD.")
    #PreLoadDefault
    InsertMethods("insertJob_cl1()")
    InsertMethods("insertJob_cl2()")
    InsertMethods("userLatency_cl1()")
    InsertMethods("userLatency_cl2()")
    InsertMethods("getLastMeasureClouds_cl1()")
    InsertMethods("getLastMeasureClouds_cl2()")
    InsertMethods("insertMetric_cl1()")
    InsertMethods("insertMetric_cl2()")
    InsertMethods("insertMetricCloud_cl1()")
    InsertMethods("insertMetricCloud_cl2()")
    InsertMethods("insertJobVnfCloud_cl1()")
    InsertMethods("insertJobVnfCloud_cl2()")
    InsertMethods("insertMetricsVnf_cl1()")
    InsertMethods("insertMetricsVnf_cl2()")
    InsertMethods("getMetricsVnfApplyWeight_cl1()")
    InsertMethods("getMetricsVnfApplyWeight_cl2()")
    InsertMethods("updateCostJobVnfCloud_cl1()")
    InsertMethods("updateCostJobVnfCloud_cl2()")
    InsertMethods("getVnfStatusDegradation_cl1()")
    InsertMethods("getVnfStatusDegradation_cl2()")
    #InsertMethods("SetProcessModel()")
    InsertMethods("configVNFsCostsOSM_cl1()")
    InsertMethods("configVNFsCostsOSM_cl2()")
    InsertMethods("createNSInstanceOSM_cl1()")
    InsertMethods("createNSInstanceOSM_cl2()")
    InsertActionsTestsTypes("Instanciação de NS.")
    InsertActionsTestsTypes("Alteração do custo do link, considerando latência e jitter entre nuvens.")
    InsertActionsTestsTypes("Alteração do custo das VNFDs de acordo com a latência para o usuário final e percentual de uso de CPU da nuvem.")
    InsertActionsTestsTypes("Aumento dos custos de todos os VNFDs da nuvem após degradação do uso de CPU.")
    InsertDegradationVnfType("CPU")
    InsertDegradationVnfType("Memoria")
    InsertDegradationsCloudsTypes("CPU")
    InsertDegradationsCloudsTypes("Memoria")
    InsertCloud("Serra","10.50.0.159","200.137.75.160",1,90,"9f104eee-5470-4e23-a8dd-3f64a53aa547")
    InsertCloud("Aracruz","172.16.112.60","200.137.82.21",2,91,"59ea6654-25f4-4196-a362-9745498721e1")
    InsertDegradations_Clouds(1,1,98)
    InsertDataTestsTypes("CPU")
    InsertDataTestsTypes("Memoria")
    InsertDataTestsTypes("NVNF")
    InsertDataTestsTypes("Latencia_to_N2")
    InsertDataTestsTypes("Jitter_to_N2")
    InsertDataTestsTypes("Latencia_to_User_Test")
    InsertVnf("VNFA")
    InsertVnf("VNFB")
    InsertStatusJobs("Started")
    InsertStatusJobs("Finished")
    InsertStatusJobs("Running")
    InsertUser("Jose Carlos","jcarlos","abc")
    InsertUser("Amarildo de Jesus","ajesus","abcd")
    #UsingSystem
    #Insert Job with User IP, name NS, cod administrator user and cod job status
    #job_cod_uuid=uuid.uuid4()
    #print (str(job_cod_uuid))
    ##########InsertJob("10.0.19.148","teste_mestrado",1,1)
    #Insert Jo
    ############JOBVNFCLOUD=InsertJobVnfCloud(20,1,1,1)
    ###########print (JOBVNFCLOUD)
    insertMetric("Lat_to_8.8.8.8")  ###proximos a comentar, verificar
    insertMetric("Lat_to_1.1.1.1")   #proximos a comentar, verificar 
    insertMetricCloud(1,1)
    ###########InsertMetricsVnf(20,8,1,JOBVNFCLOUD)
    InsertStatusNsInstanced('BUILDING')
    InsertStatusNsInstanced('READY')
    InsertStatusNsInstanced('DELETED')
    InsertStatusVnfInstanced('INSTANTIATED')
    InsertStatusVnfInstanced('DELETED')

def main():
    #File in Clouds
    app = Flask(__name__)


    #Load BD after to create BD
    @app.route('/firstloadbd/',methods=['POST'])
    def cargabd():
        FirstLoadBD()
        return "LoadedBase"

    @app.route('/copydatatests/',methods=['GET'])
    def copydatatest():
        now=datetime.now().utcnow()
        intervalo=240
        delta = timedelta(seconds=intervalo)
        time_past=now-delta
        #START = "2021-08-01 13:30:33+00:00"
        #STOP = "2021-08-01 13:35:36+00:00"
        START=time_past
        STOP=now
        GRANULARITY=60.0
        #metrics_test=json.loads(cloud1_gnocchi.get_last_measure_Data_Test("NVNF",cloud1_resource_id,None,GRANULARITY,START,STOP))
        #get_data=cloud1_gnocchi.get_last_measure_Date("NVNF",cloud1_resource_id,None,GRANULARITY,START,STOP)
        #print(get_data)
        #if get_data == -1:
        #    return "ok" 
        #metrics_test=json.loads(get_data)
        #print(metrics_test)
        
        dados=[{'date_data_tests':'21' ,'granularity_data_tests': '60.0', 'value_data_tests':'1.0',  'fk_tests':1, 'fk_data_tests_types':1,  'fk_cloud':1}]
        #print(type(dados))
        #dados2=[{'name_data_tests':'o44ii'},{'name_data_tests':'oii33332'}   ]
        #Data_Tests_Types.insert_many(dados2, fields=['name_data_tests']).execute()

        Data_Tests.insert_many(dados, fields=[Data_Tests.date_data_tests, Data_Tests.granularity_data_tests, Data_Tests.value_data_tests, Data_Tests.fk_tests, Data_Tests.fk_data_tests_types, Data_Tests.fk_cloud]).execute()
        
        #Data_Tests.insert_many(metrics_test, fields=[Data_Tests.date_data_tests, Data_Tests.granularity_data_tests, Data_Tests.value_data_tests, Data_Tests.fk_tests, Data_Tests.fk_data_tests_types, Data_Tests.fk_cloud]).execute()
        return "ok"

    app.run("0.0.0.0", '3332',debug=True)

if __name__ == "__main__":
    main()