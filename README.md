# PLAO
iperf
python3 utils/iperf.py SERVER  127.0.0.1
python3 utils/iperf.py CLIENT 127.0.0.1


python3 PLAO_client.py 127.0.0.1 openstack1 10.159.205.6
python3 PLAO_client.py 127.0.0.1 openstack2 10.159.205.12

___Terminal_1
ssh 10.159.205.10

cd /opt/PLAO
git pull
python3 PLAO.py


___Terminal_2
ssh 10.159.205.10
cd /opt/PLAO/log
while true; do  for i in `ls`; do tail -1 $i ; sleep 1 ;done ; done

___Terminal_3
cd /opt/PLAO/osm
while true; do  ls -lt  ; sleep 30; done

___Terminal_4
osm  ns-create --nsd_name teste_artigo  --ns_name test1ArtigoPLA9 --vim_account openstack1 --config '{placement-engine: PLA, wim_account: False }'

___Terminal_5
ssh root@10.159.205.6
cd /opt/PLAO
python3 PLAO_client.py 10.159.205.10 openstack1 10.159.205.6


Para simular Latencia nos openstacks
tc qdisc add dev eth0 root netem delay 100ms
tc qdisc del dev eth0 root


#Iniciando da máquina OSM
#1 - Logs em /op/PLAO/log/
#2 - Todos os valores de jitter e latencia são convertidos para inteiro, pois este e o tipo que o script de placement do OSM espera
#3 - Se nvCPU (percentual de vcpu disponiveis na cloud) for maior que 90%, price de todos os VNFD de todos os usuários sao alterados para a respectiva cloud
cd /opt/PLAO
git pull
rm -rf /opt/PLAO/log/*
python3 PLAO.py &
echo user_vnfd_latencia.txt_bkp > user_vnfd_latencia.txt
sleep 10
echo > user_vnfd_latencia.txt
ssh root@10.159.205.6 cd /opt/PLAO; git pull ; python3 PLAO_client.py 10.159.205.10 openstack1 10.159.205.6 &
ssh root@10.159.205.12 cd /opt/PLAO; git pull ; python3 PLAO_client.py 10.159.205.10 openstack2 10.159.205.12 &
cd /opt/PLAO/log/ ; while true; do  for i in `ls`; do tail -1 $i ; sleep 1 ;done ; done


