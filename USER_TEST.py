import os
import sys

IP_USER='10.0.19.148'
COMMAND=''
VMFD='VNFA,VNFB'
nomearquivo='user_vnfd_latencia.txt' #write data in file

if sys.argv[1] == '1':
    #Instanciate without constraint
    COMMAND='osm ns-create --nsd_name teste_artigo  --ns_name test1ArtigoPLA --vim_account openstack1 --config '{placement-engine: PLA, wim_account: False }''
if sys.argv[1] == '2':
    #Instanciate with constraint latency and jitter constraint
    COMMAND='osm ns-create --nsd_name teste_artigo  --ns_name test2ArtigoPLA --vim_account openstack1 --config '{placement-engine: PLA, placement-constraints: {vld-constraints: [{id: ns_vl_2mlm, link-constraints: {latency: 2, jitter: 20}}], wim_account: False }''
if sys.argv[1] == '3':
    #Instanciate with constraint with just latency constraint
    COMMAND='osm ns-create --nsd_name teste_artigo  --ns_name test2ArtigoPLA --vim_account openstack1 --config '{placement-engine: PLA, placement-constraints: {vld-constraints: [{id: ns_vl_2mlm, link-constraints: {latency: 2}}]}, wim_account: False}''
if sys.argv[1] == '4':
    #Instanciate with constraint with just jitter constraint
    COMMAND='osm ns-create --nsd_name teste_artigo  --ns_name test2ArtigoPLA --vim_account openstack1 --config '{placement-engine: PLA, placement-constraints: {vld-constraints: [{id: ns_vl_2mlm, link-constraints: {jitter: 2}}]}, wim_account: False }''

if len(COMMAND)>=1:
    with open(nomearquivo, 'a') as arquivo:
        arquivo.write(IP_USER+'#'+COMMAND+'#'+VMFD+'#')
else:
    "NS sendo criada sem a utilizacao de latencia do usuario"
    if sys.argv[1] == '1a':
        #Instanciate without constraint
        COMMAND='osm ns-create --nsd_name teste_artigo  --ns_name test1ArtigoPLA --vim_account openstack1 --config '{placement-engine: PLA, wim_account: False }''
    if sys.argv[1] == '2a':
        #Instanciate with constraint latency and jitter constraint
        COMMAND='osm ns-create --nsd_name teste_artigo  --ns_name test2ArtigoPLA --vim_account openstack1 --config '{placement-engine: PLA, placement-constraints: {vld-constraints: [{id: ns_vl_2mlm, link-constraints: {latency: 2, jitter: 20}}], wim_account: False }''
    if sys.argv[1] == '3a':
        #Instanciate with constraint with just latency constraint
        COMMAND='osm ns-create --nsd_name teste_artigo  --ns_name test2ArtigoPLA --vim_account openstack1 --config '{placement-engine: PLA, placement-constraints: {vld-constraints: [{id: ns_vl_2mlm, link-constraints: {latency: 2}}]}, wim_account: False}''
    if sys.argv[1] == '4a':
        #Instanciate with constraint with just jitter constraint
        COMMAND='osm ns-create --nsd_name teste_artigo  --ns_name test2ArtigoPLA --vim_account openstack1 --config '{placement-engine: PLA, placement-constraints: {vld-constraints: [{id: ns_vl_2mlm, link-constraints: {jitter: 2}}]}, wim_account: False }''

    with open(nomearquivo, 'a') as arquivo:
        arquivo.write(COMMAND)
