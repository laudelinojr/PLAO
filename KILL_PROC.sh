#!/bin/bash

$1

if ($1 -eq "cliente"); then
    comando=`ps -ef | grep "PLAO_client" | awk '{print $2}'`
fi
if ($1 -eq "server"); then
    comando=`ps -ef | grep "PLAO_client" | awk '{print $2}'`
fi

for pid in $comando
do
    kill -9 $pid
done
