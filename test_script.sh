#!/bin/bash
echo "INICIO CENARIO 1"
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST uplatencytouser 200.137.75.159 200.137.82.11 10;
sleep 5
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST start;
sleep 5
##python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST upcpu 200.137.82.21 10;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST sendjob 200.137.82.11 1;
##python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST resetcpu 200.137.82.21;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST resetlatency;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST deleteallns;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST deleteallns;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST stop;
sleep 20

echo "INICIO CENARIO 2" 
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST uplatencylink 15;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST uplatencytouser 200.137.75.159 200.137.82.11 10;
sleep 5
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST start;
sleep 5
#python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST upcpu 200.137.82.21 10;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST sendjob 200.137.82.11 1;
#python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST resetcpu;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST resetlatency;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST deleteallns;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST deleteallns;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST deleteallns;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST stop;

sleep 20
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST uplatencytouser 200.137.75.159 200.137.82.11 10;
sleep 5
echo "INICIO CENARIO 3"
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST start;
sleep 5
#python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST upcpu 200.137.82.21 10;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST sendjob 200.137.82.11 1;
#python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST resetcpu  200.137.82.21;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST resetlatency;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST deleteallns;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST deleteallns;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST stop;
sleep 20

echo "INICIO CENARIO 4" 
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST uplatencytouser 200.137.75.159 200.137.82.11 10;
sleep 5
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST start;
sleep 5
#python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST upcpu 200.137.82.21 10;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST sendjob 200.137.82.11 2;
#python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST resetcpu 200.137.82.21;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST resetlatency;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST deleteallns;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST deleteallns;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST stop;
sleep 20

echo "INICIO CENARIO 5"
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST uplatencytouser 200.137.75.159 200.137.82.11 10;
sleep 5
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST start;
sleep 5
#python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST upcpu 200.137.82.21 90;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST sendjob 200.137.82.11 2;
#python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST resetcpu 200.137.82.21;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST resetlatency;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST deleteallns;
python3 PLAO2_test_to_PLAOServer.py 127.0.0.1 POST stop;