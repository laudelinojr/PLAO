#!/bin/bash

#if [$1 -eq "vnf_price_list.yaml"]
#then
# `/sbin/runuser -l mano -c  'docker cp /opt/PLAO/osm/vnf_price_list.yaml $(docker ps -qf name=osm_pla):/placement/'`

#fi

#if [$1 -eq "pill_price_list.yaml"]
#then
# `/sbin/runuser -l mano -c  'docker cp /opt/PLAO/osm/pill_price_list.yaml $(docker ps -qf name=osm_pla):/placement/'`
#fi

docker cp /opt/PLAO/osm/vnf_price_list.yaml $(docker ps -qf name=osm_pla):/placement/
docker cp /opt/PLAO/osm/pil_price_list.yaml $(docker ps -qf name=osm_pla):/placement/

echo date "- copiado arquivos para container placement" >> /opt/PLAO/log/copy_to_docker.txt