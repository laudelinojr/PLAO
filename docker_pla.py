import os
import sys

FILE_VNF_PRICE="/opt/PLAO/osm/vnf_price_list.yaml"
FILE_PIL_PRICE="/opt/PLAO/osm/pil_price_list.yaml"

#os.system('docker cp '+FILE_VNF_PRICE+' '+'$(docker ps -qf name=osm_pla):/placement/')
#os.system('docker cp '+FILE_PIL_PRICE+' '+'$(docker ps -qf name=osm_pla):/placement/')

if sys.argv[1] == 'vnf_price_list.yaml':
    os.system('docker cp '+FILE_VNF_PRICE+' '+'$(docker ps -qf name=osm_pla):/placement/')

if sys.argv[1] == 'pil_price_list':
    os.system('docker cp '+FILE_VNF_PRICE+' '+'$(docker ps -qf name=osm_pla):/placement/')