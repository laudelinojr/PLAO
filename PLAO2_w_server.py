#File in Clouds

from PLAO2_w_routes import app
from PLAO2 import *

#servers = Servers()
IPServerLocal="10.159.205.10"

#Alterar para IP do servidor PLAO
app.run(IPServerLocal, '3332',debug=True)