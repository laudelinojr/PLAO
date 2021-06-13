import subprocess

subprocess.call(['python3', 'docker_pla.py', 'vnf_price_list'])
nomearquivo4=PATH_LOG+'COPY_CONFIG_OSM_history2.txt' #write data in file
with open(nomearquivo4, 'a') as arquivo:
    print("alterado arquivo")
    arquivo.write(DATEHOURS + '- Alterado e copiado arquivo '+FILE_VNF_PRICE + ' para o container PLA.' +'\n')
arquivo.close()
print("vai copiar arquivo SearchChangeVNFDPrice ")