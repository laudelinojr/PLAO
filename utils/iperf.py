import platform
import subprocess
import sys

QUANTITY_PCK="5"

STATUS = sys.argv[1] #Address Server OSM IP
if sys.argv[1] == '':
    print ("Invalido: We need the IP OSM Sever.")
    exit()

CLOUDTOIP = sys.argv[2] #Address Server OSM IP
if sys.argv[2] == '':
    print ("Invalido: We need the IP OSM Sever.")
    exit()

DIR_IPERF="C:/Temp/artigo/utils/iperf/"

def GetJitter(CLOUDTOIP,QUANTITY_PCK,STATUS):
    if STATUS == "SERVER":
        iperf = subprocess.run([DIR_IPERF+"iperf3", "-s", "-1", "-D"], )      
        #jitter = iperf.split()[-4]
        #print (jitter)
        #return iperf
    if STATUS == "CLIENT":
        iperf = subprocess.check_output([DIR_IPERF+"iperf3", "-c", CLOUDTOIP,"-u", "-t", QUANTITY_PCK])
        print(iperf)
        jitter = iperf.split()[-11]
        print (jitter)
        return jitter

GetJitter(CLOUDTOIP,QUANTITY_PCK,STATUS)
