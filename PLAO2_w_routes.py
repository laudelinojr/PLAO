#File in Clouds

from flask import Flask, request
from PLAO_client2 import *

app = Flask(__name__)

@app.route("/plaoserver/", methods=['POST', 'GET', 'DELETE'])
def latencia_user_plao():
    if request.method == "POST":
        request_data = request.get_json()
        ip_user = request_data['ip']
        print("Teste Servidor")
        return "ok"