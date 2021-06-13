import os

nomearquivo7='saida.txt' #write data in file
if(os.path.isfile(nomearquivo7)):
    #if debug == 1: print("O arquivo existe")           
    with open(nomearquivo7, 'r') as arquivo:
        #print("coletando arquivo latencia")
        linha = arquivo.readline()
    #if debug == 1: print("linha trabalhando agora: "+ linha)
        valores=linha.split('|')
        USERIP = valores[0]
        COMMAND = valores[1]        
        VNF = valores[2]           
    #print("vai excluir arquivo")
    #os.remove(nomearquivo7)
    #print("excluiu o arquivo")

print(USERIP)
print(COMMAND)
print(VNF)