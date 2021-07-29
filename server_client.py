#File in Clouds

from routes_client import app
from PLAO_client2 import *

servers = Servers()
IPServerLocal=servers.getSearchIPLocalServer()

#Alterar para IP do servidor do PLAO
app.run(IPServerLocal, '3333')