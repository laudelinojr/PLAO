import yaml
import sys

#requisites1 SearchChangeVNFDPrice
FILE_VNF_PRICE="C:/Temp/artigo/vnf_price_list.yaml"
NAME_VNFD="VNFB"
URL_VNFD='http://10.159.205.12:5000/v3'
PRICE_VNFD=33

#requisites SearchChangePriceLatencyJitterPILL
FILE_PILL_PRICE="C:/Temp/artigo/pill_price_list.yaml"
OPENSTACK_FROM="openstack1"
OPENSTACK_TO="openstack2"
PRICE=11
LATENCY=31
JITTER=44

def SearchVNFD(NAME_VNFD,B):
#Search VNFD in configuration file vnf_price and return position
#If no result, return -1 
    C = len(B) #Elements
    for i in range(C):
        if B[i]['vnfd'] == NAME_VNFD: #Search and compare the VNFD name
            return i
    else:
        return -1

def ChangeCostVNFPrice(COD_VNFD,VIMURL,PRICE,B):
#First, use the SearchVNFD function, after, this
#Change cost of specific VIMNAME OF VNFD
#If no result, return -1  
    C = len(B[COD_VNFD]['prices']) #Elements

    if COD_VNFD < 0:
        return -1
    
    for i in range(C):
        if B[COD_VNFD]['prices'][i]['vim_url'] == VIMURL: #Compare VIMURL between YAML and the new
            if B[COD_VNFD]['prices'][i]['price'] != PRICE:  #Compare new PRICE with actual Price, if equal, no change
                B[COD_VNFD]['prices'][i]['price']=PRICE #Change the VNF Cost
                return i
            else:
                return -1
    else:
        return -1

def SearchChangeVNFDPrice(NAME_VNFD,URL_VNFD,PRICE_VNFD):
    A=open(FILE_VNF_PRICE, )
    B=yaml.full_load(A)

    if (ChangeCostVNFPrice(SearchVNFD(NAME_VNFD,B),URL_VNFD,PRICE_VNFD,B)) != -1: #Change cost of specific VIM in specific VNFD

        with open(FILE_VNF_PRICE, 'w') as file:
            documents = yaml.dump(B, file, sort_keys=False) #Export changes to file without order, equal original file
        print("File changed")

    else:
        print ("File not changed")


def SearchChangePILLPrice(OPENSTACK_FROM,OPENSTACK_TO,B):  #Search in file the cloud math between from and to, in this order. If located, stop the search
    C = len(B['pil']) #Elements
    for i in range(C):
        if B['pil'][i]['pil_endpoints'][0] == OPENSTACK_FROM:
            if B['pil'][i]['pil_endpoints'][1] == OPENSTACK_TO:
                return i
    return -1


def ChangePriceLatencyJitterPILL(CLOUD_COD,PRICE,LATENCY,JITTER,B):
    if ((B['pil'][CLOUD_COD]['pil_price'] != PRICE) or (B['pil'][CLOUD_COD]['pil_latency'] != LATENCY) or (B['pil'][CLOUD_COD]['pil_jitter'] != JITTER)): #Change just one this values is different of the entry
        B['pil'][CLOUD_COD]['pil_price']=PRICE #change the price
        B['pil'][CLOUD_COD]['pil_latency']=LATENCY #change the latency - same price
        B['pil'][CLOUD_COD]['pil_jitter']=JITTER #change the jitter
        return 0
    else:
        return -1

def SearchChangePriceLatencyJitterPILL(PRICE,LATENCY,JITTER):

    A=open(FILE_PILL_PRICE, )
    B=yaml.full_load(A)

    CLOUD_COD=SearchChangePILLPrice(OPENSTACK_FROM,OPENSTACK_TO,B)

    if CLOUD_COD != -1:
        if (ChangePriceLatencyJitterPILL(CLOUD_COD,PRICE,LATENCY,JITTER,B)) != -1: #Change Price Latency and Jitter
            with open(FILE_PILL_PRICE, 'w') as file:
                documents = yaml.dump(B, file, sort_keys=False) #Export changes to file without order, equal original file
            print("File changed")
        else:
            print ("File not changed")
    else:
        print('The cloud math did not locate.')

SearchChangeVNFDPrice(NAME_VNFD,URL_VNFD,PRICE_VNFD)
SearchChangePriceLatencyJitterPILL(PRICE,LATENCY,JITTER)
