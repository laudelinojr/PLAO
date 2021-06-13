import requests
import json
import yaml

url = "https://10.159.205.10:9999/osm/admin/v1/tokens"

headers = {
'Content-Type': 'application/json'
}
payload = {
    "username": 'admin',
    "password": 'admin',
    "project_id": 'admin'
}

response = requests.request("POST", url, headers=headers, json=payload,verify=False)
print(response.text)

a=response.text
#b=json.loads(a)  #B eh um grande dicionario
#c=(len(b))
#print(b)
#A=open(a, )
B=yaml.full_load(a)


print(B['_id'])
