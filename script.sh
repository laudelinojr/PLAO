#!/bin/bash

if [ $1 == "vnf_price_list.yaml" ];
then
#echo 1 #`/sbin/runuser -l mano -c  'docker cp /opt/PLAO/osm/vnf_price_list.yaml $(docker ps -qf name=osm_pla):/placement/'`
 docker cp /opt/PLAO/osm/vnf_price_list.yaml $(docker ps -qf name=osm_pla):/placement/
 echo date "- Arquivo vnf_price_list.yaml atualizado para o  placement OSM." >> /opt/PLAO/log/copy_to_docker.txt
fi

if [ $1 == "pil_price_list.yaml" ];
then
#echo 2 # `/sbin/runuser -l mano -c  'docker cp /opt/PLAO/osm/pill_price_list.yaml $(docker ps -qf name=osm_pla):/placement/'`
 docker cp /opt/PLAO/osm/pil_price_list.yaml $(docker ps -qf name=osm_pla):/placement/
 echo date "- Arquivo pil_price_list.yaml atualizado para o  placement OSM." >> /opt/PLAO/log/copy_to_docker.txt
fi