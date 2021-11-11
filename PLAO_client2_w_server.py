#File in Clouds

from PLAO_client2_w_routes import app
from PLAO_client2 import *
from PLAO2 import *

servers = Servers()
IPServerLocal=servers.getSearchIPLocalServer()

#Alterar para IP do servidor do PLAO
app.run(IPServerLocal, '3333',debug=True)