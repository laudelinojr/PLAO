from datetime import datetime


def UnixTimeStamp():
    return datetime.timestamp(datetime.now())

print (UnixTimeStamp())