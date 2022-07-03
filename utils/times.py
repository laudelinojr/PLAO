from datetime import datetime


def UnixTimeStamp():
    print (datetime.now().utcnow())
    #print (datetime.now().utcnow()).split('.')[0]
    print(datetime.timestamp(datetime.now()))
    return "ok"

print (UnixTimeStamp())