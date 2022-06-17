import requests
from urls import *
#from env import *

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
    print("agora vai")
    print(type(token))
    str(token)
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
    print("testes")
    response = requests.request("GET", url, headers=headers, data=payload,verify=False)
    print (response.json())
    return response.json()

token = osm_create_token()
print (token)
token = token['id']
print (type(token))
osm_get_vim_accounts(token)