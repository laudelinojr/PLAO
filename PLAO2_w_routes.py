#File in Clouds

from flask import Flask, request
import requests
#from PLAO2 import *

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
        payload = request_data['ipuser']
        controle=0
        #payload = {"ipuser" : "10.0.19.148"}
        print("Inicio Teste na nuvem 1")
        # Request to cloud. Is necessary in http URL the cloud ip address
        a = requests.request(
            method="POST", url='http://'+nuvem1+':3333/plao/', json=payload)
        print(a.text)
        print("Fim Teste na nuvem 1")
        print("Inicio Teste na nuvem 2")
        a = requests.request(
            method="POST", url='http://'+nuvem2+':3333/plao/', json=payload)
        print(a.text)
        print("Fim Teste na nuvem 2")
        return "okplaoserver"