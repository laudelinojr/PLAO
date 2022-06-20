import requests
from urls import *
import time
import json
import pandas as pd

def osm_create_token(project_id='admin'):

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    payload = {
        "username": 'admin',
        "password": 'admin',
        "project_id": project_id
    }

    response = requests.request(method="POST", url=url_token_osm, headers=headers,
                                json=payload, verify=False)

    return response.json()



def osm_get_vim_accounts(token):
    # GET /admin/v1/vims Query information about multiple VIMs
    method_osm = "/admin/v1/vims/"
    url = url_osm+method_osm
    url=str(url)
    payload = {}
    # token = token.replace('\r','')

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "Authorization": 'Bearer '+str(token)
    }
    response = requests.request("GET", url, headers=headers, data=payload,verify=False)
    return response.json()

def osm_get_ns(token):
    # GET /admin/v1/vims Query information about multiple VIMs
    method_osm = "/nsd/v1/ns_descriptors/"
    url = url_osm+method_osm
    url=str(url)
    payload = {}
    # token = token.replace('\r','')

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "Authorization": 'Bearer '+str(token)
    }
    response = requests.request("GET", url, headers=headers, data=payload,verify=False)
    return response.json()

def geturls(url):
        
    urls = { 'url_projects'  : '/osm/admin/v1/projects',  
    'url_users' : '/osm/admin/v1/users',
    'url_vim' : '/osm/admin/v1/vims' ,
    'url_vnf' : '/osm/vnfpkgm/v1/vnf_packages',
    'url_associate' : '/osm/admin/v1/users/admin',
    'url_token_osm' : '/osm/admin/v1/tokens',
    'url_ns_descriptor' : '/osm/nsd/v1/ns_descriptors_content',
    'url_vim_accounts' : '/osm/admin/v1/vim_accounts',
    'url_ns_instance' : '/osm/nslcm/v1/ns_instances',
    'url_osm' : '/osm',
    'ns_descriptors' : '/nsd/v1/ns_descriptors'
    }
    return "https://"+IP+":"+PORT+urls.get(url)

def check_token_valid(token):
    #Compara unixtimestemp e se for o caso gera outro invocando o osm_create_token
    actual=1655499441.8314078 #time.time()
    to_expire=1655498598.1036203 #token['expires']
    if (to_expire < actual):
        print(to_expire)
        print(actual)
        print("renovando token")
        osm_create_token()

token = osm_create_token()
#check_token_valid(token)
print(token)
token2 = token['id']
#token3 = token['expires']
#check_token_valid(token)



retorno=osm_get_ns(token2)

#retorno.get('vld')
print(retorno)
for i in (retorno):
    ID=i['id']
    VNFDLIST=[]
    VNFDLIST2={}
    VLD=(i['vld'])
    for i in VLD:
        VNFD=(i['vnfd-connection-point-ref'])
        for i in VNFD:
            NEWVNFD=i['vnfd-id-ref']
            if (not VNFDLIST.__contains__(NEWVNFD)):
                VNFDLIST.append(i['vnfd-id-ref'])

    VNFDLIST2.update({ID:VNFDLIST})
    df5=json.dumps(VNFDLIST2, indent=2)
    print(df5)



#VIM_ACCOUNTS=osm_get_vim_accounts(token2)

#print (token3)
#print(token)

#print(geturls('url_projects' ))

#for i in (1,len(VIM_ACCOUNTS)-1):
    #print (VIM_ACCOUNTS[i]['_id'])
    #print (VIM_ACCOUNTS[i]['name'])
    #print (VIM_ACCOUNTS[i]['vim_type'])
    #print (VIM_ACCOUNTS[i]['vim_url'])

    #print (time.time())
