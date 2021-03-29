import subprocess
import time


def ExecuteCommand(exec_command):
    try:
        ret = subprocess.run(exec_command, universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
        if debug_file == 1:
            print("DEBUG ON")
            print("CMD - " + exec_command)
            print("RETURN - \n" + ret.stdout)
        return ret.returncode
    except:
        print('FAIL IN COMMAND EXECUTE')
        print("CMD - " + exec_command)
        print("ERROR - " + ret)
        return ret.returncode


COMANDO1='cd /opt/PLAO ; git pull; rm -rf logs/*; python3 PLAO.py &'
COMANDO2='ssh 10.159.205.6 cd /opt/PLAO; git pull; python3 PLAO_client.py 10.159.205.10 openstack1 10.159.205.6 &'
COMANDO3='ssh 10.159.205.12 cd /opt/PLAO; git pull; python3 PLAO_client.py 10.159.205.10 openstack2 10.159.205.12 &'
COMANDO4='python3 USER_TEST.py 1'
COMMANDO=
COMANDO8=''
COMANDO9=''
COMANDO10=''

for i in range(4):
    ExecuteCommand(str('COMANDO'+i))
    time.sleep(2)

