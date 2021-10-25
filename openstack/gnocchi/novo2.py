#!/usr/bin/python3

# https://gnocchi.xyz/gnocchiclient/api.html
# https://docs.openstack.org//python-novaclient/latest/doc-python-novaclient.pdf

import json
import shade
import os
import datetime
import uuid
import sys
import time
import urllib3
import argparse
import pandas as pd

from keystoneauth1.identity import v3
from keystoneauth1 import session
from gnocchiclient.v1 import client
from gnocchiclient import auth
from novaclient import client as nclient

# Class to autenticate on OpenStack and return authentication session
class OpenStack_Auth():
    def __init__(self, cloud_name):
        self.cloud = shade.openstack_cloud(cloud=cloud_name)
        # Import credentials witch clouds.yml
        self.auth_dict = self.cloud.auth
        self.auth = v3.Password(auth_url=str(self.auth_dict['auth_url']),
                                username=str(self.auth_dict['username']),
                                password=str(self.auth_dict['password']),
                                project_name=str(
                                    self.auth_dict['project_name']),
                                user_domain_name=str(
                                    self.auth_dict['user_domain_name']),
                                project_domain_id=str(self.auth_dict['project_domain_id']))
        # Create a session with credentials clouds.yml
        self.sess = session.Session(auth=self.auth, verify=False)

    # Return authentication session
    def get_session(self):
        return self.sess


# Class to get measures from Gnocchi
class Gnocchi():
    def __init__(self, session):
        # param verify : ignore self-signed certificate
        self.gnocchi_client = client.Client(session=session)

    '''Get Metric CPU Utilization (%)
        Arguments: resource_id (Identification Virtual Machine)
                    granularity in format integer (granularity to retrieve (in seconds))
                    vcpus (number of vcpus alocated to Virtual Machine)
        Output: Return measure
    '''
    def get_metric_cpu_utilization(self, resource_id, granularity, vcpus, start, stop):
        # Divide per vcpus (OpenStack sum all processors times)
        operations = "(/ (* (/ (metric cpu rate:mean) "+str(granularity*1000000000.0)+") 100) "+str(vcpus)+")"
        # print(operations)
        meters = self.gnocchi_client.aggregates.fetch(operations,
                                                      # resource_type='generic',
                                                      search="id="+resource_id,
                                                      start=start,
                                                      stop=stop,
                                                      granularity=granularity)
        
        meters = meters['measures'][resource_id]['cpu']['rate:mean']
        df = pd.DataFrame(meters, columns =['timestamp', 'granularity', 'cpu'])
        print("\n")
        print(df.head())
        return(df)
