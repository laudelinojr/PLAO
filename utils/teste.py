import time

def UsersAdd():
    while True:
        nomearquivo1='user_vnfd_latencia.txt'
        arquivo = open(nomearquivo1,'r')
        linha = arquivo.readline()
        for linha in arquivo:
            valores=linha.split('#')

            USERIP = valores[0]
            LATENCY = valores[1]
            COMMAND = valores[2]        
            VNF = valores[3]
            users.update({'0':{'USERIP': USERIP,'LATENCY': LATENCY,'VNF': VNF,'COMMAND': COMMAND}})
            # users.update({(str(len(users)+1)):{'USERIP': USERIP,'LATENCY': LATENCY,'VNF': VNF,'COMMAND': COMMAND}})
        arquivo.close()
        print(len(users))
        print(users.get('1').get('USERIP'))
        time.sleep(1)


    #us.get(str(1)).get('VIMURL')


def UsersManager():
    while True:
        time.sleep(5)
  
        for i in (users):
            print(users.get(i))
            

users = {}
UsersAdd()
#UsersManager()