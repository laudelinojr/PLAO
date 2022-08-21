#!/bin/bash

#chmod 755 /opt/PLAO/linux/crontab_plao_server.sh
cd /opt/PLAO
git pull

if [ `ps ax | grep PLAO.py | grep -v grep | wc -l` ==  0 ] ; then
 cd /opt/PLAO/
 python3 PLAO2.py
fi