import requests
from PLAO_client2 import *

payload = {"ip" : "10.159.205.11"}

a = requests.request(
    method="POST", url='http://192.168.56.1:3333/plao/', json=payload)

print(a.text)