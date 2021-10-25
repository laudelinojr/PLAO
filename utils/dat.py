import datetime
from datetime import datetime, tzinfo



def DATEHOURS():
    DATEHOUR = datetime.now()  #.strftime('%d.%m.%y-%H:%M:%S')  # converte hora para string do cliente
    return DATEHOUR


print(DATEHOURS())

#timestamp = 1545730073
#dt_object = datetime.fromtimestamp(timestamp)
#inverso = datetime.fromordinal(dt_object)
#print("dt_object =", dt_object)
#print("type(dt_object) =", type(dt_object))
#print(inverso)