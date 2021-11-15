import requests
from PLAO_client2 import *

# The payload is the user ip address.
payload = {"ipuser" : "10.0.19.148"}

# Request to cloud. Is necessary in http URL the cloud ip address
a = requests.request(
    method="POST", url='http://10.159.205.10:3332/start/', json=payload)

print(a.text)

# Request to cloud. Is necessary in http URL the cloud ip address
a = requests.request(
    method="POST", url='http://10.159.205.10:3332/plaoserver/', json=payload)

print(a.text)