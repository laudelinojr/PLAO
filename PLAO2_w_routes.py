#File in Clouds

from flask import Flask, request
import requests
#from PLAO2 import *

app = Flask(__name__)

@app.route('/start/',methods=['POST'])
def start():
    if request.method == "POST":
        payload = {"ipuser" : "10.0.19.148"}
        a = requests.request(
            method="POST", url='http://10.159.205.8:3333/start/', json=payload)
        print(a.text)
        return "okstart"
@app.route("/plaoserver/", methods=['POST', 'GET', 'DELETE'])
def latencia_user_plao():
    if request.method == "POST":
        request_data = request.get_json()
        ipuser = request_data['ipuser']
        controle=0
        print (ipuser)
        print("Teste na nuvem 1")
            #from PLAO_client2 import *
            # The payload is the user ip address.
        nuvem1="10.159.205.8"
        nuvem2="10.159.205.8"
        payload = {"ipuser" : "10.0.19.148"}
        print (payload)
        # Request to cloud. Is necessary in http URL the cloud ip address
        a = requests.request(
            method="POST", url='http://10.159.205.8:3333/plao/', json=payload)
        print(a.text)
        print("Fim Teste na nuvem 1")

        print("Teste na nuvem 2")

        print("Fim Teste na nuvem 2")
        return "ok"