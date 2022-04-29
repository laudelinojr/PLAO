import subprocess
import threading
import time
import sys
import os
import platform

debug_file = 1
TARGET= "200.137.82.21"


# To execute commands in Linux
def ExecuteCommand(exec_command):
 try:
  ret = subprocess.run(exec_command, universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
  if debug_file == 1:
   print("DEBUG ON")
   print("CMD - " + exec_command)
   print("RETURN - \n" + ret.stdout)
   print (ret.stdout)
   print (+ret.returncode)
   return ret.returncode
 except:
  print('FAIL IN COMMAND EXECUTE')
  print("CMD - " + exec_command)
  print("ERROR - " + ret)
  return ret.returncode

while True:
    time.sleep(1)
    if platform.system().lower() == "linux":
        if (ExecuteCommand("ps ax | grep 'iperf3 -s -D'  | grep -v grep | wc -l")==0):
            print("executing iperf Daemon loop 1")            
            subprocess.run(["iperf3", "-s", "-D"])
        try:
            print("executing iperf to: "+TARGET)
            iperf2 = subprocess.check_output(["iperf3", "-c", TARGET,"-u", "-t", 5])
        except:
            print ("Error in iperf client")