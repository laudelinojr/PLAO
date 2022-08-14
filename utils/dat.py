import datetime
from datetime import datetime, tzinfo,date,timedelta



def DATEHOURS():
    DATEHOUR = datetime.now().utcnow()  #.strftime('%d.%m.%y-%H:%M:%S')  # converte hora para string do cliente
    return DATEHOUR


print(DATEHOURS())

#timestamp = 1545730073
#dt_object = datetime.fromtimestamp(timestamp)
#inverso = datetime.fromordinal(dt_object)
#print("dt_object =", dt_object)
#print("type(dt_object) =", type(dt_object))
#print(inverso)
print ("stop")
stop=1660400692.264529
print(stop)
#now=datetime.now()
stop=datetime.fromtimestamp(stop)
print(stop)
intervalo=60
delta = timedelta(seconds=intervalo)
time_past=stop-delta
#START = "2021-08-01 13:30:33+00:00"
#STOP = "2021-08-01 13:35:36+00:00"
start=time_past
print("oi")
print(start)