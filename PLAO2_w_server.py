#File in Clouds

from PLAO_client2_w_routes import app
from PLAO_client2 import *

#servers = Servers()
IPServerLocal="127.0.0.1"

#Alterar para IP do servidor do PLAO
app.run(IPServerLocal, '3332')