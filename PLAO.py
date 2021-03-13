import yaml
import sys

FILE_VNF_PRICE="C:/Temp/artigo/vnf_price_list.yaml"
FILE_PILL_PRICE="C:/Temp/artigo/XXXXXXX.yaml"
NAME_VNFD="VNFB"
URL_VNFD='http://10.159.205.12:5000/v3'
PRICE_VNFD=81

A=open(FILE_VNF_PRICE, )
B=yaml.full_load(A)

def SearchVNFD(NAME_VNFD):
#Search VNFD in configuration file vnf_price and return position
#If no result, return -1 
    C = len(B) #Elements
    for i in range(C):
        if B[i]['vnfd'] == NAME_VNFD: #Search and compare the VNFD name
            return i
    else:
        return -1

def ChangeCostVNFPrice(COD_VNFD,VIMURL,PRICE):
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

SearchVNFD(NAME_VNFD) #Search VNFD in file

if (ChangeCostVNFPrice(SearchVNFD(NAME_VNFD),URL_VNFD,PRICE_VNFD)) != -1: #Change cost of specific VIM in specific VNFD

    with open(FILE_VNF_PRICE, 'w') as file:
        documents = yaml.dump(B, file, sort_keys=False) #Export changes to file without order, equal original file
    print("File changed")

else:
    print ("File not changed")


