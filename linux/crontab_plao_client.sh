#!/bin/bash

#chmod 755 /home/laudelinoas/PLAO/linux/crontab_plao_client.sh
cd /home/laudelinoas/PLAO
git stash
git stash clear
git pull

#if [ `ps ax | grep PLAO_client2.py | grep -v grep | wc -l` ==  0 ] ; then
# cd /home/laudelinoas/PLAO
# python3 PLAO_client2.py
#fi
