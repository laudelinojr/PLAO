import os
import sys

FILE_VNF_PRICE="/opt/PLAO/osm/vnf_price_list.yaml"
FILE_PIL_PRICE="/opt/PLAO/osm/pil_price_list.yaml"

#os.system('docker cp '+FILE_VNF_PRICE+' '+'$(docker ps -qf name=osm_pla):/placement/')
#os.system('docker cp '+FILE_PIL_PRICE+' '+'$(docker ps -qf name=osm_pla):/placement/')

if sys.argv[1] == '1':
    os.system('docker cp '+FILE_VNF_PRICE+' '+'$(docker ps -qf name=osm_pla):/placement/')

if sys.argv[1] == '2':
    os.system('docker cp '+FILE_VNF_PRICE+' '+'$(docker ps -qf name=osm_pla):/placement/')

    nomearquivo6=PATH_LOG+'CONFIG_OSM_history.txt' #write data in file
    with open(nomearquivo6, 'a') as arquivo:
        arquivo.write(DATEHOURS() + ' - Changed and copied file '+ FILE_VNF_PRICE + ' to container PLA. Add values in All prices to Cloud: '+VIM_URL+ '.' +'\n')